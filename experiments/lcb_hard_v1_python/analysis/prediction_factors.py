#!/usr/bin/env python3
"""Prepare canonical prediction-factor points for lcb_hard_v1_python."""

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
from experiments.lcb_hard_v1_python import grade  # noqa: E402
from experiments.lcb_hard_v1_python.analysis.program_complexity import (  # noqa: E402
    ALL_DYNAMIC_METRICS,
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
    "INVALID_ORACLE_MISMATCH": (
        "The natural execution did not match the committed oracle."
    ),
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


def load_measurements(
    path: Path, benchmark_name: str, language: str
) -> dict[tuple[str, str, str], dict[str, str]]:
    records: dict[tuple[str, str, str], dict[str, str]] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {
            "benchmark",
            "problem",
            "arm",
            "language",
            "source_sha256",
            "input_sha256",
            "execution_id",
            "metric",
            "value",
            "value_relation",
            "status",
            "not_measured_reason",
        }
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"{path}: normalized measurement schema is incomplete")
        for line, row in enumerate(reader, 2):
            if row["benchmark"] != benchmark_name:
                raise ValueError(f"{path}:{line}: benchmark mismatch")
            if row["language"] != language:
                raise ValueError(f"{path}:{line}: language mismatch")
            key = (row["problem"], row["arm"], row["metric"])
            if key in records:
                raise ValueError(f"{path}:{line}: duplicate measurement {key}")
            normalized_measurement_value(row)
            records[key] = row
    return records


