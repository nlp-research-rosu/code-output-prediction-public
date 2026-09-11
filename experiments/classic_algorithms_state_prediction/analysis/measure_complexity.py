#!/usr/bin/env python3

from __future__ import annotations

import argparse
import csv
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import platform
import tempfile
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
MEASUREMENTS = EXPERIMENT / "measurements/program-complexity"
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
METRICS = (
    "Omega_CC",
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
RUNTIME_METRICS = METRICS[1:]
NOT_MEASURED = "NOT_MEASURED"
METHODS = {
    "Omega_CC": "python-control-flow-v2",
    "Omega_hat_NativeTrace": "python-cpython-monitoring-instruction-v2",
    "Omega_hat_StateSize": "python-cpython-program-state-v5",
    "Omega_hat_StateLoad": "python-cpython-program-state-sum-v1",
}
PROFILE_FIELDS = (
    "problem",
    "arm",
    "source_sha256",
    "input_sha256",
    "execution_id",
    *METRICS,
)


def load_module(name: str, path: Path) -> Any:
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


STATIC = load_module(
    "shared_python_complexity",
    ROOT / "shared/metrics/scripts/python_complexity.py",
)
RUNTIME = load_module(
    "shared_measure_python_runtime",
    ROOT / "shared/metrics/scripts/measure_python_runtime.py",
)
RUNTIME_ADAPTER = load_module(
    "shared_python_runtime_metrics_adapter",
    ROOT / "shared/metrics/scripts/python_runtime_metrics.py",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent, text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def execution_id(
    source: Path,
    input_path: Path,
    timeout: int,
    state_cell_visit_limit: int,
) -> str:
    identity = {
        "source_sha256": sha256(source.read_bytes()),
        "input_sha256": sha256(input_path.read_bytes()),
        "runtime": f"{platform.python_implementation()} {platform.python_version()}",
        "adapter_version": RUNTIME_ADAPTER.ADAPTER_VERSION,
        "observation_convention": RUNTIME_ADAPTER.OBSERVATION_CONVENTION,
        "execution_timeout_seconds": timeout,
        "state_cell_visit_limit": state_cell_visit_limit,
    }
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":"))
    return "sha256:" + sha256(payload.encode())


def normalize_runtime_measurement(measurement: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(measurement))
    for field in ("artifact_root",):
        value = normalized.get(field)
        if isinstance(value, str):
            normalized[field] = Path(value).relative_to(EXPERIMENT).as_posix()
    for repetition in normalized.get("repetitions", []):
        value = repetition.get("raw_artifact")
        if isinstance(value, str):
            repetition["raw_artifact"] = Path(value).relative_to(EXPERIMENT).as_posix()
    return normalized


def measure_dynamic(
    case_id: str,
    source_arm: str,
    timeout: int,
    state_cell_visit_limit: int,
    repetitions: int,
) -> tuple[tuple[str, str], dict[str, Any]]:
    arm_root = EXPERIMENT / "problems" / case_id / source_arm
    source = arm_root / "program.py"
    input_path = arm_root / "input.txt"
    oracle = arm_root / "ground-output.txt"
    identifier = execution_id(
        source, input_path, timeout, state_cell_visit_limit
    )
    artifact_root = (
        MEASUREMENTS
        / "raw-state-observations"
        / source_arm
        / identifier.removeprefix("sha256:")
    )
    metrics, runtime_measurement = RUNTIME.measure_execution(
        source,
        input_path,
        oracle,
        artifact_root,
        source.relative_to(EXPERIMENT).as_posix(),
        timeout,
        repetitions=repetitions,
        state_cell_visit_limit=state_cell_visit_limit,
    )
    result = {
        "execution_id": identifier,
        "source_arm": source_arm,
        "source": source.relative_to(EXPERIMENT).as_posix(),
        "source_sha256": sha256(source.read_bytes()),
        "input_sha256": sha256(input_path.read_bytes()),
        "oracle": oracle.relative_to(EXPERIMENT).as_posix(),
        "oracle_sha256": sha256(oracle.read_bytes()),
        "runtime": f"{platform.python_implementation()} {platform.python_version()}",
        "adapter_version": RUNTIME_ADAPTER.ADAPTER_VERSION,
        "observation_convention": RUNTIME_ADAPTER.OBSERVATION_CONVENTION,
        "execution_timeout_seconds": timeout,
        "state_cell_visit_limit": state_cell_visit_limit,
        "status": (
            "OK"
            if metrics["Omega_hat_NativeTrace"] != NOT_MEASURED
            else "NOT_MEASURED"
        ),
        "metrics": metrics,
        "runtime_measurement": normalize_runtime_measurement(runtime_measurement),
    }
    return (case_id, source_arm), result


