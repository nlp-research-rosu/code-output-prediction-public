"""Normalize committed profiles to the retained four-metric contract."""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .program_complexity import (
    ARMS,
    CPP_METRIC_METHODS,
    METRICS,
    NOT_MEASURED,
    PYTHON_METRIC_METHODS,
    SCHEMA_VERSION,
    apply_state_measurement_summary,
    atomic_write_text,
    explanation,
    sha256,
    write_program_complexity_readme,
    write_profiles_csv,
)


class NormalizationError(RuntimeError):
    pass


def observation_totals(path: Path, expected_sha256: str) -> tuple[int, int]:
    payload = path.read_bytes()
    if sha256(payload) != expected_sha256:
        raise NormalizationError(f"{path}: raw artifact hash does not match the profile")
    rows = csv.DictReader(io.StringIO(gzip.decompress(payload).decode("utf-8")))
    sizes = [int(row["state_size"]) for row in rows]
    if not sizes:
        raise NormalizationError(f"{path}: raw artifact contains no observations")
    return sum(sizes), max(sizes)


def normalize_record(
    record: dict[str, Any], benchmark: Path, language: str
) -> str:
    methods = PYTHON_METRIC_METHODS if language == "python" else CPP_METRIC_METHODS
    old_metrics = record.get("metrics") or {}
    metrics = {
        metric: old_metrics.get(metric, NOT_MEASURED)
        for metric in METRICS
    }
    status = "retained"

    if language == "python" and "Omega_hat_StateSize" in old_metrics:
        measurement = record.get("runtime_measurement") or {}
        repetitions = measurement.get("repetitions") or []
        peak = metrics["Omega_hat_StateSize"]
        if isinstance(peak, int):
            totals: set[int] = set()
            for repetition in repetitions:
                total, observed_peak = observation_totals(
                    benchmark / repetition["raw_artifact"],
                    repetition["raw_artifact_sha256"],
                )
                if observed_peak != peak:
                    raise NormalizationError(
                        f"{record['program']}: raw peak {observed_peak} does not "
                        f"reproduce committed Omega_hat_StateSize {peak}"
                    )
                if repetition.get("Omega_hat_StateLoad", total) != total:
                    raise NormalizationError(
                        f"{record['program']}: committed StateLoad does not match raw data"
                    )
                repetition["Omega_hat_StateLoad"] = total
                repetition.pop("Omega_hat_StateCount", None)
                repetition.pop("state_count_peak_event", None)
                totals.add(total)
            if len(totals) != 1:
                raise NormalizationError(
                    f"{record['program']}: state load differed across repetitions"
                )
            metrics["Omega_hat_StateLoad"] = totals.pop()
            status = "verified"
        else:
            metrics["Omega_hat_StateLoad"] = NOT_MEASURED
            for repetition in repetitions:
                repetition["Omega_hat_StateLoad"] = NOT_MEASURED
                repetition.pop("Omega_hat_StateCount", None)
                repetition.pop("state_count_peak_event", None)

    record["schema_version"] = SCHEMA_VERSION
    record["metric_methods"] = dict(methods)
    record["metrics"] = metrics
    provenance = record.get("metric_provenance") or {}
    record["metric_provenance"] = {
        metric: provenance.get(metric, "not_measured")
        for metric in METRICS
    }
    record["plain_english_profile"] = explanation(metrics)
    notes = record.get("method_notes") or {}
    record["method_notes"] = {
        "parser_cfg": notes.get("parser_cfg", "language-aware cyclomatic complexity"),
        "execution": notes.get("execution", NOT_MEASURED),
        "limitations": [
            value
            for value in notes.get("limitations", [])
            if not any(
                removed in value
                for removed in (
                    "Omega_DD",
                    "Omega_If",
                    "Omega_Loc",
                    "Omega_Loop",
                    "Omega_Voc",
                    "Omega_Vol",
                )
            )
        ],
    }
    measurement = record.get("runtime_measurement")
    if isinstance(measurement, dict):
        measurement.pop("state_count_peak_event", None)
    apply_state_measurement_summary(record)
    return status


def normalize_directory(root: Path, benchmark: Path, language: str) -> tuple[int, int]:
    profiles_path = root / "profiles.jsonl"
    records = [
        json.loads(line)
        for line in profiles_path.read_text(encoding="utf-8").splitlines()
        if line
    ]
    verified = sum(
        normalize_record(record, benchmark, language) == "verified"
        for record in records
    )
    atomic_write_text(
        profiles_path,
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
    )
    write_profiles_csv(root / "profiles.csv", records)

    manifest_path = root / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    methods = PYTHON_METRIC_METHODS if language == "python" else CPP_METRIC_METHODS
    manifest["schema_version"] = SCHEMA_VERSION
    manifest["metric_methods"] = dict(methods)
    manifest["metric_provenance"] = {
        metric: dict(
            sorted(
                Counter(
                    record.get("metric_provenance", {}).get(metric, "not_measured")
                    for record in records
                ).items()
            )
        )
        for metric in METRICS
    }
    manifest["profile_count"] = len(records)
    manifest["selected_profile_count"] = len(records)
    manifest["selected_problem_ids"] = [record["problem"] for record in records]
    manifest["profiles"] = [
        {
            "problem": record["problem"],
            "program": record["program"],
            "source_sha256": record["source_sha256"],
            "input_sha256": record["input_sha256"],
            "dynamic_execution_id": (record.get("dynamic_execution") or {}).get(
                "execution_id"
            ),
        }
        for record in records
    ]
    manifest["state_measurement_coverage"] = dict(
        sorted(Counter(record["state_measurement"]["status"] for record in records).items())
    )
    manifest["runtime_repetition_counts"] = dict(
        sorted(
            Counter(
                str(len((record.get("runtime_measurement") or {}).get("repetitions") or []))
                for record in records
            ).items()
        )
    )
    requested_repetitions = manifest.pop("runtime_repetitions", None)
    if requested_repetitions is not None:
        manifest["last_requested_runtime_repetitions"] = requested_repetitions
    atomic_write_text(
        manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    atomic_write_text(
        root / "failures.jsonl",
        "".join(
            json.dumps(record, sort_keys=True) + "\n"
            for record in records
            if record["failures"]
        ),
    )
    return verified, len(records)


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    benchmark = arguments.benchmark.resolve()
    root = benchmark / "measurements" / "program-complexity"
    total_verified = total_records = 0
    for arm in ARMS:
        arm_root = root / arm / "python"
        if not (arm_root / "profiles.jsonl").is_file():
            continue
        verified, records = normalize_directory(arm_root, benchmark, "python")
        total_verified += verified
        total_records += records
        print(f"{arm:16s} verified StateLoad {verified}/{records}")
    for arm in ARMS:
        cpp_root = root / arm / "cpp"
        if not (cpp_root / "profiles.jsonl").is_file():
            continue
        _, records = normalize_directory(cpp_root, benchmark, "cpp")
        total_records += records
        print(f"{f'{arm}/cpp':24s} retained metrics {records}/{records}")
    print(f"{'total':16s} normalized profiles {total_records}")
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--benchmark", type=Path, required=True)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
