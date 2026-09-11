#!/usr/bin/env python3
"""Prepare canonical dynamic prediction-factor points for this experiment."""

from __future__ import annotations

import csv
from collections import Counter
import hashlib
from io import StringIO
import json
from pathlib import Path


EXPERIMENT = Path(__file__).resolve().parents[1]
RESULTS = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/graded-predictions.json"
)
CASES = EXPERIMENT / "cases.json"
NORMALIZED_MEASUREMENTS = (
    EXPERIMENT / "measurements/program-complexity/normalized-profiles.csv"
)
OUTPUT = EXPERIMENT / "reports/prediction-factor-analysis/data/source-points.csv"
MANIFEST = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/cohort-manifest.json"
)
COHORT_ACCURACY_CSV = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/cohort-accuracy.csv"
)
COHORT_ACCURACY_MD = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/cohort-accuracy.md"
)
MODELS = (
    "gpt-5.6-sol-high",
    "gpt-5.6-sol-off",
    "glm-5.3-high",
    "deepseek-v4-pro-0813-off",
    "deepseek-v4-pro-0813-high",
    "qwen3.8-27b-off",
    "qwen3.8-27b-high",
)
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
DYNAMIC_ARMS = ARMS
STATIC_METRICS = (
    "Omega_CC",
)
DYNAMIC_METRICS = (
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
ELIGIBLE_STATUSES = {
    "correct_valid",
    "correct_invalid",
    "wrong_valid",
    "wrong_invalid",
}
FIELDS = (
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
COHORTS = ("lower", "medium", "higher")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def numeric_measurement_value(row: dict[str, str]) -> str | None:
    """Return any canonical numeric measurement value."""
    if row["status"] == "NOT_MEASURED":
        return None
    expected_relation = {"MEASURED": "=", "LOWER_BOUND": ">="}.get(row["status"])
    if expected_relation is None:
        return None
    if row["value_relation"] != expected_relation or row["value"] == "":
        raise ValueError(f"Malformed numeric measurement row: {row}")
    return str(int(row["value"]))


def write_cohort_accuracy(results: dict[tuple[str, str, str], dict]) -> None:
    case_document = json.loads(CASES.read_text(encoding="utf-8"))
    cohorts = {row["case_id"]: row["cohort"] for row in case_document["cases"]}
    expected_cases = {f"problem-{case:02d}" for case in range(1, 31)}
    if set(cohorts) != expected_cases:
        raise ValueError("Case cohort map does not match the 30 selected problems")

    rows = []
    for model in MODELS:
        for cohort in COHORTS:
            cohort_cases = {case for case, label in cohorts.items() if label == cohort}
            for arm in (*ARMS, "all-arms"):
                selected = [
                    result
                    for (candidate_model, case, candidate_arm), result in results.items()
                    if candidate_model == model
                    and case in cohort_cases
                    and (arm == "all-arms" or candidate_arm == arm)
                    and result["status"] in ELIGIBLE_STATUSES
                ]
                correct = sum(bool(result["semantic_correct"]) for result in selected)
                total = len(selected)
                rows.append(
                    {
                        "model_id": model,
                        "cohort": cohort,
                        "arm_id": arm,
                        "correct": correct,
                        "eligible": total,
                        "accuracy": f"{correct / total:.6f}" if total else "",
                    }
                )

    COHORT_ACCURACY_CSV.parent.mkdir(parents=True, exist_ok=True)
    with COHORT_ACCURACY_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("model_id", "cohort", "arm_id", "correct", "eligible", "accuracy"),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)

    lookup = {(row["model_id"], row["cohort"], row["arm_id"]): row for row in rows}
    lines = [
        "# Accuracy by preselected runtime-complexity cohort",
        "",
        "Each cohort contains 10 problems. Cells show `correct/eligible (accuracy)`; "
        "the cohort labels were fixed before model outcomes were inspected.",
        "",
        "| Model | Cohort | " + " | ".join((*ARMS, "overall")) + " |",
        "| --- | --- | " + " | ".join(["---:"] * 5) + " |",
    ]
    for model in MODELS:
        for cohort in COHORTS:
            cells = []
            for arm in (*ARMS, "all-arms"):
                row = lookup[(model, cohort, arm)]
                cells.append(
                    f"{row['correct']}/{row['eligible']} ({float(row['accuracy']):.1%})"
                )
            lines.append(f"| `{model}` | {cohort} | " + " | ".join(cells) + " |")
    COHORT_ACCURACY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    result_document = json.loads(RESULTS.read_text(encoding="utf-8"))
    results = {
        (row["model"], row["case_id"], row["arm_id"]): row
        for row in result_document["rows"]
    }
    if len(results) != len(result_document["rows"]):
        raise ValueError("Duplicate result cell")
    expected = {
        (model, f"problem-{case:02d}", arm)
        for model in MODELS
        for case in range(1, 31)
        for arm in ARMS
    }
    if set(results) != expected:
        raise ValueError(
            f"Result matrix mismatch: missing={len(expected - set(results))}, "
            f"extra={len(set(results) - expected)}"
        )
    measurements: dict[tuple[str, str, str], dict[str, str]] = {}
    with NORMALIZED_MEASUREMENTS.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = (row["problem"], row["arm"], row["metric"])
            if key in measurements:
                raise ValueError(f"Duplicate measurement: {key}")
            measurements[key] = row
    expected_measurements = {
        (case, arm, metric)
        for _, case, arm in expected
        for metric in (*STATIC_METRICS, *DYNAMIC_METRICS)
    }
    if set(measurements) != expected_measurements:
        raise ValueError("Normalized measurements do not match the 120 arm profiles")

    write_cohort_accuracy(results)

    points = []
    excluded = 0
    included_by_model_arm: dict[tuple[str, str], int] = {}
    excluded_by_model_arm_status: dict[tuple[str, str, str], int] = {}
    for model, case, arm in sorted(expected):
        result = results[(model, case, arm)]
        if result["status"] not in ELIGIBLE_STATUSES:
            excluded += 1
            key = (model, arm, str(result["status"]))
            excluded_by_model_arm_status[key] = (
                excluded_by_model_arm_status.get(key, 0) + 1
            )
            continue
        key = (model, arm)
        included_by_model_arm[key] = included_by_model_arm.get(key, 0) + 1
        prediction_id = result["prediction_id"]
        if arm in DYNAMIC_ARMS:
            for metric in DYNAMIC_METRICS:
                measurement = measurements[(case, arm, metric)]
                value = numeric_measurement_value(measurement)
                if value is None:
                    continue
                points.append(
                    {
                        "series_id": f"dynamic::{model}::all-arms::{metric}",
                        "prediction_id": prediction_id,
                        "program_id": case,
                        "execution_id": measurement["execution_id"],
                        "model_id": model,
                        "arm_id": arm,
                        "arm_group": "all-arms",
                        "scope": "dynamic",
                        "metric_name": metric,
                        "x": value,
                        "y": int(bool(result["semantic_correct"])),
                    }
                )
        for metric in STATIC_METRICS:
            measurement = measurements[(case, arm, metric)]
            value = numeric_measurement_value(measurement)
            if value is None:
                raise ValueError(f"Static metric is unavailable: {(case, arm, metric)}")
            points.append(
                {
                    "series_id": f"static::{model}::{arm}::{metric}",
                    "prediction_id": prediction_id,
                    "program_id": case,
                    "execution_id": "",
                    "model_id": model,
                    "arm_id": arm,
                    "arm_group": arm,
                    "scope": "static",
                    "metric_name": metric,
                    "x": value,
                    "y": int(bool(result["semantic_correct"])),
                }
            )
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(points)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output.getvalue(), encoding="utf-8", newline="")
    measurement_coverage = []
    for arm in ARMS:
        arm_measurements = [
            measurement
            for (case_id, arm_id, metric_name), measurement in measurements.items()
            if arm_id == arm and metric_name in DYNAMIC_METRICS
        ]
        for metric in DYNAMIC_METRICS:
            metric_measurements = [
                measurement
                for measurement in arm_measurements
                if measurement["metric"] == metric
            ]
            statuses = Counter(row["status"] for row in metric_measurements)
            unavailable_by_reason = Counter()
            for measurement in metric_measurements:
                if measurement["status"] == "MEASURED":
                    continue
                reason = measurement["not_measured_reason"] or measurement["status"]
                unavailable_by_reason[reason] += 1
            measured = statuses["MEASURED"]
            lower_bound = statuses["LOWER_BOUND"]
            total = len(metric_measurements)
            measurement_coverage.append(
                {
                    "arm_id": arm,
                    "metric_name": metric,
                    "measured": measured,
                    "lower_bound": lower_bound,
                    "usable": measured + lower_bound,
                    "selected_profiles": total,
                    "unavailable": total - measured - lower_bound,
                    "unavailable_by_reason": dict(sorted(unavailable_by_reason.items())),
                }
            )
    MANIFEST.write_text(
        json.dumps(
            {
                "schema": "networkx-state-prediction-factor-cohort-v1",
                "cases": 30,
                "arms": list(ARMS),
                "models": list(MODELS),
                "arm_labels": {arm: arm for arm in ARMS},
                "included_by_model_arm": {
                    f"{model}::{arm}": count
                    for (model, arm), count in sorted(included_by_model_arm.items())
                },
                "excluded_by_model_arm_status": {
                    f"{model}::{arm}::{status}": count
                    for (model, arm, status), count in sorted(
                        excluded_by_model_arm_status.items()
                    )
                },
                "eligible_predictions": len({row["prediction_id"] for row in points}),
                "excluded_predictions": excluded,
                "static_metrics": list(STATIC_METRICS),
                "dynamic_metrics": list(DYNAMIC_METRICS),
                "dynamic_arms": list(DYNAMIC_ARMS),
                "dynamic_pooling": {
                    "arm_group": "all-arms",
                    "arms": list(DYNAMIC_ARMS),
                },
                "metric_measurement_coverage": {
                    "unit": "selected program profiles",
                    "records": measurement_coverage,
                    "reason_definitions": {
                        "NOT_MEASURED": "The adapter did not produce a numeric value.",
                        "NOT_REQUESTED": "The metric was not requested for this profile.",
                    },
                    "notes": [
                        "Coverage and unavailable causes come from normalized measurement statuses; unavailable status tokens are never parsed as values."
                    ],
                },
                "series": {
                    "static": "model x arm x static metric",
                    "dynamic": "model x dynamic metric, pooled across the four canonical arms",
                },
                "independence_limitation": "several executions can come from one problem; the row-level permutation test does not model within-problem dependence",
                "inputs": {
                    "results_sha256": sha256(RESULTS),
                    "cases_sha256": sha256(CASES),
                    "normalized_measurements_sha256": sha256(NORMALIZED_MEASUREMENTS),
                },
                "outputs": {
                    "cohort_accuracy_csv_sha256": sha256(COHORT_ACCURACY_CSV),
                    "cohort_accuracy_md_sha256": sha256(COHORT_ACCURACY_MD),
                    "source_points_sha256": sha256(OUTPUT),
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Prepared {len(points)} points across {len(set(row['series_id'] for row in points))} series")


if __name__ == "__main__":
    main()
