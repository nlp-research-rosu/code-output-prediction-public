#!/usr/bin/env python3
"""Measure every NetworkX arm with the repository's shared Python adapter."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
from typing import Any

import networkx as nx


EXPERIMENT = Path(__file__).resolve().parents[2]
REPOSITORY = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent
PROBLEMS = EXPERIMENT / "problems"
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
NOT_MEASURED = "NOT_MEASURED"
REPETITIONS = max(1, int(os.environ.get("COMPLEXITY_REPETITIONS", "1")))
TIMEOUT_SECONDS = int(os.environ.get("COMPLEXITY_TRACE_TIMEOUT_SECONDS", "600"))
STATE_CELL_VISIT_LIMIT = int(
    os.environ.get("COMPLEXITY_STATE_CELL_VISIT_LIMIT", "50000000")
)
WORKERS = max(1, int(os.environ.get("COMPLEXITY_WORKERS", "4")))
INSTRUMENTATION = "python-shared-runtime-v1"
METRIC_METHODS = {
    "Omega_CC": "python-control-flow-v2",
    "Omega_hat_NativeTrace": "python-cpython-monitoring-instruction-v2",
    "Omega_hat_StateSize": "python-cpython-program-state-v5",
    "Omega_hat_StateLoad": "python-cpython-program-state-sum-v1",
}
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


def load_module(path: Path, name: str):
    specification = importlib.util.spec_from_file_location(name, path)
    if specification is None or specification.loader is None:
        raise RuntimeError(f"Could not load {path}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


RUNTIME = load_module(
    REPOSITORY / "shared/metrics/scripts/measure_python_runtime.py",
    "shared_measure_python_runtime",
)
PYTHON_COMPLEXITY = load_module(
    REPOSITORY / "shared/metrics/scripts/python_complexity.py",
    "shared_python_complexity",
)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(content, encoding="utf-8", newline="")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def execution_id(source_hash: str, input_hash: str) -> str:
    identity = {
        "source_sha256": source_hash,
        "input_sha256": input_hash,
        "runtime": f"CPython {platform.python_version()}",
        "instrumentation": INSTRUMENTATION,
        "metric_methods": METRIC_METHODS,
    }
    payload = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + sha256_bytes(payload)


def relative_artifact_paths(metadata: dict[str, Any]) -> None:
    artifact_root = metadata.get("artifact_root")
    if isinstance(artifact_root, str):
        metadata["artifact_root"] = Path(artifact_root).relative_to(EXPERIMENT).as_posix()
    for repetition in metadata.get("repetitions") or []:
        value = repetition.get("raw_artifact")
        if not isinstance(value, str):
            continue
        repetition["raw_artifact"] = Path(value).relative_to(EXPERIMENT).as_posix()


def unavailable_reason(metadata: dict[str, Any]) -> str | None:
    failure = metadata.get("failure")
    if isinstance(failure, str) and failure:
        if failure != "state traversal was unavailable":
            return failure
    repetitions = metadata.get("repetitions") or []
    state_failure = repetitions[0].get("state_failure") if repetitions else None
    if isinstance(state_failure, dict):
        return str(state_failure.get("type") or state_failure.get("reason"))
    return failure if isinstance(failure, str) else None


def measure_profile(case: dict[str, Any], arm: str) -> tuple[dict[str, Any], dict[str, Any]]:
    case_id = str(case["case_id"])
    root = PROBLEMS / case_id / arm
    source = root / "program.py"
    input_path = root / "input.txt"
    oracle = root / "ground-output.txt"
    source_hash = sha256_bytes(source.read_bytes())
    input_hash = sha256_bytes(input_path.read_bytes())
    oracle_hash = sha256_bytes(oracle.read_bytes())
    dynamic_id = execution_id(source_hash, input_hash)
    artifact_root = (
        OUTPUT
        / "raw-state-observations"
        / arm
        / dynamic_id.removeprefix("sha256:")
    )
    metrics, metadata = RUNTIME.measure_execution(
        source.resolve(),
        input_path.resolve(),
        oracle.resolve(),
        artifact_root.resolve(),
        f"problems/{case_id}/{arm}/program.py",
        TIMEOUT_SECONDS,
        repetitions=REPETITIONS,
        state_cell_visit_limit=STATE_CELL_VISIT_LIMIT,
    )
    relative_artifact_paths(metadata)
    repetitions = metadata.get("repetitions") or []
    trace_values = [
        repetition["Omega_hat_NativeTrace"]
        for repetition in repetitions
        if isinstance(repetition.get("Omega_hat_NativeTrace"), int)
    ]
    state_values = [
        repetition["Omega_hat_StateSize"]
        for repetition in repetitions
        if isinstance(repetition.get("Omega_hat_StateSize"), int)
    ]
    state_load_values = [
        repetition["Omega_hat_StateLoad"]
        for repetition in repetitions
        if isinstance(repetition.get("Omega_hat_StateLoad"), int)
    ]
    observation_counts = [
        repetition["raw_observation_rows"]
        for repetition in repetitions
        if isinstance(repetition.get("raw_observation_rows"), int)
    ]
    state_available = isinstance(metrics["Omega_hat_StateSize"], int)
    reason = unavailable_reason(metadata)
    row = {
        "case_id": case_id,
        "cohort": str(case["cohort"]),
        "arm_id": arm,
        "measurement_source_arm": arm,
        "execution_id": dynamic_id,
        **metrics,
        "Omega_CC": PYTHON_COMPLEXITY.measure_python_static(
            source.read_text(encoding="utf-8")
        )["Omega_CC"],
        "state_size_status": "OK" if state_available else reason or NOT_MEASURED,
        "native_trace_event": "CPython 3.12 instruction events in target-source frames",
        "state_size_observation": "initial state, post-mutation boundaries, and return or unwind events in target-source frames",
        "state_load_observation": "sum over the same complete state-observation series as StateSize",
        "state_observation_count": observation_counts[0] if observation_counts else 0,
        "source_sha256": source_hash,
        "input_sha256": input_hash,
        "oracle_sha256": oracle_hash,
        "native_trace_repetitions": len(trace_values),
        "state_size_repetitions": len(state_values),
        "raw_native_trace_measurements": json.dumps(trace_values, separators=(",", ":")),
        "raw_state_size_measurements": json.dumps(state_values, separators=(",", ":")),
        "raw_state_load_measurements": json.dumps(state_load_values, separators=(",", ":")),
        "raw_state_observation_counts": json.dumps(observation_counts, separators=(",", ":")),
    }
    evidence = {
        "case_id": case_id,
        "arm_id": arm,
        "execution_id": dynamic_id,
        "source_sha256": source_hash,
        "input_sha256": input_hash,
        "oracle_sha256": oracle_hash,
        "metrics": metrics,
        "metric_methods": METRIC_METHODS,
        "unavailable_reason": reason,
        "runtime_measurement": metadata,
    }
    print(
        f"MEASURED {case_id}/{arm} trace={metrics['Omega_hat_NativeTrace']} "
        f"state={metrics['Omega_hat_StateLoad']}",
        flush=True,
    )
    return row, evidence


def is_measured(value: Any) -> bool:
    return isinstance(value, int) or (
        isinstance(value, str) and value.isdigit()
    )


def write_outputs(
    completed: dict[tuple[str, str], tuple[dict[str, Any], dict[str, Any]]]
) -> None:
    arm_order = {arm: index for index, arm in enumerate(ARMS)}
    ordered = sorted(
        completed.values(),
        key=lambda item: (item[0]["case_id"], arm_order[item[0]["arm_id"]]),
    )
    rows = [item[0] for item in ordered]
    evidence = [item[1] for item in ordered]
    import io

    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write(OUTPUT / "measurements.csv", handle.getvalue())

    coverage = {
        metric: sum(is_measured(row[metric]) for row in rows)
        for metric in (
            "Omega_hat_NativeTrace",
            "Omega_hat_StateSize",
            "Omega_hat_StateLoad",
        )
    }
    unavailable = Counter(
        evidence_row["unavailable_reason"]
        for evidence_row in evidence
        if evidence_row["unavailable_reason"]
    )
    repetition_counts = sorted(
        {
            len((evidence_row.get("runtime_measurement") or {}).get("repetitions") or [])
            for evidence_row in evidence
            if (evidence_row.get("runtime_measurement") or {}).get("repetitions")
        }
    )
    manifest = {
        "schema_version": 4,
        "benchmark": "networkx_network_simplex_state_prediction",
        "profiles": len(rows),
        "executions": len({row["execution_id"] for row in rows}),
        "arms": list(ARMS),
        "python": platform.python_version(),
        "networkx": nx.__version__,
        "instrumentation": INSTRUMENTATION,
        "metric_methods": METRIC_METHODS,
        "repetition_counts": repetition_counts,
        "timeout_seconds": TIMEOUT_SECONDS,
        "state_cell_visit_limit": STATE_CELL_VISIT_LIMIT,
        "coverage": coverage,
        "unavailable_reasons": dict(sorted(unavailable.items())),
        "profile_evidence": evidence,
        "output_sha256": sha256_bytes((OUTPUT / "measurements.csv").read_bytes()),
    }
    atomic_write(
        OUTPUT / "measurement-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )


def main() -> int:
    if sys.version_info[:2] != (3, 12):
        raise RuntimeError(f"CPython 3.12 is required; found {platform.python_version()}")
    if nx.__version__ != "3.4.2":
        raise RuntimeError(f"NetworkX 3.4.2 is required; found {nx.__version__}")
    cases = json.loads((EXPERIMENT / "cases.json").read_text(encoding="utf-8"))["cases"]
    rows = list(csv.DictReader((OUTPUT / "measurements.csv").open()))
    manifest = json.loads((OUTPUT / "measurement-manifest.json").read_text())
    evidence = manifest["profile_evidence"]
    completed = {
        (row["case_id"], row["arm_id"]): (row, evidence_row)
        for row, evidence_row in zip(rows, evidence, strict=True)
    }
    case_by_id = {str(case["case_id"]): case for case in cases}
    tasks = [
        (case_by_id[case_id], arm)
        for (case_id, arm), (row, _) in completed.items()
        if not is_measured(row["Omega_hat_StateSize"])
        or not is_measured(row["Omega_hat_StateLoad"])
    ]
    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        futures = {
            executor.submit(measure_profile, case, arm): (case["case_id"], arm)
            for case, arm in tasks
        }
        for future in as_completed(futures):
            row, evidence_row = future.result()
            completed[(row["case_id"], row["arm_id"])] = (row, evidence_row)
            write_outputs(completed)

    write_outputs(completed)
    current_rows = [item[0] for item in completed.values()]
    coverage = {
        metric: sum(is_measured(row[metric]) for row in current_rows)
        for metric in ("Omega_hat_NativeTrace", "Omega_hat_StateSize", "Omega_hat_StateLoad")
    }
    print(f"COMPLETE profiles={len(current_rows)} coverage={coverage}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