def load_profiles(arm: str) -> dict[str, dict[str, Any]]:
    path = MEASUREMENTS / arm / "python/profiles.jsonl"
    if not path.is_file():
        return {}
    return {
        record["problem"]: record
        for record in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def reusable_dynamic(
    case_id: str,
    arm: str,
    record: dict[str, Any] | None,
    timeout: int,
    state_cell_visit_limit: int,
    recover_missing_runtime: bool,
) -> dict[str, Any] | None:
    if record is None:
        return None
    arm_root = EXPERIMENT / "problems" / case_id / arm
    source = arm_root / "program.py"
    input_path = arm_root / "input.txt"
    oracle = arm_root / "ground-output.txt"
    expected_id = execution_id(source, input_path, timeout, state_cell_visit_limit)
    dynamic = record.get("dynamic_execution") or {}
    metrics = record.get("metrics") or {}
    has_state = all(
        metrics.get(metric) != NOT_MEASURED
        for metric in ("Omega_hat_StateSize", "Omega_hat_StateLoad")
    )
    if dynamic.get("execution_id") != expected_id and not (
        recover_missing_runtime and has_state
    ):
        return None
    if dynamic.get("source_sha256") != sha256(source.read_bytes()):
        return None
    if dynamic.get("input_sha256") != sha256(input_path.read_bytes()):
        return None
    if dynamic.get("oracle_sha256") != sha256(oracle.read_bytes()):
        return None
    measurement = record.get("runtime_measurement") or {}
    for repetition in measurement.get("repetitions", []):
        artifact_value = repetition.get("raw_artifact")
        artifact_hash = repetition.get("raw_artifact_sha256")
        if not isinstance(artifact_value, str) or not isinstance(artifact_hash, str):
            return None
        artifact = EXPERIMENT / artifact_value
        if not artifact.is_file() or sha256(artifact.read_bytes()) != artifact_hash:
            return None
    return {
        **dynamic,
        "metrics": {metric: record["metrics"][metric] for metric in RUNTIME_METRICS},
        "runtime_measurement": measurement,
    }


def profile(
    case_id: str,
    arm: str,
    dynamic: dict[str, Any],
    existing: dict[str, Any] | None,
) -> dict[str, Any]:
    arm_root = EXPERIMENT / "problems" / case_id / arm
    source = arm_root / "program.py"
    input_path = arm_root / "input.txt"
    source_bytes = source.read_bytes()
    static_reusable = (
        existing is not None
        and existing.get("source_sha256") == sha256(source_bytes)
        and existing.get("metric_methods", {}).get("Omega_CC")
        == METHODS["Omega_CC"]
        and existing.get("metrics", {}).get("Omega_CC") != NOT_MEASURED
    )
    static = (
        {"Omega_CC": existing["metrics"]["Omega_CC"]}
        if static_reusable
        else STATIC.measure_python_static(source_bytes.decode("utf-8"))
    )
    metrics = {
        "Omega_CC": static["Omega_CC"],
        **dynamic["metrics"],
    }
    runtime_status = dynamic["runtime_measurement"]["status"]
    limitations = [
        "Raw values are comparable only under this CPython adapter and convention."
    ]
    if runtime_status != "OK":
        limitations.append(
            str(dynamic["runtime_measurement"].get("failure") or runtime_status)
        )
    provenance = {
        "Omega_CC": "reused" if static_reusable else "measured",
        **{
            metric: (
                "reused"
                if existing is not None
                and (existing.get("dynamic_execution") or {}).get("execution_id")
                == dynamic["execution_id"]
                else "measured"
                if metrics[metric] != NOT_MEASURED
                else "failed"
            )
            for metric in RUNTIME_METRICS
        },
    }
    return {
        "schema_version": 1,
        "program": f"{case_id}/{arm}",
        "problem": case_id,
        "arm": arm,
        "language": f"Python {platform.python_version()}",
        "input": (arm_root / "input.txt").relative_to(EXPERIMENT).as_posix(),
        "scope": "complete visible program, excluding natural-language prompt",
        "source_sha256": sha256(source_bytes),
        "input_sha256": sha256(input_path.read_bytes()),
        "metric_methods": METHODS,
        "metric_provenance": provenance,
        "metrics": metrics,
        "dynamic_execution": {
            key: dynamic[key]
            for key in (
                "execution_id",
                "source_arm",
                "source",
                "source_sha256",
                "input_sha256",
                "oracle",
                "oracle_sha256",
                "runtime",
                "adapter_version",
                "observation_convention",
                "execution_timeout_seconds",
                "state_cell_visit_limit",
                "status",
            )
        },
        "runtime_measurement": dynamic["runtime_measurement"],
        "method_notes": {
            "parser_cfg": "CPython AST extended-decision cyclomatic complexity",
            "execution": "Three isolated CPython runs with byte-exact oracle validation",
            "limitations": limitations,
        },
        "failures": (
            []
            if dynamic["status"] == "OK"
            else [str(dynamic["runtime_measurement"].get("failure"))]
        ),
    }


def csv_content(records: list[dict[str, Any]]) -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=PROFILE_FIELDS, lineterminator="\n")
    writer.writeheader()
    for record in records:
        execution = record["dynamic_execution"]
        writer.writerow(
            {
                "problem": record["problem"],
                "arm": record["arm"],
                "source_sha256": record["source_sha256"],
                "input_sha256": record["input_sha256"],
                "execution_id": execution["execution_id"],
                **record["metrics"],
            }
        )
    return output.getvalue()