def csv_content(rows: Iterable[dict[str, object]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=POINT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def measurement_unavailable_reason(row: dict[str, str]) -> str:
    if row["status"] == "NOT_REQUESTED":
        return "ADAPTER_NOT_RUN"
    failure = row["not_measured_reason"]
    if "stdout did not match ground-output.txt" in failure:
        return "INVALID_ORACLE_MISMATCH"
    if "timed out" in failure:
        return "TRACE_TIMEOUT"
    if "differed across repetitions" in failure:
        return "NONDETERMINISTIC_TRACE"
    if "STATE_TRAVERSAL_WORK_LIMIT" in failure:
        return "STATE_TRAVERSAL_WORK_LIMIT"
    if "STATE_TRAVERSAL_RECURSION_LIMIT" in failure:
        return "STATE_TRAVERSAL_RECURSION_LIMIT"
    if "unsupported" in failure.lower():
        return "UNSUPPORTED_REACHABLE_TYPE"
    return "MEASUREMENT_FAILED"


def metric_measurement_coverage(
    measurements: dict[tuple[str, str, str], dict[str, str]],
    problem_ids: set[str],
) -> dict[str, Any]:
    records = []
    for arm in grade.ARMS:
        for metric in ALL_DYNAMIC_METRICS:
            measured = 0
            unavailable: Counter[str] = Counter()
            for problem_id in problem_ids:
                row = measurements[(problem_id, arm, metric)]
                if normalized_measurement_value(row) is not None:
                    measured += 1
                else:
                    unavailable[measurement_unavailable_reason(row)] += 1
            total = len(problem_ids)
            records.append(
                {
                    "arm_id": arm,
                    "metric_name": metric,
                    "measured": measured,
                    "usable": measured,
                    "selected_profiles": total,
                    "unavailable": total - measured,
                    "unavailable_by_reason": dict(sorted(unavailable.items())),
                }
            )
    return {
        "unit": "selected program profiles",
        "records": records,
        "reason_definitions": MEASUREMENT_REASON_DEFINITIONS,
    }


def normalized_measurement_value(row: dict[str, str]) -> int | None:
    """Read only canonical equality measurements used by this experiment."""
    status = row["status"]
    if status == "MEASURED":
        if row["value_relation"] != "=" or row["value"] == "":
            raise ValueError(f"malformed equality measurement: {row}")
        return int(row["value"])
    if status == "LOWER_BOUND":
        raise ValueError(
            "lcb_hard_v1_python recovered values must be normalized as "
            "MEASURED equalities before analysis"
        )
    if status not in {"NOT_MEASURED", "NOT_REQUESTED"}:
        raise ValueError(f"unknown normalized measurement status: {status}")
    if row["value"] or row["value_relation"] or not row["not_measured_reason"]:
        raise ValueError(f"malformed unavailable measurement: {row}")
    return None


def prepare(
    benchmark_root: Path,
    normalized_profiles: Path,
    language: str,
) -> tuple[list[dict[str, object]], dict[str, Any]]:
    benchmark = workbench.load_benchmark(benchmark_root)
    suffix = ".py" if language == "python" else ".cpp"
    measurements = load_measurements(
        normalized_profiles, benchmark.root.name, language
    )
    normalized_manifest_path = normalized_profiles.with_name(
        "normalized-profiles-manifest.json"
    )
    normalized_config_path = normalized_profiles.with_name(
        "normalized-profiles-config.json"
    )
    normalized_manifest = json.loads(
        normalized_manifest_path.read_text(encoding="utf-8")
    )
    normalized_config = json.loads(
        normalized_config_path.read_text(encoding="utf-8")
    )
    if normalized_manifest.get("numeric_recovery_policy") != "assume_equal":
        raise ValueError("normalized measurement manifest must use assume_equal")
    if normalized_config.get("numeric_recovery_policy") != "assume_equal":
        raise ValueError("normalized measurement config must use assume_equal")
    if (normalized_manifest.get("output") or {}).get("sha256") != sha256(
        normalized_profiles
    ):
        raise ValueError("normalized measurement manifest output hash mismatch")
    if (normalized_manifest.get("config") or {}).get("sha256") != sha256(
        normalized_config_path
    ):
        raise ValueError("normalized measurement manifest config hash mismatch")
    selected_problems = [
        problem for problem in benchmark.problems if problem.program.suffix == suffix
    ]
    problem_ids = {problem.id.rsplit("/", 1)[0] for problem in selected_problems}
    expected_measurements = {
        (problem.id.rsplit("/", 1)[0], problem.id.rsplit("/", 1)[-1], metric)
        for problem in selected_problems
        for metric in (*STATIC_METRICS, *ALL_DYNAMIC_METRICS)
    }
    if set(measurements) != expected_measurements:
        raise ValueError(
            "normalized measurements do not match benchmark profiles: "
            f"missing={len(expected_measurements - set(measurements))}, "
            f"extra={len(set(measurements) - expected_measurements)}"
        )
    for problem in selected_problems:
        arm = problem.id.rsplit("/", 1)[-1]
        program_id = problem.id.rsplit("/", 1)[0]
        profile_rows = [
            measurements[(program_id, arm, metric)]
            for metric in (*STATIC_METRICS, *ALL_DYNAMIC_METRICS)
        ]
        if {row["source_sha256"] for row in profile_rows} != {
            sha256(problem.program)
        }:
            raise ValueError(f"normalized source mismatch for {problem.id}")
        if len({row["input_sha256"] for row in profile_rows}) != 1:
            raise ValueError(f"normalized input identity mismatch for {problem.id}")
        if len({row["execution_id"] for row in profile_rows}) != 1:
            raise ValueError(
                f"normalized execution identity mismatch for {problem.id}"
            )
    rows = []
    exclusions: Counter[tuple[str, str, str]] = Counter()
    inclusions: Counter[tuple[str, str]] = Counter()
    unavailable_dynamic: Counter[tuple[str, str]] = Counter()
    execution_predictions: dict[str, set[str]] = defaultdict(set)
    retry_cells = 0
    for model in benchmark.models:
        for problem in selected_problems:
            arm = problem.id.rsplit("/", 1)[-1]
            program_id = problem.id.rsplit("/", 1)[0]
            run_directory = benchmark.root / "runs" / model.id / Path(problem.id)
            if len(list(run_directory.glob("r*/session.jsonl"))) > 1:
                retry_cells += 1
            result = grade.grade_problem(benchmark, model, problem)
            if result.status not in ELIGIBLE_STATUSES:
                exclusions[(model.id, arm, result.status)] += 1
                continue
            profile_measurements = {
                metric: measurements[(program_id, arm, metric)]
                for metric in (*STATIC_METRICS, *ALL_DYNAMIC_METRICS)
            }
            prediction_id = f"{model.id}::{problem.id}"
            inclusions[(model.id, arm)] += 1
            for metric in STATIC_METRICS:
                value = normalized_measurement_value(profile_measurements[metric])
                if value is None:
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
            dynamic_measurements = [
                profile_measurements[metric] for metric in ALL_DYNAMIC_METRICS
            ]
            execution_ids = {row["execution_id"] for row in dynamic_measurements}
            if len(execution_ids) != 1:
                raise ValueError(f"{problem.id}: dynamic execution identity mismatch")
            execution_id = execution_ids.pop()
            usable_dynamic = any(
                normalized_measurement_value(profile_measurements[metric]) is not None
                for metric in ALL_DYNAMIC_METRICS
            )
            if usable_dynamic:
                if not execution_id:
                    raise ValueError(
                        f"{problem.id}: usable dynamic metrics have no valid "
                        "execution identity"
                    )
                execution_predictions[execution_id].add(prediction_id)
            for metric in ALL_DYNAMIC_METRICS:
                value = normalized_measurement_value(profile_measurements[metric])
                if value is None:
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
        "schema": "lcb-hard-v1-prediction-factor-cohort-v7",
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
        "metric_measurement_coverage": metric_measurement_coverage(
            measurements, problem_ids
        ),
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
            "normalized_profiles": {
                "path": display_path(normalized_profiles),
                "sha256": sha256(normalized_profiles),
            },
            "normalized_profiles_manifest": {
                "path": display_path(normalized_manifest_path),
                "sha256": sha256(normalized_manifest_path),
            },
            "normalized_profiles_config": {
                "path": display_path(normalized_config_path),
                "sha256": sha256(normalized_config_path),
            },
            "numeric_recovery_policy": normalized_manifest[
                "numeric_recovery_policy"
            ],
        },
    }
    return rows, manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--benchmark", type=Path, default=ROOT / "experiments/lcb_hard_v1_python"
    )
    parser.add_argument(
        "--normalized-profiles",
        type=Path,
        default=ROOT
        / (
            "experiments/lcb_hard_v1_python/measurements/program-complexity/"
            "normalized-profiles.csv"
        ),
    )
    parser.add_argument("--language", choices=("python", "cpp"), default="python")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    arguments = parser.parse_args()
    try:
        rows, manifest = prepare(
            arguments.benchmark.resolve(),
            arguments.normalized_profiles.resolve(),
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
