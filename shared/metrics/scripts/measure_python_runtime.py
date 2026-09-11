#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


NOT_MEASURED = "NOT_MEASURED"
RUNTIME_METRICS = (
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
RUNNER = Path(__file__).with_name("python_runtime_metrics.py")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def unavailable(
    reason: str,
    source_label: str,
    artifact_root: Path,
    repetitions: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, int | str], dict[str, Any]]:
    values = {metric: NOT_MEASURED for metric in RUNTIME_METRICS}
    return values, {
        "status": "NOT_MEASURED",
        "failure": reason,
        "source_label": source_label,
        "artifact_root": str(artifact_root),
        "runtime": f"{platform.python_implementation()} {platform.python_version()}",
        "repetitions": repetitions or [],
    }


def measure_execution(
    source_path: Path,
    input_path: Path,
    oracle_path: Path,
    artifact_root: Path,
    source_label: str,
    timeout: int,
    repetitions: int = 3,
    state_cell_visit_limit: int = 2_000_000,
) -> tuple[dict[str, int | str], dict[str, Any]]:
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT": str(
            state_cell_visit_limit
        ),
    }
    expected = oracle_path.read_bytes()
    try:
        natural = subprocess.run(
            [sys.executable, str(source_path)],
            input=input_path.read_bytes(),
            capture_output=True,
            timeout=timeout,
            cwd=source_path.parent,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return unavailable(
            "natural execution timed out", source_label, artifact_root
        )
    if natural.returncode != 0:
        return unavailable(
            f"natural runtime exited {natural.returncode}",
            source_label,
            artifact_root,
        )
    if natural.stdout != expected:
        return unavailable(
            "natural stdout did not match ground-output.txt",
            source_label,
            artifact_root,
        )

    measured: list[dict[str, Any]] = []
    for repetition in range(1, repetitions + 1):
        artifact = artifact_root / f"repetition-{repetition}.csv.gz"
        result_path = artifact_root / f"repetition-{repetition}.json"
        command = [
            sys.executable,
            str(RUNNER),
            str(source_path),
            source_label,
            str(artifact),
            str(result_path),
        ]
        try:
            completed = subprocess.run(
                command,
                input=input_path.read_bytes(),
                capture_output=True,
                timeout=timeout,
                cwd=source_path.parent,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            return unavailable(
                f"traced repetition {repetition} timed out",
                source_label,
                artifact_root,
                measured,
            )
        if not result_path.is_file():
            return unavailable(
                f"traced repetition {repetition} exited {completed.returncode} without result",
                source_label,
                artifact_root,
                measured,
            )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        result_path.unlink()
        if payload["status"] != "ok" or completed.returncode != 0:
            return unavailable(
                payload.get("error")
                or f"traced repetition {repetition} exited {completed.returncode}",
                source_label,
                artifact_root,
                measured,
            )
        if completed.stdout != expected:
            return unavailable(
                f"traced repetition {repetition} stdout did not match oracle",
                source_label,
                artifact_root,
                measured,
            )
        measured.append(
            {
                **payload,
                "repetition": repetition,
                "raw_artifact": str(artifact),
            }
        )

    trace_values = {
        int(repetition["Omega_hat_NativeTrace"]) for repetition in measured
    }
    if len(trace_values) != 1:
        return unavailable(
            "NativeTrace counts differed across repetitions",
            source_label,
            artifact_root,
            measured,
        )
    raw_series = {
        (
            repetition["raw_artifact_sha256"],
            int(repetition["raw_observation_rows"]),
        )
        for repetition in measured
    }
    if len(raw_series) != 1:
        values = {
            "Omega_hat_NativeTrace": next(iter(trace_values)),
            "Omega_hat_StateSize": NOT_MEASURED,
            "Omega_hat_StateLoad": NOT_MEASURED,
        }
        return values, {
            "status": "PARTIAL",
            "failure": "raw state observations differed across repetitions",
            "source_label": source_label,
            "artifact_root": str(artifact_root),
            "runtime": f"{platform.python_implementation()} {platform.python_version()}",
            "repetitions": measured,
        }

    state_failures = [repetition["state_failure"] for repetition in measured]
    state_available = all(failure is None for failure in state_failures)
    state_values: dict[str, int | str] = {}
    for metric in ("Omega_hat_StateSize", "Omega_hat_StateLoad"):
        values = {repetition[metric] for repetition in measured}
        state_values[metric] = (
            int(next(iter(values)))
            if state_available and len(values) == 1
            else NOT_MEASURED
        )
    failure = None
    if not state_available:
        failure = "state traversal was unavailable"
    elif NOT_MEASURED in state_values.values():
        failure = "state aggregates differed across repetitions"
    values = {
        "Omega_hat_NativeTrace": next(iter(trace_values)),
        **state_values,
    }
    return values, {
        "status": "OK" if failure is None else "PARTIAL",
        "failure": failure,
        "source_label": source_label,
        "artifact_root": str(artifact_root),
        "runtime": f"{platform.python_implementation()} {platform.python_version()}",
        "state_cell_visit_limit": state_cell_visit_limit,
        "adapter_version": measured[0]["adapter_version"],
        "observation_convention": measured[0]["observation_convention"],
        "repetitions": measured,
    }
