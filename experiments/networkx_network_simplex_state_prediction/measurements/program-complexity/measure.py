#!/usr/bin/env python3
"""Measure dynamic complexity for the matched NetworkX executions."""

from __future__ import annotations

import ast
import csv
from contextlib import redirect_stdout
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import sysconfig
import tempfile
import types
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import networkx as nx

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[2]
REPOSITORY = Path(__file__).resolve().parents[4]
PROBLEMS = ROOT / "problems"
OUTPUT = Path(__file__).resolve().parent
CASE_MANIFEST = json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))
CASE_COHORT = {
    str(case["case_id"]): str(case["cohort"])
    for case in CASE_MANIFEST["cases"]
}
REPETITIONS = 3
TRACE_TIMEOUT_SECONDS = int(os.environ.get("COMPLEXITY_TRACE_TIMEOUT_SECONDS", "600"))
CACHE_ROOT = Path(
    os.environ.get(
        "COMPLEXITY_CACHE_DIR",
        str(Path(tempfile.gettempdir()) / "networkx-complexity-state-load-v1"),
    )
)
CONVENTION = "python-cpython-opcode-v1"
STATE_CONVENTION = "python-cpython-line-state-size-v1"
STATE_LOAD_CONVENTION = "python-cpython-line-state-load-v1"
STATE_CELLS_SOURCE = Path(__file__).resolve().with_name("state_cells.c")
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
STATIC_METRICS = (
    "Omega_CC",
)
OUTPUT_FIELDS = (
    "case_id",
    "cohort",
    "arm_id",
    "measurement_source_arm",
    "execution_id",
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
    "Omega_CC",
    "state_size_status",
    "native_trace_event",
    "state_size_observation",
    "state_load_observation",
    "state_observation_count",
    "source_sha256",
    "input_sha256",
    "oracle_sha256",
    "native_trace_repetitions",
    "state_size_repetitions",
    "raw_native_trace_measurements",
    "raw_state_size_measurements",
    "raw_state_load_measurements",
    "raw_state_observation_counts",
)
PYTHON_COMPLEXITY_PATH = (
    REPOSITORY / "shared/metrics/scripts/python_complexity.py"
)
PYTHON_COMPLEXITY_SPEC = importlib.util.spec_from_file_location(
    "shared_python_complexity", PYTHON_COMPLEXITY_PATH
)
if PYTHON_COMPLEXITY_SPEC is None or PYTHON_COMPLEXITY_SPEC.loader is None:
    raise RuntimeError(f"Could not load {PYTHON_COMPLEXITY_PATH}")
PYTHON_COMPLEXITY = importlib.util.module_from_spec(PYTHON_COMPLEXITY_SPEC)
sys.modules[PYTHON_COMPLEXITY_SPEC.name] = PYTHON_COMPLEXITY
PYTHON_COMPLEXITY_SPEC.loader.exec_module(PYTHON_COMPLEXITY)
measure_python_static = PYTHON_COMPLEXITY.measure_python_static


EXCLUDED_RUNTIME_TYPES = (
    types.ModuleType,
    types.FunctionType,
    types.BuiltinFunctionType,
    types.MethodType,
    type,
)


