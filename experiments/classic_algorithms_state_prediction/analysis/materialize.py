#!/usr/bin/env python3

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

from .specs import AlgorithmSpec, SPECS


ROOT = Path(__file__).resolve().parents[1]
PROBLEMS = ROOT / "problems"
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
REPETITIONS = 3


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def add_json_import(source: str) -> str:
    if "import json\n" in source:
        return source
    return "import json\n\n" + source


def line_number(source: str, target: str) -> int:
    if source.count(target) != 1:
        raise RuntimeError(f"Expected one source target, found {source.count(target)}")
    return source[: source.index(target)].count("\n") + 1


def ordinal(value: int) -> str:
    if 10 <= value % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(value % 10, "th")
    return f"{value}{suffix}"


def with_counter(source: str) -> str:
    marker = "def main():\n"
    if source.count(marker) != 1:
        raise RuntimeError("Expected one main function")
    return source.replace(marker, marker + "    __target_count = 0\n", 1)


def hook(source: str, anchor: str, statements: list[str]) -> str:
    indentation = anchor[: len(anchor) - len(anchor.lstrip())]
    injected = "".join(indentation + statement + "\n" for statement in statements)
    if source.count(anchor) != 1:
        raise RuntimeError("Expected one checkpoint anchor")
    return source.replace(anchor, injected + anchor, 1)


def count_program(specification: AlgorithmSpec) -> str:
    source = with_counter(specification.source)
    source = hook(source, specification.anchor, ["__target_count += 1"])
    return source.replace(specification.out_anchor, "    print(__target_count)\n", 1)


def state_projection_expressions(
    specification: AlgorithmSpec,
) -> tuple[str, str, tuple[str, ...]]:
    inside = ast.parse(specification.in_state, mode="eval").body
    post = ast.parse(specification.out_state, mode="eval").body
    if not isinstance(inside, ast.Dict) or not isinstance(post, ast.Dict):
        raise RuntimeError("State projections must be dictionary expressions")

    def fields(expression: ast.Dict) -> dict[str, ast.expr]:
        result = {}
        for key, value in zip(expression.keys, expression.values, strict=True):
            if not isinstance(key, ast.Constant) or not isinstance(key.value, str):
                raise RuntimeError("State projection keys must be strings")
            result[key.value] = value
        return result

    inside_fields = fields(inside)
    post_fields = fields(post)
    shared = tuple(sorted(set(inside_fields) & set(post_fields)))
    if not shared:
        raise RuntimeError(f"{specification.case_id}: no shared state fields")

    def render(values: dict[str, ast.expr]) -> str:
        return "{" + ", ".join(
            f"{field!r}: {ast.unparse(values[field])}" for field in shared
        ) + "}"

    return render(inside_fields), render(post_fields), shared


def inside_loop_program(
    specification: AlgorithmSpec, checkpoint: int, state_expression: str
) -> str:
    source = add_json_import(with_counter(specification.source))
    return hook(
        source,
        specification.anchor,
        [
            "__target_count += 1",
            f"if __target_count == {checkpoint}:",
            f"    print(json.dumps({state_expression}, separators=(\",\", \":\"), sort_keys=True))",
            "    return",
        ],
    )


def post_loop_program(specification: AlgorithmSpec, state_expression: str) -> str:
    source = add_json_import(specification.source)
    replacement = f"    print(json.dumps({state_expression}, separators=(\",\", \":\"), sort_keys=True))\n"
    if source.count(specification.out_anchor) != 1:
        raise RuntimeError("Expected one post-loop anchor")
    return source.replace(specification.out_anchor, replacement, 1)


def run_program(source: str, input_text: str) -> bytes:
    with tempfile.TemporaryDirectory(prefix="classic-algorithm-") as directory:
        path = Path(directory) / "program.py"
        path.write_text(source, encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(path)],
            input=input_text.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=20,
        )
    if process.returncode != 0:
        raise RuntimeError(process.stderr.decode(errors="replace"))
    return process.stdout


def repeat(source: str, input_text: str) -> bytes:
    outputs = [run_program(source, input_text) for _ in range(REPETITIONS)]
    if len(set(outputs)) != 1:
        raise RuntimeError("Repeated executions produced different output")
    return outputs[0]


def count(specification: AlgorithmSpec, input_text: str) -> int:
    output = repeat(count_program(specification), input_text)
    return int(output.decode().strip())


def write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        data = data.encode()
    path.write_bytes(data)


def arm_metadata(source: str, input_text: str, oracle: bytes, **extra: object) -> dict[str, object]:
    result: dict[str, object] = {
        "source_sha256": sha256(source.encode()),
        "input_sha256": sha256(input_text.encode()),
        "oracle_sha256": sha256(oracle),
        "oracle_bytes": len(oracle),
    }
    result.update(extra)
    return result


