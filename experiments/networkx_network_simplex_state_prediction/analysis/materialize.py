#!/usr/bin/env python3
"""Build the canonical four-arm NetworkX runtime-complexity benchmark."""

from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import random
import shutil
import subprocess
import sys

import networkx as nx
from networkx.algorithms.flow import networksimplex

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "problems"
NETWORKX_VERSION = "3.4.2"
NETWORKX_COMMIT = "2acf1590f82757c01a57b81b8c5dfb79e60aa416"
UPSTREAM_SHA256 = "df6b9eb686568feffb28f3b6389a6eb4fd05a53aec43fa89c67b42f17c4856bd"
SEARCH_SIZE = 1_000
REPETITIONS = 3
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
PIVOT_LOOP = "    for i, p, q in DEAF.find_entering_edges():\n"
POST_LOOP_POINT = "    if any(DEAF.edge_flow[i] != 0 for i in range(-n, 0)):\n"

# Each tuple is topology seed, short-trace attribute index/pivots, then long-trace
# attribute index/pivots. The first ten qualifying topologies in each declared
# seed range were frozen before model evaluation.
COHORTS = (
    {
        "id": "lower",
        "nodes": 14,
        "extra_edges": 75,
        "demand": 30,
        "checkpoint": 100,
        "seed_range": (1, 30),
        "short_max": 55,
        "long_min": 110,
        "minimum_ratio": 2.0,
        "selections": (
            (1, 591, 40, 281, 115),
            (4, 37, 49, 318, 116),
            (5, 16, 43, 482, 113),
            (6, 414, 48, 243, 119),
            (8, 44, 42, 859, 112),
            (10, 337, 42, 894, 116),
            (13, 85, 42, 296, 110),
            (14, 935, 40, 501, 110),
            (16, 819, 45, 295, 117),
            (17, 771, 47, 760, 116),
        ),
    },
    {
        "id": "medium",
        "nodes": 22,
        "extra_edges": 150,
        "demand": 45,
        "checkpoint": 190,
        "seed_range": (101, 130),
        "short_max": 130,
        "long_min": 210,
        "minimum_ratio": 1.6,
        "selections": (
            (102, 472, 114, 887, 223),
            (103, 197, 116, 970, 212),
            (104, 213, 106, 763, 229),
            (105, 201, 114, 985, 227),
            (106, 643, 108, 816, 217),
            (107, 853, 113, 805, 210),
            (108, 105, 107, 298, 218),
            (109, 248, 106, 6, 211),
            (110, 608, 116, 411, 225),
            (111, 823, 109, 171, 218),
        ),
    },
    {
        "id": "higher",
        "nodes": 32,
        "extra_edges": 280,
        "demand": 65,
        "checkpoint": 360,
        "seed_range": (201, 230),
        "short_max": 270,
        "long_min": 400,
        "minimum_ratio": 1.45,
        "selections": (
            (201, 909, 244, 162, 412),
            (202, 372, 230, 476, 402),
            (204, 57, 230, 727, 416),
            (205, 633, 239, 297, 410),
            (207, 487, 245, 337, 402),
            (210, 705, 239, 424, 401),
            (211, 501, 239, 657, 401),
            (212, 204, 237, 228, 427),
            (213, 393, 246, 607, 415),
            (214, 906, 227, 668, 404),
        ),
    },
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compact(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def stripped_program() -> str:
    if nx.__version__ != NETWORKX_VERSION:
        raise RuntimeError(
            f"NetworkX {NETWORKX_VERSION} is required; found {nx.__version__}"
        )
    upstream_path = Path(networksimplex.__file__).resolve()
    upstream = upstream_path.read_text(encoding="utf-8")
    if sha256(upstream.encode()) != UPSTREAM_SHA256:
        raise RuntimeError(f"Unexpected NetworkX source: {upstream_path}")

    tree = ast.parse(upstream)
    function = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == "network_simplex"
    )
    docstring = function.body[0]
    if not (
        isinstance(docstring, ast.Expr)
        and isinstance(docstring.value, ast.Constant)
        and isinstance(docstring.value.value, str)
    ):
        raise RuntimeError("Could not locate network_simplex documentation")

    lines = upstream.splitlines(keepends=True)
    dispatch_decorator = next(
        decorator
        for decorator in function.decorator_list
        if "_dispatchable" in ast.get_source_segment(upstream, decorator)
    )
    lines[docstring.lineno - 1 : docstring.end_lineno] = [
        "    # Documentation and examples removed for benchmark evaluation.\n"
    ]
    lines[dispatch_decorator.lineno - 1 : dispatch_decorator.end_lineno] = []
    source = "".join(lines)
    signature = (
        'def network_simplex(G, demand="demand", capacity="capacity", weight="weight"):'
    )
    replacement = (
        'def benchmark_network_simplex(G, demand="demand", capacity="capacity", '
        'weight="weight"):'
    )
    if source.count(signature) != 1:
        raise RuntimeError("Could not rename network_simplex entry point")
    source = source.replace(signature, replacement, 1)
    source = source.replace(
        "import networkx as nx\n",
        "import json\n\nimport networkx as nx\n",
        1,
    )
    return source + r'''


def __load_graph(text):
    specification = json.loads(text)
    graph = nx.DiGraph()
    for node, demand in specification["nodes"]:
        graph.add_node(node, demand=demand)
    for source, target, edge_capacity, edge_weight in specification["edges"]:
        graph.add_edge(
            source,
            target,
            capacity=edge_capacity,
            weight=edge_weight,
        )
    return graph


def solve(text):
    cost, _ = benchmark_network_simplex(__load_graph(text))
    return cost


if __name__ == "__main__":
    import sys
    print(solve(sys.stdin.read()))
'''


def source_line(source: str, text: str) -> int:
    matches = [
        index
        for index, line in enumerate(source.splitlines(keepends=True), 1)
        if line == text
    ]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one source anchor for {text!r}; found {matches}")
    return matches[0]


def inside_loop_program(source: str, checkpoint: int) -> str:
    replacement = (
        "    __benchmark_pivot = 0\n"
        + PIVOT_LOOP
        + "        __benchmark_pivot += 1\n"
        + f"        if __benchmark_pivot == {checkpoint}:\n"
        + "            print(json.dumps({'node_potentials': DEAF.node_potentials}, separators=(',', ':')))\n"
        + "            raise SystemExit\n"
    )
    if source.count(PIVOT_LOOP) != 1:
        raise RuntimeError("Could not instrument the network-simplex pivot loop")
    return source.replace(PIVOT_LOOP, replacement, 1)


def post_loop_program(source: str) -> str:
    replacement = (
        "    print(json.dumps({'node_potentials': DEAF.node_potentials}, separators=(',', ':')))\n"
        "    raise SystemExit\n\n"
        + POST_LOOP_POINT
    )
    if source.count(POST_LOOP_POINT) != 1:
        raise RuntimeError("Could not instrument the post-pivot-loop point")
    return source.replace(POST_LOOP_POINT, replacement, 1)


def topology(seed: int, node_count: int, extra_edge_count: int) -> list[tuple[int, int]]:
    rng = random.Random(seed)
    edges = [(node, node + 1) for node in range(node_count - 1)]
    seen = set(edges)
    edge_count = node_count - 1 + extra_edge_count
    while len(edges) < edge_count:
        source = rng.randrange(node_count)
        target = rng.randrange(node_count)
        if source == target or (source, target) in seen:
            continue
        edges.append((source, target))
        seen.add((source, target))
    return edges


def graph_specification(
    cohort: dict[str, object], topology_seed: int, attribute_index: int
) -> dict[str, object]:
    node_count = int(cohort["nodes"])
    extra_edge_count = int(cohort["extra_edges"])
    demand_value = int(cohort["demand"])
    attribute_seed = topology_seed * 100_000 + attribute_index
    rng = random.Random(attribute_seed)
    nodes = [[f"n{node:02d}", 0] for node in range(node_count)]
    nodes[0][1] = -demand_value
    nodes[-1][1] = demand_value
    edges: list[list[object]] = []
    for index, (source, target) in enumerate(
        topology(topology_seed, node_count, extra_edge_count)
    ):
        capacity = (
            demand_value
            if index < node_count - 1
            else rng.randint(1, demand_value + 5)
        )
        weight = rng.randint(-40, 60)
        edges.append(
            [f"n{source:02d}", f"n{target:02d}", capacity, weight]
        )
    return {"nodes": nodes, "edges": edges}


def graph_from_specification(specification: dict[str, object]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for node, demand in specification["nodes"]:
        graph.add_node(node, demand=demand)
    for source, target, capacity, weight in specification["edges"]:
        graph.add_edge(source, target, capacity=capacity, weight=weight)
    return graph


def upstream_pivot_count(
    cohort: dict[str, object], topology_seed: int, attribute_index: int
) -> int:
    original = networksimplex._DataEssentialsAndFunctions.find_entering_edges
    count = 0

    def counted(instance):
        nonlocal count
        for item in original(instance):
            count += 1
            yield item

    networksimplex._DataEssentialsAndFunctions.find_entering_edges = counted
    try:
        nx.network_simplex(
            graph_from_specification(
                graph_specification(cohort, topology_seed, attribute_index)
            )
        )
    finally:
        networksimplex._DataEssentialsAndFunctions.find_entering_edges = original
    return count


def verify_selection_search() -> None:
    candidate_count = 0
    for cohort in COHORTS:
        selected: list[tuple[int, int, int, int, int]] = []
        first_seed, last_seed = cohort["seed_range"]
        for topology_seed in range(int(first_seed), int(last_seed) + 1):
            values = [
                (
                    upstream_pivot_count(cohort, topology_seed, attribute_index),
                    attribute_index,
                )
                for attribute_index in range(SEARCH_SIZE)
            ]
            candidate_count += len(values)
            short_pivots, short_attribute = min(values)
            long_pivots, long_attribute = max(values)
            if (
                short_pivots <= int(cohort["short_max"])
                and long_pivots >= int(cohort["long_min"])
                and long_pivots / short_pivots >= float(cohort["minimum_ratio"])
                and len(selected) < 10
            ):
                selected.append(
                    (
                        topology_seed,
                        short_attribute,
                        short_pivots,
                        long_attribute,
                        long_pivots,
                    )
                )
        expected = tuple(cohort["selections"])
        if tuple(selected) != expected:
            raise RuntimeError(
                f"{cohort['id']} selection changed:\n"
                f"expected={expected!r}\nactual={selected!r}"
            )
    print(f"Verified 30 selected topologies across {candidate_count} candidate graphs")


def load_module(program_path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, program_path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not import {program_path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def pivot_count(program_path: Path, input_text: str, name: str) -> tuple[int, int]:
    module = load_module(program_path, name)
    original = module._DataEssentialsAndFunctions.find_entering_edges
    count = 0

    def counted(instance):
        nonlocal count
        for item in original(instance):
            count += 1
            yield item

    module._DataEssentialsAndFunctions.find_entering_edges = counted
    cost = module.solve(input_text)
    return count, cost


def run_program(program_path: Path, input_text: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(program_path)],
        input=input_text,
        text=True,
        capture_output=True,
        check=True,
        timeout=60,
    )
    if completed.stderr:
        raise RuntimeError(f"Unexpected stderr from {program_path}: {completed.stderr}")
    return completed.stdout


def stable_program_output(program_path: Path, input_text: str, identity: str) -> str:
    observed = [run_program(program_path, input_text) for _ in range(REPETITIONS)]
    if len(set(observed)) != 1:
        raise RuntimeError(f"Unstable oracle for {identity}: {observed}")
    return observed[0]


def main() -> int:
    if "--verify-selection" in sys.argv[1:]:
        verify_selection_search()
    clean_source = stripped_program()
    post_loop_source = post_loop_program(clean_source)
    clean_source_bytes = clean_source.encode()
    post_loop_source_bytes = post_loop_source.encode()

    PROBLEMS.mkdir(parents=True, exist_ok=True)
    for generated_problem in PROBLEMS.glob("problem-*"):
        if generated_problem.is_dir():
            shutil.rmtree(generated_problem)

    cases: list[dict[str, object]] = []
    case_number = 0
    source_hashes: dict[str, str] = {
        "clean": sha256(clean_source_bytes),
        "post-loop-state": sha256(post_loop_source_bytes),
    }
    for cohort in COHORTS:
        checkpoint = int(cohort["checkpoint"])
        inside_loop_source_bytes = inside_loop_program(clean_source, checkpoint).encode()
        source_hashes[f"inside-loop-state-{cohort['id']}"] = sha256(
            inside_loop_source_bytes
        )
        for selection in cohort["selections"]:
            case_number += 1
            (
                topology_seed,
                short_attribute,
                short_pivots,
                long_attribute,
                long_pivots,
            ) = selection
            case_id = f"problem-{case_number:02d}"
            if long_pivots / short_pivots < float(cohort["minimum_ratio"]):
                raise RuntimeError(f"Trace ratio below threshold for {case_id}")
            if long_pivots < checkpoint:
                raise RuntimeError(f"Checkpoint is unreachable for {case_id}")

            short_input = compact(
                graph_specification(cohort, topology_seed, short_attribute)
            ) + "\n"
            long_input = compact(
                graph_specification(cohort, topology_seed, long_attribute)
            ) + "\n"
            input_by_arm = {
                "short-trace-final": short_input,
                "long-trace-final": long_input,
                "inside-loop-state": long_input,
                "post-loop-state": long_input,
            }
            source_by_arm = {
                "short-trace-final": clean_source_bytes,
                "long-trace-final": clean_source_bytes,
                "inside-loop-state": inside_loop_source_bytes,
                "post-loop-state": post_loop_source_bytes,
            }
            source_variant_by_arm = {
                "short-trace-final": "clean",
                "long-trace-final": "clean",
                "inside-loop-state": "inside-loop-state",
                "post-loop-state": "post-loop-state",
            }

            case_record: dict[str, object] = {
                "case_id": case_id,
                "cohort": cohort["id"],
                "topology_seed": topology_seed,
                "nodes": cohort["nodes"],
                "edges": int(cohort["nodes"]) - 1 + int(cohort["extra_edges"]),
                "demand": cohort["demand"],
                "inside_loop_checkpoint": checkpoint,
                "search_attribute_indices": [0, SEARCH_SIZE - 1],
                "short_attribute_index": short_attribute,
                "long_attribute_index": long_attribute,
                "short_pivots": short_pivots,
                "long_pivots": long_pivots,
                "pivot_ratio": long_pivots / short_pivots,
                "arms": {},
            }
            for arm in ARMS:
                arm_root = PROBLEMS / case_id / arm
                arm_root.mkdir(parents=True)
                (arm_root / "program.py").write_bytes(source_by_arm[arm])
                (arm_root / "input.txt").write_text(
                    input_by_arm[arm], encoding="utf-8"
                )

            short_program = PROBLEMS / case_id / "short-trace-final" / "program.py"
            long_program = PROBLEMS / case_id / "long-trace-final" / "program.py"
            observed_short_pivots, short_cost = pivot_count(
                short_program, short_input, f"networkx_{case_number}_short"
            )
            observed_long_pivots, long_cost = pivot_count(
                long_program, long_input, f"networkx_{case_number}_long"
            )
            if observed_short_pivots != short_pivots:
                raise RuntimeError(
                    f"{case_id}/short-trace-final: expected {short_pivots} pivots, "
                    f"got {observed_short_pivots}"
                )
            if observed_long_pivots != long_pivots:
                raise RuntimeError(
                    f"{case_id}/long-trace-final: expected {long_pivots} pivots, "
                    f"got {observed_long_pivots}"
                )

            oracle_by_arm = {
                "short-trace-final": f"{short_cost}\n",
                "long-trace-final": f"{long_cost}\n",
                "inside-loop-state": stable_program_output(
                    PROBLEMS / case_id / "inside-loop-state" / "program.py",
                    long_input,
                    f"{case_id}/inside-loop-state",
                ),
                "post-loop-state": stable_program_output(
                    PROBLEMS / case_id / "post-loop-state" / "program.py",
                    long_input,
                    f"{case_id}/post-loop-state",
                ),
            }
            inside_state = json.loads(oracle_by_arm["inside-loop-state"])
            post_state = json.loads(oracle_by_arm["post-loop-state"])
            if list(inside_state) != list(post_state):
                raise RuntimeError(f"State projection fields differ for {case_id}")
            if inside_state == post_state:
                raise RuntimeError(f"State projection did not change for {case_id}")

            for arm in ARMS:
                arm_root = PROBLEMS / case_id / arm
                oracle = oracle_by_arm[arm]
                observed = stable_program_output(
                    arm_root / "program.py",
                    input_by_arm[arm],
                    f"{case_id}/{arm}",
                )
                if observed != oracle:
                    raise RuntimeError(
                        f"Oracle mismatch for {case_id}/{arm}: "
                        f"{observed!r} != {oracle!r}"
                    )
                (arm_root / "ground-output.txt").write_text(
                    oracle, encoding="utf-8"
                )
                attribute_index = (
                    short_attribute if arm == "short-trace-final" else long_attribute
                )
                pivots = short_pivots if arm == "short-trace-final" else long_pivots
                if arm == "inside-loop-state":
                    pivots = checkpoint
                case_record["arms"][arm] = {
                    "attribute_index": attribute_index,
                    "attribute_seed": topology_seed * 100_000 + attribute_index,
                    "input_variant": "short-trace-final" if arm == "short-trace-final" else "long-trace-final",
                    "source_variant": source_variant_by_arm[arm],
                    "source_sha256": sha256(source_by_arm[arm]),
                    "pivots": pivots,
                    "target": {
                        "short-trace-final": "final minimum cost",
                        "long-trace-final": "final minimum cost",
                        "inside-loop-state": f"node_potentials at pivot-loop body execution {checkpoint}",
                        "post-loop-state": "node_potentials immediately after the pivot loop",
                    }[arm],
                    "input_bytes": len(input_by_arm[arm].encode()),
                    "input_sha256": sha256(input_by_arm[arm].encode()),
                    "oracle_sha256": sha256(oracle.encode()),
                }
            case_record["state_projection"] = {
                "fields": ["node_potentials"],
                "field_types": ["array[integer]"],
                "serialization": "canonical compact JSON",
                "changed": True,
            }
            cases.append(case_record)

    manifest = {
        "schema_version": 2,
        "networkx_version": NETWORKX_VERSION,
        "networkx_commit": NETWORKX_COMMIT,
        "networkx_upstream_sha256": UPSTREAM_SHA256,
        "model_visible_source_sha256": source_hashes,
        "arms": list(ARMS),
        "selection": {
            "fixed_before_model_evaluation": True,
            "candidate_graphs": 90_000,
            "cohorts": [
                {
                    "id": cohort["id"],
                    "problems": 10,
                    "nodes": cohort["nodes"],
                    "edges": int(cohort["nodes"]) - 1 + int(cohort["extra_edges"]),
                    "demand": cohort["demand"],
                    "inside_loop_checkpoint": cohort["checkpoint"],
                    "topology_seed_range": list(cohort["seed_range"]),
                    "short_pivot_max": cohort["short_max"],
                    "long_pivot_min": cohort["long_min"],
                    "minimum_pair_ratio": cohort["minimum_ratio"],
                }
                for cohort in COHORTS
            ],
            "attribute_generator": (
                "backbone capacity equals cohort demand; other capacities are "
                "uniform integers 1..demand+5; "
                "all weights uniform integer -40..60"
            ),
            "attribute_indices_per_topology": SEARCH_SIZE,
            "input_rule": (
                "short-trace-final uses the minimum-pivot candidate and every other arm "
                "uses the maximum-pivot candidate for the selected topology"
            ),
            "problem_rule": (
                "first 10 topology seeds in each disjoint declared range meeting "
                "that cohort's short-trace maximum, long-trace minimum, and ratio threshold"
            ),
        },
        "oracle_repetitions": REPETITIONS,
        "cases": cases,
    }
    (ROOT / "cases.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        f"Built {len(cases)} problems, {len(cases) * len(ARMS)} canonical-arm tasks"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