def load_compiled_state_counter():
    """Build and load the exact cell counter used inside the line tracer."""
    if os.environ.get("COMPLEXITY_STATE_COUNTER", "compiled") == "python":
        return None
    source_bytes = STATE_CELLS_SOURCE.read_bytes()
    build_root = CACHE_ROOT / "compiled-state-counter"
    build_root.mkdir(parents=True, exist_ok=True)
    suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    source_digest = hashlib.sha256(source_bytes).hexdigest()
    library = build_root / f"_networkx_state_cells-{source_digest[:16]}{suffix}"
    if not library.exists():
        linker = sysconfig.get_config_var("LDSHARED")
        include = sysconfig.get_paths()["include"]
        if not linker or not include:
            raise RuntimeError("CPython compiler configuration is incomplete")
        temporary = library.with_suffix(library.suffix + ".tmp")
        completed = subprocess.run(
            [
                *shlex.split(str(linker)),
                "-O3",
                f"-I{include}",
                str(STATE_CELLS_SOURCE),
                "-o",
                str(temporary),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                "Could not compile StateSize cell counter: "
                f"{completed.stderr.strip() or completed.stdout.strip()}"
            )
        os.replace(temporary, library)
    specification = importlib.util.spec_from_file_location(
        "_networkx_state_cells", library
    )
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not load compiled StateSize counter: {library}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module.count


COMPILED_STATE_COUNT = load_compiled_state_counter()


def load_baseline_native_rows() -> dict[tuple[str, str], dict[str, str]]:
    """Retain exact final-arm NativeTrace evidence during StateSize refreshes."""
    measurements = OUTPUT / "measurements.csv"
    if not measurements.exists():
        return {}
    arm_names = {
        "short-trace-final": "short-trace-final",
        "long-trace-final": "long-trace-final",
    }
    result = {}
    with measurements.open(newline="", encoding="utf-8") as handle:
        for source in csv.DictReader(handle):
            arm = arm_names.get(source["arm_id"])
            if arm is None:
                continue
            row = dict(source)
            row["arm_id"] = arm
            row["measurement_source_arm"] = arm
            result[(row["case_id"], arm)] = row
    return result


BASELINE_NATIVE_ROWS = load_baseline_native_rows()


def normalize_measurement_row(row: dict[str, object]) -> dict[str, object]:
    """Normalize legacy cache rows and preserve authoritative NativeTrace repeats."""
    normalized = dict(row)
    legacy_raw = normalized.pop("raw_measurements", None)
    legacy_repetitions = normalized.pop("repetitions", None)
    if legacy_raw is not None:
        observations = json.loads(str(legacy_raw))
        normalized["raw_native_trace_measurements"] = json.dumps(
            [int(item["Omega_hat_NativeTrace"]) for item in observations],
            separators=(",", ":"),
        )
        normalized["raw_state_size_measurements"] = json.dumps(
            [int(item["Omega_hat_StateSize"]) for item in observations],
            separators=(",", ":"),
        )
        normalized["native_trace_repetitions"] = int(legacy_repetitions)
        normalized["state_size_repetitions"] = int(legacy_repetitions)
    normalized["state_size_status"] = "OK"
    normalized.setdefault("state_load_observation", normalized["state_size_observation"])

    baseline = BASELINE_NATIVE_ROWS.get(
        (str(normalized["case_id"]), str(normalized["arm_id"]))
    )
    if baseline is not None:
        for identity_field in ("source_sha256", "input_sha256", "oracle_sha256"):
            if str(normalized[identity_field]) != baseline[identity_field]:
                raise RuntimeError(
                    f"NativeTrace baseline identity mismatch for "
                    f"{normalized['case_id']}/{normalized['arm_id']}: {identity_field}"
                )
        if (
            str(normalized["execution_id"]) != baseline["execution_id"]
            and baseline["state_size_status"] != "NOT_MEASURED_RESOURCE_LIMIT"
        ):
            raise RuntimeError(
                f"Execution identity mismatch for completed baseline "
                f"{normalized['case_id']}/{normalized['arm_id']}"
            )
        native_value = int(baseline["Omega_hat_NativeTrace"])
        if int(normalized["Omega_hat_NativeTrace"]) != native_value:
            raise RuntimeError(
                f"NativeTrace mismatch for {normalized['case_id']}/"
                f"{normalized['arm_id']}"
            )
        normalized["Omega_hat_NativeTrace"] = native_value
        normalized["native_trace_repetitions"] = int(
            baseline["native_trace_repetitions"]
        )
        normalized["raw_native_trace_measurements"] = baseline[
            "raw_native_trace_measurements"
        ]

    return {field: normalized[field] for field in OUTPUT_FIELDS}


def reachable_value_cells(roots: list[object]) -> int:
    """Count semantic value cells reachable from roots under the Python adapter."""
    if COMPILED_STATE_COUNT is not None:
        return int(COMPILED_STATE_COUNT(roots))
    seen_compounds: set[int] = set()

    def visit(value: object) -> int:
        if isinstance(value, EXCLUDED_RUNTIME_TYPES):
            return 0
        if value is None or isinstance(value, (bool, int, float, complex)):
            return 1
        if isinstance(value, (str, bytes, bytearray, memoryview)):
            return 1 + len(value)
        if isinstance(value, range):
            return 1

        identity = id(value)
        if identity in seen_compounds:
            return 0
        seen_compounds.add(identity)

        if isinstance(value, dict):
            return 1 + sum(visit(key) + visit(item) for key, item in value.items())
        if isinstance(value, (list, tuple, set, frozenset, deque)):
            return 1 + sum(visit(item) for item in value)

        try:
            attributes = object.__getattribute__(value, "__dict__")
        except (AttributeError, TypeError):
            attributes = None
        if isinstance(attributes, dict):
            return 1 + sum(
                visit(item)
                for name, item in attributes.items()
                if not name.startswith("__")
            )
        # Opaque iterators, generators, and extension objects are one reachable
        # value cell. Their interpreter-owned internals are deliberately not
        # traversed.
        return 1

    return sum(visit(root) for root in roots)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_module(program_path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, program_path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not import {program_path}")
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    return module


def run_untraced(program_path: Path, input_text: str) -> str:
    completed = subprocess.run(
        [sys.executable, str(program_path)],
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
        timeout=300,
    )
    if completed.stderr:
        raise RuntimeError(f"Unexpected stderr from {program_path}: {completed.stderr}")
    return completed.stdout


def prime_opcode_tracing() -> None:
    """Activate CPython's opcode tracing before measuring target frames."""
    count = 0

    def target() -> int:
        value = 1
        return value

    target_code = target.__code__

    def tracer(frame, event, argument):
        del argument
        nonlocal count
        if frame.f_code is not target_code:
            return None
        if event == "call":
            frame.f_trace_opcodes = True
            return tracer
        if event == "opcode":
            count += 1
        return tracer

    for _ in range(2):
        sys.settrace(tracer)
        try:
            target()
        finally:
            sys.settrace(None)
        if count:
            break
    if count == 0:
        raise RuntimeError("Could not activate CPython opcode tracing")


def position(node: ast.AST, end: bool = False) -> tuple[int, int]:
    line_name = "end_lineno" if end else "lineno"
    column_name = "end_col_offset" if end else "col_offset"
    line = getattr(node, line_name, None)
    column = getattr(node, column_name, None)
    if not isinstance(line, int) or not isinstance(column, int):
        raise RuntimeError(f"AST node has no complete source position: {node!r}")
    return line, column


def body_region(body: list[ast.stmt]) -> tuple[tuple[int, int], tuple[int, int]] | None:
    if not body:
        return None
    return position(body[0]), position(body[-1], end=True)


def control_regions(program_path: Path) -> tuple[
    list[tuple[tuple[int, int], tuple[int, int], int]],
    list[tuple[tuple[int, int], tuple[int, int], int]],
]:
    """Return lexical regions entered at each conditional and loop depth."""
    tree = ast.parse(program_path.read_text(encoding="utf-8"))
    if_regions: list[tuple[tuple[int, int], tuple[int, int], int]] = []
    loop_regions: list[tuple[tuple[int, int], tuple[int, int], int]] = []

    def add_region(regions, nodes, depth):
        region = body_region(nodes)
        if region is not None:
            regions.append((region[0], region[1], depth))

    def visit(node: ast.AST, if_depth: int, loop_depth: int) -> None:
        if isinstance(node, ast.If):
            add_region(if_regions, node.body, if_depth + 1)
            for child in node.body:
                visit(child, if_depth + 1, loop_depth)
            if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
                visit(node.orelse[0], if_depth, loop_depth)
            else:
                add_region(if_regions, node.orelse, if_depth + 1)
                for child in node.orelse:
                    visit(child, if_depth + 1, loop_depth)
            visit(node.test, if_depth, loop_depth)
            return
        if isinstance(node, (ast.For, ast.AsyncFor, ast.While)):
            add_region(loop_regions, node.body, loop_depth + 1)
            for child in node.body:
                visit(child, if_depth, loop_depth + 1)
            for child in node.orelse:
                visit(child, if_depth, loop_depth)
            for field in ("target", "iter", "test"):
                child = getattr(node, field, None)
                if isinstance(child, ast.AST):
                    visit(child, if_depth, loop_depth)
            return
        if isinstance(node, ast.IfExp):
            for branch in (node.body, node.orelse):
                if_regions.append((position(branch), position(branch, end=True), if_depth + 1))
                visit(branch, if_depth + 1, loop_depth)
            visit(node.test, if_depth, loop_depth)
            return
        if isinstance(node, ast.comprehension):
            # The element and later generators are compiled in a nested frame;
            # their source positions still fall within this generator region.
            for child in ast.iter_child_nodes(node):
                visit(child, if_depth, loop_depth + 1)
            return
        for child in ast.iter_child_nodes(node):
            visit(child, if_depth, loop_depth)

    visit(tree, 0, 0)
    return if_regions, loop_regions


def contains(
    region: tuple[tuple[int, int], tuple[int, int], int],
    point: tuple[int, int],
) -> bool:
    start, end, _ = region
    return start <= point <= end


def measure_trace_in_process(
    program_path: Path,
    input_text: str,
    name: str,
    *,
    collect_native_trace: bool = True,
    collect_state_size: bool = True,
) -> tuple[dict[str, int], str]:
    module = load_module(program_path, name)
    included = str(program_path.resolve())
    metrics = {
        "Omega_hat_NativeTrace": 0,
        "Omega_hat_StateSize": 0,
        "Omega_hat_StateLoad": 0,
        "state_observation_count": 0,
    }
    active_frames: dict[int, object] = {}

    def observe_state() -> None:
        roots: list[object] = []
        for active in active_frames.values():
            roots.extend(
                value
                for variable, value in active.f_locals.items()
                if not variable.startswith("__")
            )
        roots.extend(
            value
            for variable, value in module.__dict__.items()
            if not variable.startswith("__")
        )
        current_state_size = reachable_value_cells(roots)
        metrics["Omega_hat_StateSize"] = max(
            metrics["Omega_hat_StateSize"], current_state_size
        )
        metrics["Omega_hat_StateLoad"] += current_state_size
        metrics["state_observation_count"] += 1

    def tracer(frame, event, argument):
        del argument
        if frame.f_code.co_filename != included:
            return None
        if event == "call":
            active_frames[id(frame)] = frame
            frame.f_trace_opcodes = collect_native_trace
            if collect_state_size:
                observe_state()
            return tracer
        if event == "line":
            if collect_state_size:
                observe_state()
            return tracer
        if event == "opcode" and collect_native_trace:
            metrics["Omega_hat_NativeTrace"] += 1
            return tracer
        if event == "return":
            if collect_state_size:
                observe_state()
            active_frames.pop(id(frame), None)
        return tracer

    output = StringIO()
    result = None
    sys.settrace(tracer)
    try:
        with redirect_stdout(output):
            try:
                result = module.solve(input_text)
            except SystemExit:
                pass
    finally:
        sys.settrace(None)
    visible_output = output.getvalue()
    if not visible_output:
        visible_output = f"{result}\n"
    return metrics, visible_output


def measure_trace_fresh_process(
    program_path: Path,
    input_path: Path,
    name: str,
    *,
    collect_native_trace: bool = True,
    collect_state_size: bool = True,
) -> tuple[dict[str, int], str]:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    completed = subprocess.run(
        [
            sys.executable,
            str(Path(__file__).resolve()),
            (
                "--trace-one"
                if collect_native_trace and collect_state_size
                else "--native-one"
                if collect_native_trace
                else "--state-one"
            ),
            str(program_path),
            str(input_path),
            name,
        ],
        text=True,
        capture_output=True,
        check=True,
        timeout=TRACE_TIMEOUT_SECONDS,
        env=environment,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"Trace subprocess failed for {program_path} (exit {completed.returncode}): "
            f"{completed.stderr.strip() or '<no stderr>'}"
        )
    payload = json.loads(completed.stdout)
    return {name: int(value) for name, value in payload["metrics"].items()}, str(payload["output"])


def compact_counts_payload(metrics: dict[str, int], output: str) -> str:
    return json.dumps(
        {"metrics": metrics, "output": output},
        separators=(",", ":"),
        sort_keys=True,
    )


def measure_execution(program_path: Path) -> dict[str, object]:
    """Measure one non-prompt arm in isolated, repeatable subprocesses."""
    arm_root = program_path.parent
    case_id = arm_root.parent.name
    arm_id = arm_root.name
    input_bytes = (arm_root / "input.txt").read_bytes()
    source_bytes = program_path.read_bytes()
    execution_id = sha256(
        source_bytes
        + b"\0"
        + input_bytes
        + b"\0"
        + CONVENTION.encode()
        + b"\0"
        + STATE_CONVENTION.encode()
    )
    baseline = BASELINE_NATIVE_ROWS.get((case_id, arm_id))
    current_hashes = {
        "source_sha256": sha256(source_bytes),
        "input_sha256": sha256(input_bytes),
        "oracle_sha256": sha256((arm_root / "ground-output.txt").read_bytes()),
    }
    if baseline is not None and all(
        baseline[field] == value for field, value in current_hashes.items()
    ):
        if baseline["execution_id"] != execution_id:
            raise RuntimeError(f"Retained execution identity mismatch: {case_id}/{arm_id}")
        print(f"Retained {case_id}/{arm_id}", flush=True)
        return {field: baseline[field] for field in OUTPUT_FIELDS}
    cache_path = CACHE_ROOT / f"{case_id}-{arm_id}-{execution_id}-r{REPETITIONS}.json"
    if cache_path.exists():
        row = normalize_measurement_row(
            json.loads(cache_path.read_text(encoding="utf-8"))
        )
        if row.get("execution_id") != execution_id:
            raise RuntimeError(f"Invalid measurement cache entry: {cache_path}")
        print(f"Reused {case_id}/{arm_id}", flush=True)
        return row
    input_text = input_bytes.decode("utf-8")
    oracle = (arm_root / "ground-output.txt").read_text(encoding="utf-8")
    if run_untraced(program_path, input_text) != oracle:
        raise RuntimeError(f"Untraced oracle mismatch: {case_id}/{arm_id}")

    repetitions: list[dict[str, int]] = []
    for repetition in range(REPETITIONS):
        baseline = BASELINE_NATIVE_ROWS.get((case_id, arm_id))
        if baseline is None:
            native_measured, native_output = measure_trace_fresh_process(
                program_path,
                arm_root / "input.txt",
                f"native_{case_id}_{arm_id}_{repetition}".replace("-", "_"),
                collect_state_size=False,
            )
        else:
            native_measured = {
                "Omega_hat_NativeTrace": int(baseline["Omega_hat_NativeTrace"])
            }
            native_output = oracle
        state_measured, state_output = measure_trace_fresh_process(
            program_path,
            arm_root / "input.txt",
            f"state_{case_id}_{arm_id}_{repetition}".replace("-", "_"),
            collect_native_trace=False,
        )
        if native_output != oracle:
            raise RuntimeError(f"Native-traced oracle mismatch: {case_id}/{arm_id}")
        if state_output != oracle:
            raise RuntimeError(f"State-traced oracle mismatch: {case_id}/{arm_id}")
        repetitions.append(
            {
                "Omega_hat_NativeTrace": native_measured["Omega_hat_NativeTrace"],
                "Omega_hat_StateSize": state_measured["Omega_hat_StateSize"],
                "Omega_hat_StateLoad": state_measured["Omega_hat_StateLoad"],
                "state_observation_count": state_measured["state_observation_count"],
            }
        )
    if any(measured != repetitions[0] for measured in repetitions[1:]):
        raise RuntimeError(
            f"Unstable dynamic measurements: {case_id}/{arm_id}: {repetitions}"
        )

    measured_static = measure_python_static(program_path.read_text(encoding="utf-8"))
    row = normalize_measurement_row({
        "case_id": case_id,
        "cohort": CASE_COHORT[case_id],
        "arm_id": arm_id,
        "measurement_source_arm": arm_id,
        "execution_id": execution_id,
        **repetitions[0],
        "Omega_CC": measured_static["Omega_CC"],
        "state_size_status": "OK",
        "native_trace_event": "CPython 3.12 opcode event in program.py frames",
        "state_size_observation": "CPython call, line, and return events in program.py frames",
        "state_load_observation": "sum of reachable value cells over the same CPython call, line, and return observations as StateSize",
        "state_observation_count": repetitions[0]["state_observation_count"],
        "source_sha256": sha256(source_bytes),
        "input_sha256": sha256(input_bytes),
        "oracle_sha256": sha256(oracle.encode()),
        "native_trace_repetitions": REPETITIONS,
        "state_size_repetitions": REPETITIONS,
        "raw_native_trace_measurements": json.dumps(
            [row["Omega_hat_NativeTrace"] for row in repetitions],
            separators=(",", ":"),
        ),
        "raw_state_size_measurements": json.dumps(
            [row["Omega_hat_StateSize"] for row in repetitions],
            separators=(",", ":"),
        ),
        "raw_state_load_measurements": json.dumps(
            [row["Omega_hat_StateLoad"] for row in repetitions],
            separators=(",", ":"),
        ),
        "raw_state_observation_counts": json.dumps(
            [row["state_observation_count"] for row in repetitions],
            separators=(",", ":"),
        ),
    })
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    temporary_cache = cache_path.with_suffix(".tmp")
    temporary_cache.write_text(
        json.dumps(row, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary_cache, cache_path)
    print(f"Measured {case_id}/{arm_id}", flush=True)
    return row


def parallel_main() -> int:
    if nx.__version__ != "3.4.2":
        raise RuntimeError(f"NetworkX 3.4.2 is required; found {nx.__version__}")
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(
            f"CPython 3.12 is required; found {sys.version_info.major}.{sys.version_info.minor}"
        )

    program_paths = sorted(PROBLEMS.glob("*/**/program.py"))
    workers = max(1, int(os.environ.get("COMPLEXITY_WORKERS", "1")))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(measure_execution, program_paths))
    arm_order = {arm: index for index, arm in enumerate(ARMS)}
    rows.sort(key=lambda row: (str(row["case_id"]), arm_order[str(row["arm_id"])]))
    with (OUTPUT / "measurements.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    native_trace_repetitions = sorted(
        {int(row["native_trace_repetitions"]) for row in rows}
    )
    state_size_repetitions = sorted(
        {int(row["state_size_repetitions"]) for row in rows}
    )
    manifest = {
        "schema_version": 2,
        "metrics": {
            "Omega_CC": "source control-flow path count (cyclomatic complexity)",
            "Omega_hat_NativeTrace": "CPython opcode events executed in program.py frames",
            "Omega_hat_StateSize": "maximum reachable runtime value cells at CPython call, line, and return observation events in program.py frames",
            "Omega_hat_StateLoad": "sum of reachable runtime value cells over every CPython call, line, and return observation in program.py frames",
        },
        "conventions": {
            "native_trace": CONVENTION,
            "state_size": STATE_CONVENTION,
            "state_load": STATE_LOAD_CONVENTION,
        },
        "state_size_counter": {
            "implementation": "compiled CPython extension",
            "source": STATE_CELLS_SOURCE.name,
            "source_sha256": sha256(STATE_CELLS_SOURCE.read_bytes()),
            "fallback": "pure Python with COMPLEXITY_STATE_COUNTER=python",
        },
        "python": sys.version,
        "networkx": nx.__version__,
        "included_files": ["program.py"],
        "excluded": [
            "CPython internals",
            "NetworkX library frames",
            "standard-library frames",
            "measurement code and tracer state",
            "module, function, class, and interpreter-owned object internals",
        ],
        "state_size_rules": {
            "scalar": 1,
            "string_or_bytes": "one container cell plus one cell per element",
            "materialized_container": "one container cell plus recursively reachable keys, values, or elements",
            "object": "one object cell plus inspectable instance fields",
            "sharing": "compound objects counted once per observation; primitive occurrences counted separately",
            "opaque_iterator_or_extension": "one reachable cell; interpreter-owned internals excluded",
        },
        "state_load_rules": {
            "aggregation": "sum of the StateSize value at every complete state observation",
            "observation_series": "identical to Omega_hat_StateSize",
            "unit": "runtime value-cell observations",
        },
        "native_trace_repetitions": native_trace_repetitions,
        "state_size_repetitions": state_size_repetitions,
        "profiles": len(rows),
        "executions": len({str(row["execution_id"]) for row in rows}),
        "arms": list(ARMS),
        "output_sha256": sha256((OUTPUT / "measurements.csv").read_bytes()),
    }
    (OUTPUT / "measurement-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        f"Measured {len(rows)} arm profiles across "
        f"{len({str(row['execution_id']) for row in rows})} unique executions"
    )
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[1] in {
        "--trace-one",
        "--native-one",
        "--state-one",
    }:
        collect_native_trace = sys.argv[1] in {"--trace-one", "--native-one"}
        collect_state_size = sys.argv[1] in {"--trace-one", "--state-one"}
        if collect_native_trace:
            prime_opcode_tracing()
        trace_metrics, trace_output = measure_trace_in_process(
            Path(sys.argv[2]).resolve(),
            Path(sys.argv[3]).read_text(encoding="utf-8"),
            sys.argv[4],
            collect_native_trace=collect_native_trace,
            collect_state_size=collect_state_size,
        )
        print(compact_counts_payload(trace_metrics, trace_output))
        raise SystemExit(0)
    raise SystemExit(parallel_main())