def materialize_case(specification: AlgorithmSpec) -> dict[str, object]:
    short_count = count(specification, specification.short_input)
    long_count = count(specification, specification.long_input)
    if short_count < 1 or long_count <= short_count:
        raise RuntimeError(
            f"{specification.case_id}: long count {long_count} does not exceed short count {short_count}"
        )
    inside_expression, post_expression, fields = state_projection_expressions(
        specification
    )
    post_source = post_loop_program(specification, post_expression)
    short_oracle = repeat(specification.source, specification.short_input)
    long_oracle = repeat(specification.source, specification.long_input)
    post_oracle = repeat(post_source, specification.long_input)
    if not all((short_oracle, long_oracle, post_oracle)):
        raise RuntimeError(f"{specification.case_id}: an oracle is empty")
    post_state = json.loads(post_oracle)
    checkpoints = dict.fromkeys(
        [
            *(
                max(1, long_count * numerator // denominator)
                for numerator, denominator in (
                    (78, 100),
                    (2, 3),
                    (1, 2),
                    (1, 3),
                    (1, 4),
                    (1, 10),
                )
            ),
            1,
        ]
    )
    for checkpoint in checkpoints:
        inside_source = inside_loop_program(
            specification, checkpoint, inside_expression
        )
        inside_oracle = repeat(inside_source, specification.long_input)
        inside_state = json.loads(inside_oracle)
        if list(inside_state) != list(post_state):
            raise RuntimeError(f"{specification.case_id}: state field order differs")
        if any(
            type(inside_state[key]) is not type(post_state[key]) for key in fields
        ):
            raise RuntimeError(f"{specification.case_id}: state field types differ")
        if inside_state != post_state:
            break
    else:
        raise RuntimeError(f"{specification.case_id}: state projection did not change")

    case_root = PROBLEMS / specification.case_id
    if case_root.exists():
        shutil.rmtree(case_root)
    sources = {
        "short-trace-final": specification.source,
        "long-trace-final": specification.source,
        "inside-loop-state": inside_source,
        "post-loop-state": post_source,
    }
    inputs = {
        "short-trace-final": specification.short_input,
        "long-trace-final": specification.long_input,
        "inside-loop-state": specification.long_input,
        "post-loop-state": specification.long_input,
    }
    oracles = {
        "short-trace-final": short_oracle,
        "long-trace-final": long_oracle,
        "inside-loop-state": inside_oracle,
        "post-loop-state": post_oracle,
    }
    arm_records: dict[str, object] = {}
    for arm in ARMS:
        directory = case_root / arm
        write(directory / "program.py", sources[arm])
        write(directory / "input.txt", inputs[arm])
        write(directory / "ground-output.txt", oracles[arm])
        arm_records[arm] = arm_metadata(
            sources[arm],
            inputs[arm],
            oracles[arm],
            input_variant="short" if arm == "short-trace-final" else "long",
            source_variant=(
                arm
                if arm in {"inside-loop-state", "post-loop-state"}
                else "clean"
            ),
        )

    return {
        "case_id": specification.case_id,
        "title": specification.title,
        "category": specification.category,
        "language": "python",
        "source_origin": specification.source_origin,
        "algorithm_reference": specification.reference,
        "algorithm_reference_url": specification.reference_url,
        "selection": "selected before model evaluation as a canonical state-rich algorithm comparable to the original ten-program pilot",
        "core_loop": {
            "baseline_line": line_number(specification.source, specification.anchor),
            "statement": specification.anchor.strip(),
            "short_executions": short_count,
            "long_executions": long_count,
            "long_to_short_ratio": long_count / short_count,
        },
        "checkpoints": {
            "inside_loop_occurrence": checkpoint,
            "inside_loop_fraction": checkpoint / long_count,
            "post_loop_baseline_line": line_number(specification.source, specification.out_anchor),
            "fields": list(fields),
            "field_types": [type(inside_state[field]).__name__ for field in fields],
            "serialization": "canonical compact JSON",
        },
        "validation": {
            "repeated_executions": REPETITIONS,
            "deterministic_oracles": True,
            "long_increases_core_loop": True,
            "state_arms_share_input": True,
            "state_projection_schema_matches": True,
            "state_projection_changed": True,
        },
        "arms": arm_records,
    }


def main() -> int:
    expected = {specification.case_id for specification in SPECS}
    for path in PROBLEMS.iterdir():
        if path.is_dir() and path.name not in expected:
            shutil.rmtree(path)
    records = [materialize_case(specification) for specification in SPECS]
    payload = {
        "experiment": "classic_algorithms_state_prediction",
        "case_count": len(records),
        "prediction_count_per_model": len(records) * len(ARMS),
        "arms": list(ARMS),
        "cases": records,
    }
    write(ROOT / "cases.json", json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"Materialized {len(records)} cases x {len(ARMS)} arms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