def write_arm(
    arm: str,
    records: list[dict[str, Any]],
    timeout: int,
    state_cell_visit_limit: int,
    repetitions: int,
) -> None:
    output = MEASUREMENTS / arm / "python"
    payload = "".join(
        json.dumps(record, sort_keys=True) + "\n" for record in records
    )
    atomic_write(output / "profiles.jsonl", payload)
    atomic_write(output / "profiles.csv", csv_content(records))
    failed = [record for record in records if record["failures"]]
    atomic_write(
        output / "failures.jsonl",
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in failed),
    )
    metric_coverage = {
        metric: {
            "measured": sum(
                record["metrics"][metric] != NOT_MEASURED for record in records
            ),
            "unavailable": sum(
                record["metrics"][metric] == NOT_MEASURED for record in records
            ),
        }
        for metric in METRICS
    }
    runtime_repetition_counts = Counter(
        str(len((record.get("runtime_measurement") or {}).get("repetitions") or []))
        for record in records
    )
    manifest = {
        "schema": "classic-algorithms-program-complexity-v1",
        "experiment": EXPERIMENT.name,
        "arm": arm,
        "language": f"Python {platform.python_version()}",
        "profiles": len(records),
        "unique_execution_ids": len(
            {record["dynamic_execution"]["execution_id"] for record in records}
        ),
        "execution_timeout_seconds": timeout,
        "state_cell_visit_limit": state_cell_visit_limit,
        "last_requested_runtime_repetitions": repetitions,
        "runtime_repetition_counts": dict(
            sorted(runtime_repetition_counts.items())
        ),
        "metric_methods": METHODS,
        "metric_coverage": metric_coverage,
        "profiles_sha256": sha256((output / "profiles.jsonl").read_bytes()),
    }
    atomic_write(
        output / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


def write_readme(dynamic: dict[tuple[str, str], dict[str, Any]]) -> None:
    execution_count = len(dynamic)
    native_measured = sum(
        result["metrics"]["Omega_hat_NativeTrace"] != NOT_MEASURED
        for result in dynamic.values()
    )
    state_measured = sum(
        result["metrics"]["Omega_hat_StateSize"] != NOT_MEASURED
        for result in dynamic.values()
    )
    unavailable = sorted(
        f"{case_id}/{source_arm}"
        for (case_id, source_arm), result in dynamic.items()
        if result["metrics"]["Omega_hat_StateSize"] == NOT_MEASURED
    )
    unavailable_text = ",\n".join(f"`{value}`" for value in unavailable)
    content = f"""# Program complexity measurements

This package measures the exact Python source and source-input executions used
by the experiment. Static and dynamic profiles cover all four canonical arms.

The retained dimensions are `Omega_CC`, `Omega_hat_NativeTrace`,
`Omega_hat_StateSize`, and `Omega_hat_StateLoad`. A missing dynamic value is
written as `NOT_MEASURED`, never as zero. Raw compressed state-observation rows
and three-repetition provenance live under `raw-state-observations/`.

Metric names, formulas, units, calculation, and interpretation are defined in
the [shared metric definitions](../../../../shared/metrics/README.md).
This experiment uses the Python extended-decision convention, target-frame
CPython instruction events, and the shared Python reachable-value adapter.

`Omega_hat_NativeTrace` is available for {native_measured}/{execution_count} unique
executions. `Omega_hat_StateSize` and `Omega_hat_StateLoad` are available for
{state_measured}/{execution_count}. The unavailable executions are
{unavailable_text}; each exceeded the pinned 50,000,000 semantic-cell traversal
limit. One semantic-cell visit is one recursive inspection of a reachable
value. The counter accumulates over every state observation in one isolated
measurement repetition, so repeatedly observing a large container can exhaust
the budget even when no single state has 50,000,000 cells. The limit controls
measurement work; it is not a program metric, byte count, variable count, or
instruction count. No partial peak, sampled state series, or proxy value is
reported.

<!-- dataset-complexity-summary:start -->
<!-- dataset-complexity-summary:end -->

## Reproduce

```bash
uv run --python 3.12.11 python -m experiments.classic_algorithms_state_prediction.analysis.measure_complexity --workers 4 --execution-timeout 120 --state-cell-visit-limit 50000000
python3 shared/metrics/scripts/summarize_dataset.py --config experiments/classic_algorithms_state_prediction/measurements/program-complexity/dataset-summary-config.json --output experiments/classic_algorithms_state_prediction/measurements/program-complexity --readme experiments/classic_algorithms_state_prediction/measurements/program-complexity/README.md
```
"""
    atomic_write(MEASUREMENTS / "README.md", content)


def write_summary_config() -> None:
    config = {
        "schema": "program-complexity-dataset-summary-config-v1",
        "rows": [
            {
                "dataset_id": EXPERIMENT.name,
                "label": "Classic algorithms state prediction",
                "static_profiles": ["short-trace-final/python/profiles.jsonl"],
                "dynamic_profiles": [
                    "short-trace-final/python/profiles.jsonl",
                    "long-trace-final/python/profiles.jsonl",
                    "inside-loop-state/python/profiles.jsonl",
                    "post-loop-state/python/profiles.jsonl",
                ],
                "note": "Static medians use one clean source per case. Dynamic medians use the four canonical execution identities per case.",
            }
        ],
    }
    atomic_write(
        MEASUREMENTS / "dataset-summary-config.json",
        json.dumps(config, indent=2, sort_keys=True) + "\n",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--execution-timeout", type=int, default=120)
    parser.add_argument(
        "--state-cell-visit-limit", type=int, default=50_000_000
    )
    parser.add_argument("--repetitions", type=int, default=1)
    parser.add_argument("--recover-missing-runtime", action="store_true")
    arguments = parser.parse_args(argv)
    if (
        arguments.workers < 1
        or arguments.execution_timeout < 1
        or arguments.state_cell_visit_limit < 1
        or arguments.repetitions < 1
    ):
        parser.error("workers, execution-timeout, state-cell-visit-limit, and repetitions must be positive")
    cases = json.loads((EXPERIMENT / "cases.json").read_text(encoding="utf-8"))[
        "cases"
    ]
    case_ids = [case["case_id"] for case in cases]
    existing = {arm: load_profiles(arm) for arm in ARMS}
    dynamic: dict[tuple[str, str], dict[str, Any]] = {}
    tasks = []
    for case_id in case_ids:
        for arm in ARMS:
            reused = reusable_dynamic(
                case_id,
                arm,
                existing[arm].get(case_id),
                arguments.execution_timeout,
                arguments.state_cell_visit_limit,
                arguments.recover_missing_runtime,
            )
            if reused is None:
                tasks.append((case_id, arm))
            else:
                dynamic[(case_id, arm)] = reused
    with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
        futures = {
            executor.submit(
                measure_dynamic,
                case_id,
                source_arm,
                arguments.execution_timeout,
                arguments.state_cell_visit_limit,
                arguments.repetitions,
            ): (case_id, source_arm)
            for case_id, source_arm in tasks
        }
        for index, future in enumerate(as_completed(futures), 1):
            key, result = future.result()
            dynamic[key] = result
            print(f"MEASURED {index}/{len(tasks)} {key[0]}/{key[1]}", flush=True)
    for arm in ARMS:
        records = [
            profile(
                case_id,
                arm,
                dynamic[(case_id, arm)],
                existing[arm].get(case_id),
            )
            for case_id in case_ids
        ]
        write_arm(
            arm,
            records,
            arguments.execution_timeout,
            arguments.state_cell_visit_limit,
            arguments.repetitions,
        )
    write_readme(dynamic)
    write_summary_config()
    print(
        f"COMPLETE profiles={len(case_ids) * len(ARMS)} executions={len(dynamic)} output={MEASUREMENTS}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
