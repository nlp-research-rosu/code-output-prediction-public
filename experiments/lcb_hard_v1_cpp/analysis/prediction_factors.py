#!/usr/bin/env python3
"""Prepare canonical prediction-factor points for lcb_hard_v1_cpp."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import workbench  # noqa: E402
from experiments.lcb_hard_v1_cpp import grade  # noqa: E402
from experiments.lcb_hard_v1_cpp.analysis.program_complexity import (  # noqa: E402
    ALL_DYNAMIC_METRICS,
    NOT_MEASURED,
    STATIC_METRICS,
)


POINT_FIELDS = (
    "series_id",
    "prediction_id",
    "program_id",
    "execution_id",
    "model_id",
    "arm_id",
    "arm_group",
    "scope",
    "metric_name",
    "x",
    "y",
)
ELIGIBLE_STATUSES = {
    "correct_valid",
    "correct_invalid",
    "wrong_valid",
    "wrong_invalid",
}
DYNAMIC_ARMS = grade.ARMS
MEASUREMENT_REASON_DEFINITIONS = {
    "ADAPTER_NOT_RUN": "The metric adapter did not run for this arm.",
    "TRACE_TIMEOUT": "The instrumented execution exceeded its timeout.",
    "NONDETERMINISTIC_TRACE": "Repeated executions produced different native trace counts.",
    "STATE_TRAVERSAL_WORK_LIMIT": "Exact state traversal exceeded the configured semantic-cell visit limit.",
    "UNSUPPORTED_REACHABLE_TYPE": "The reachable state contained a value that cannot be inspected faithfully.",
    "STATE_TRAVERSAL_RECURSION_LIMIT": "Exact state traversal exceeded the CPython recursion limit.",
    "MEASUREMENT_FAILED": "The metric adapter ran but did not produce a valid measurement.",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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


def load_profiles(path: Path, arm: str) -> dict[str, dict[str, Any]]:
    records = {}
    for line, text in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not text.strip():
            continue
        record = json.loads(text)
        if record.get("arm") != arm:
            raise ValueError(f"{path}:{line}: expected arm {arm}")
        problem = record.get("problem")
        if not isinstance(problem, str) or not problem:
            raise ValueError(f"{path}:{line}: missing problem id")
        if problem in records:
            raise ValueError(f"{path}:{line}: duplicate problem {problem}")
        records[problem] = record
    return records


def csv_content(rows: Iterable[dict[str, object]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=POINT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def measurement_unavailable_reason(record: dict[str, Any], metric: str) -> str:
    metrics = record.get("metrics") or {}
    if metric not in metrics:
        return "ADAPTER_NOT_RUN"
    if (record.get("metric_provenance") or {}).get(metric) == "not_requested":
        return "ADAPTER_NOT_RUN"
    measurement = record.get("runtime_measurement") or {}
    failure = str(measurement.get("failure") or "")
    if "timed out" in failure:
        return "TRACE_TIMEOUT"
    if "differed across repetitions" in failure:
        return "NONDETERMINISTIC_TRACE"
    failures = {
        str(repetition.get("state_failure", {}).get("type"))
        for repetition in measurement.get("repetitions") or []
        if repetition.get("state_failure")
    }
    if "STATE_TRAVERSAL_WORK_LIMIT" in failures:
        return "STATE_TRAVERSAL_WORK_LIMIT"
    if "STATE_TRAVERSAL_RECURSION_LIMIT" in failures:
        return "STATE_TRAVERSAL_RECURSION_LIMIT"
    if failures:
        return "UNSUPPORTED_REACHABLE_TYPE"
    return "MEASUREMENT_FAILED"


def metric_measurement_coverage(
    profiles_by_arm: dict[str, dict[str, dict[str, Any]]]
) -> dict[str, Any]:
    records = []
    for arm in grade.ARMS:
        profiles = profiles_by_arm[arm].values()
        for metric in ALL_DYNAMIC_METRICS:
            measured = 0
            unavailable: Counter[str] = Counter()
            for profile in profiles:
                value = (profile.get("metrics") or {}).get(metric, NOT_MEASURED)
                if value != NOT_MEASURED:
                    measured += 1
                else:
                    unavailable[measurement_unavailable_reason(profile, metric)] += 1
            total = len(profiles_by_arm[arm])
            records.append(
                {
                    "arm_id": arm,
                    "metric_name": metric,
                    "measured": measured,
                    "selected_profiles": total,
                    "unavailable": total - measured,
                    "unavailable_by_reason": dict(sorted(unavailable.items())),
                }
            )
    return {
        "unit": "selected program profiles",
        "records": records,
        "reason_definitions": MEASUREMENT_REASON_DEFINITIONS,
        "notes": [],
    }


def prepare(
    benchmark_root: Path,
    profiles_root: Path,
    language: str,
) -> tuple[list[dict[str, object]], dict[str, Any]]:
    benchmark = workbench.load_benchmark(benchmark_root)
    suffix = ".py" if language == "python" else ".cpp"
    language_directory = "python" if language == "python" else "cpp"
    profiles_by_arm = {
        arm: load_profiles(
            profiles_root / arm / language_directory / "profiles.jsonl", arm
        )
        for arm in grade.ARMS
    }
    rows = []
    exclusions: Counter[tuple[str, str, str]] = Counter()
    inclusions: Counter[tuple[str, str]] = Counter()
    unavailable_dynamic: Counter[tuple[str, str]] = Counter()
    execution_predictions: dict[str, set[str]] = defaultdict(set)
    retry_cells = 0
    profile_manifests = {}
    for arm in grade.ARMS:
        manifest = profiles_root / arm / language_directory / "manifest.json"
        profile_manifests[arm] = {
            "path": display_path(manifest),
            "sha256": sha256(manifest),
        }
    for model in benchmark.models:
        for problem in benchmark.problems:
            if problem.program.suffix != suffix:
                continue
            arm = problem.id.rsplit("/", 1)[-1]
            program_id = problem.id.rsplit("/", 1)[0]
            run_directory = benchmark.root / "runs" / model.id / Path(problem.id)
            if len(list(run_directory.glob("r*/session.jsonl"))) > 1:
                retry_cells += 1
            result = grade.grade_problem(benchmark, model, problem)
            if result.status not in ELIGIBLE_STATUSES:
                exclusions[(model.id, arm, result.status)] += 1
                continue
            record = profiles_by_arm[arm].get(program_id)
            if record is None:
                raise ValueError(f"missing profile for {program_id}/{arm}")
            if record.get("source_sha256") != sha256(problem.program):
                raise ValueError(f"profile source mismatch for {problem.id}")
            prediction_id = f"{model.id}::{problem.id}"
            inclusions[(model.id, arm)] += 1
            for metric in STATIC_METRICS:
                value = record["metrics"].get(metric, NOT_MEASURED)
                if value == NOT_MEASURED:
                    raise ValueError(f"{problem.id}: {metric} is not measured")
                rows.append(
                    {
                        "series_id": f"static::{model.id}::{arm}::{metric}",
                        "prediction_id": prediction_id,
                        "program_id": program_id,
                        "execution_id": "",
                        "model_id": model.id,
                        "arm_id": arm,
                        "arm_group": arm,
                        "scope": "static",
                        "metric_name": metric,
                        "x": format(float(value), ".17g"),
                        "y": int(bool(result.correct)),
                    }
                )
            if arm not in DYNAMIC_ARMS:
                continue
            execution = record.get("dynamic_execution") or {}
            execution_id = execution.get("execution_id")
            measured_dynamic = any(
                record["metrics"].get(metric, NOT_MEASURED) != NOT_MEASURED
                for metric in ALL_DYNAMIC_METRICS
            )
            if measured_dynamic:
                if execution.get("status") != "OK" or not execution_id:
                    raise ValueError(
                        f"{problem.id}: measured dynamic metrics have no valid "
                        "execution identity"
                    )
                execution_predictions[execution_id].add(prediction_id)
            for metric in ALL_DYNAMIC_METRICS:
                value = record["metrics"].get(metric, NOT_MEASURED)
                if value == NOT_MEASURED:
                    unavailable_dynamic[(arm, metric)] += 1
                    continue
                rows.append(
                    {
                        "series_id": f"dynamic::{model.id}::all-arms::{metric}",
                        "prediction_id": prediction_id,
                        "program_id": program_id,
                        "execution_id": execution_id,
                        "model_id": model.id,
                        "arm_id": arm,
                        "arm_group": "all-arms",
                        "scope": "dynamic",
                        "metric_name": metric,
                        "x": format(float(value), ".17g"),
                        "y": int(bool(result.correct)),
                    }
                )
    rows.sort(
        key=lambda row: (
            str(row["series_id"]),
            str(row["program_id"]),
            str(row["prediction_id"]),
        )
    )
    included_predictions = sum(inclusions.values())
    manifest = {
        "schema": "lcb-hard-v1-prediction-factor-cohort-v4",
        "benchmark": benchmark.root.name,
        "language": language,
        "scope": "static-and-dynamic",
        "metrics": {
            "static": list(STATIC_METRICS),
            "dynamic": list(ALL_DYNAMIC_METRICS),
        },
        "arm_labels": {arm: arm for arm in grade.ARMS},
        "model_ids": [model.id for model in benchmark.models],
        "selection_policy": (
            "selected-attempts.json pins corrected reasoning-condition "
            "recollections; every other cell uses the first completed assistant "
            "response in rNNN order; retries are not independent predictions"
        ),
        "eligibility": {
            "included": sorted(ELIGIBLE_STATUSES),
            "excluded": ["no_response", "not_run"],
        },
        "included_prediction_count": included_predictions,
        "point_count": len(rows),
        "retry_cells_deduplicated": retry_cells,
        "included_by_model_arm": {
            f"{model}::{arm}": count
            for (model, arm), count in sorted(inclusions.items())
        },
        "excluded_by_model_arm_status": {
            f"{model}::{arm}::{status}": count
            for (model, arm, status), count in sorted(exclusions.items())
        },
        "unavailable_dynamic_prediction_points_by_arm_metric": {
            f"{arm}::{metric}": count
            for (arm, metric), count in sorted(unavailable_dynamic.items())
        },
        "metric_measurement_coverage": metric_measurement_coverage(profiles_by_arm),
        "dynamic_pooling": {
            "arm_group": "all-arms",
            "arms": list(DYNAMIC_ARMS),
            "prediction_count": sum(
                len(predictions) for predictions in execution_predictions.values()
            ),
            "distinct_execution_id_count": len(execution_predictions),
            "shared_execution_id_count": sum(
                len(predictions) > 1
                for predictions in execution_predictions.values()
            ),
            "predictions_backed_by_shared_execution_ids": sum(
                len(predictions)
                for predictions in execution_predictions.values()
                if len(predictions) > 1
            ),
            "dependence_disclosure": (
                "Predictions are clustered by program; the row-level test does "
                "not model within-program dependence."
            ),
        },
        "provenance": {
            "cases": {
                "path": display_path(benchmark.root / "cases.json"),
                "sha256": sha256(benchmark.root / "cases.json"),
            },
            "workbench_config": {
                "path": display_path(benchmark.root / "workbench.toml"),
                "sha256": sha256(benchmark.root / "workbench.toml"),
            },
            "grader": {
                "path": display_path(benchmark.root / "grade.py"),
                "sha256": sha256(benchmark.root / "grade.py"),
            },
            "profile_manifests": profile_manifests,
        },
    }
    return rows, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark", type=Path, default=ROOT / "experiments/lcb_hard_v1_cpp"
    )
    parser.add_argument(
        "--profiles-root",
        type=Path,
        default=ROOT
        / "experiments/lcb_hard_v1_cpp/measurements/program-complexity",
    )
    parser.add_argument("--language", choices=("python", "cpp"), default="cpp")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        rows, manifest = prepare(
            arguments.benchmark.resolve(),
            arguments.profiles_root.resolve(),
            arguments.language,
        )
    except (OSError, ValueError, workbench.WorkbenchError) as error:
        parser.error(str(error))
    atomic_write(arguments.output, csv_content(rows))
    manifest["points_sha256"] = hashlib.sha256(
        csv_content(rows).encode("utf-8")
    ).hexdigest()
    atomic_write(arguments.manifest, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(
        f"Prepared {manifest['point_count']} points from "
        f"{manifest['included_prediction_count']} predictions"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
