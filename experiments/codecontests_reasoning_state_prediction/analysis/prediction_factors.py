#!/usr/bin/env python3
"""Prepare canonical prediction-factor points for CodeContests reasoning and state prediction."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import tempfile
from collections import Counter
from io import StringIO
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
DEFAULT_RESULTS = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/graded-predictions.json"
)
DEFAULT_PROFILES = EXPERIMENT / "measurements/program-complexity/profiles.json"
DEFAULT_OUTPUT = (
    EXPERIMENT / "reports/prediction-factor-analysis/data/source-points.csv"
)
DEFAULT_MANIFEST = (
    EXPERIMENT / "reports/prediction-factor-analysis/data/cohort-manifest.json"
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
ARM_LABELS = {arm: arm for arm in ARMS}
STATIC_METRICS = {
    "Omega_CC": "cyclomatic_complexity",
}
DYNAMIC_METRICS = {
    "Omega_hat_NativeTrace": "native_trace_length",
    "Omega_hat_StateSize": "state_size",
    "Omega_hat_StateLoad": "state_load",
}
EXECUTION_PROFILE_ARMS = {
    "short-trace-final": "short-trace-final",
    "long-trace-final": "long-trace-final",
    "inside-loop-state": "inside-loop-state",
    "post-loop-state": "post-loop-state",
}
ELIGIBLE_STATUSES = {
    "correct_valid",
    "correct_invalid",
    "wrong_valid",
    "wrong_invalid",
}
DYNAMIC_ADAPTER_VERSION = "clang-18.1.8-coverage-state-load-v1"


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


def csv_content(rows: Iterable[dict[str, object]]) -> str:
    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=POINT_FIELDS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def load_results(path: Path) -> list[dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    rows = document.get("rows")
    if not isinstance(rows, list):
        raise ValueError(f"{path}: expected a rows array")
    return rows


def load_profiles(path: Path) -> dict[str, dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    records = document.get("programs")
    if not isinstance(records, list):
        raise ValueError(f"{path}: expected a programs array")
    profiles = {record["problem_id"]: record for record in records}
    if len(profiles) != len(records):
        raise ValueError(f"{path}: duplicate problem_id")
    return profiles


def prepare(
    results_path: Path,
    profiles_path: Path,
) -> tuple[list[dict[str, object]], dict[str, Any]]:
    results = load_results(results_path)
    profiles = load_profiles(profiles_path)
    lookup: dict[tuple[str, str, str], dict[str, Any]] = {}
    status_counts: Counter[str] = Counter()
    for result in results:
        if result["model"] not in MODELS:
            continue
        key = (result["model"], result["problem_id"], result["arm_id"])
        if key in lookup:
            raise ValueError(f"duplicate result cell: {key}")
        lookup[key] = result
        status_counts[str(result["status"])] += 1

    expected = {
        (model, problem_id, arm)
        for model in MODELS
        for problem_id in profiles
        for arm in ARMS
    }
    missing = expected - set(lookup)
    extra = set(lookup) - expected
    if missing or extra:
        raise ValueError(
            "result matrix mismatch: "
            f"missing={sorted(missing)[:3]}, "
            f"extra={sorted(extra)[:3]}"
        )
    rows: list[dict[str, object]] = []
    reused_static_profiles: Counter[str] = Counter()
    pooled_dynamic_profiles: Counter[str] = Counter()
    excluded: Counter[tuple[str, str, str]] = Counter()
    included: Counter[tuple[str, str]] = Counter()
    for model in MODELS:
        for problem_id, profile in sorted(profiles.items()):
            arm_profiles = profile["arm_profiles"]
            for arm in ARMS:
                result = lookup.get((model, problem_id, arm))
                if result is None:
                    continue
                prediction_id = f"{model}::{problem_id}::{arm}"
                y = int(bool(result["semantic_correct"]))
                static_name = arm_profiles[arm]["static_profile"]
                static = profile["static_profiles"][static_name]
                program = EXPERIMENT / "problems" / problem_id / arm / "program.cpp"
                if sha256(program) != static["source_sha256"]:
                    raise ValueError(f"static source/profile mismatch for {problem_id}/{arm}")
                if result["status"] not in ELIGIBLE_STATUSES:
                    excluded[(model, arm, str(result["status"]))] += 1
                    continue
                included[(model, arm)] += 1
                reused_static_profiles[static_name] += 1
                for metric, field in STATIC_METRICS.items():
                    rows.append(
                        {
                            "series_id": f"static::{model}::{arm}::{metric}",
                            "prediction_id": prediction_id,
                            "program_id": problem_id,
                            "execution_id": "",
                            "model_id": model,
                            "arm_id": arm,
                            "arm_group": ARM_LABELS[arm],
                            "scope": "static",
                            "metric_name": metric,
                            "x": format(float(static[field]), ".17g"),
                            "y": y,
                        }
                    )

            for arm in DYNAMIC_ARMS:
                result = lookup.get((model, problem_id, arm))
                if result is None:
                    continue
                prediction_id = f"{model}::{problem_id}::{arm}"
                y = int(bool(result["semantic_correct"]))
                execution_profile = arm_profiles[arm]["prediction_target_profile"]
                dynamic = profile["dynamic"][execution_profile]
                source_arm = EXECUTION_PROFILE_ARMS[execution_profile]
                task = EXPERIMENT / "problems" / problem_id / source_arm
                if sha256(task / "program.cpp") != dynamic["source_sha256"]:
                    raise ValueError(
                        f"dynamic source mismatch for {problem_id}/{arm} via {execution_profile}"
                    )
                if sha256(task / "input.txt") != dynamic["input_sha256"]:
                    raise ValueError(
                        f"dynamic input mismatch for {problem_id}/{arm} via {execution_profile}"
                    )
                if result["status"] not in ELIGIBLE_STATUSES:
                    continue
                execution_id = (
                    f"{dynamic['source_sha256']}:{dynamic['input_sha256']}:"
                    f"{DYNAMIC_ADAPTER_VERSION}"
                )
                pooled_dynamic_profiles[execution_profile] += 1
                for metric, field in DYNAMIC_METRICS.items():
                    value = dynamic[field]
                    if not isinstance(value, (int, float)) or isinstance(value, bool):
                        continue
                    rows.append(
                        {
                            "series_id": f"dynamic::{model}::all-arms::{metric}",
                            "prediction_id": prediction_id,
                            "program_id": problem_id,
                            "execution_id": execution_id,
                            "model_id": model,
                            "arm_id": arm,
                            "arm_group": "all-arms",
                            "scope": "dynamic",
                            "metric_name": metric,
                            "x": str(value) if isinstance(value, int) else format(float(value), ".17g"),
                            "y": y,
                        }
                    )

    rows.sort(
        key=lambda row: (
            str(row["series_id"]),
            str(row["program_id"]),
            str(row["execution_id"]),
        )
    )
    measurement_coverage = []
    for arm in ARMS:
        for metric, field in DYNAMIC_METRICS.items():
            measured = 0
            for profile in profiles.values():
                execution_profile = profile["arm_profiles"][arm][
                    "prediction_target_profile"
                ]
                value = profile["dynamic"][execution_profile][field]
                measured += isinstance(value, (int, float)) and not isinstance(
                    value, bool
                )
            total = len(profiles)
            measurement_coverage.append(
                {
                    "arm_id": arm,
                    "metric_name": metric,
                    "measured": measured,
                    "selected_profiles": total,
                    "unavailable": total - measured,
                    "unavailable_by_reason": (
                        {} if measured == total else {"MEASUREMENT_FAILED": total - measured}
                    ),
                }
            )
    manifest = {
        "schema": "codecontests-prediction-factor-cohort-v2",
        "experiment": EXPERIMENT.name,
        "model_ids": list(MODELS),
        "arm_labels": ARM_LABELS,
        "metrics": {
            "static": list(STATIC_METRICS),
            "dynamic": list(DYNAMIC_METRICS),
        },
        "outcome_policy": {
            "eligible_statuses": sorted(ELIGIBLE_STATUSES),
            "status_counts": dict(sorted(status_counts.items())),
            "excluded_by_model_arm_status": {
                f"{model}::{arm}::{status}": count
                for (model, arm, status), count in sorted(excluded.items())
            },
            "correctness_field": "semantic_correct",
            "not_collected": [
                {
                    "model_id": model,
                    "problem_id": problem_id,
                    "arm_id": arm,
                    "reason": "corrected_task_requires_recollection",
                }
                for model, problem_id, arm in sorted(missing)
            ],
        },
        "included_by_model_arm": {
            f"{model}::{arm}": count
            for (model, arm), count in sorted(included.items())
        },
        "excluded_by_model_arm_status": {
            f"{model}::{arm}::{status}": count
            for (model, arm, status), count in sorted(excluded.items())
        },
        "static_analysis": {
            "series": "model x arm x metric",
            "source_scope": "exact byte-identical source shown in each arm",
            "profile_reuse_counts": dict(sorted(reused_static_profiles.items())),
        },
        "dynamic_analysis": {
            "series": "model x metric",
            "arm_group": "all-arms",
            "arms": list(DYNAMIC_ARMS),
            "execution_profile_arms": EXECUTION_PROFILE_ARMS,
            "pooling_policy": "pool every eligible prediction from the four canonical arms",
            "profile_counts": dict(sorted(pooled_dynamic_profiles.items())),
            "independence_limitation": "four predictions per program are analyzed as rows; the row-level permutation test does not model within-program dependence",
            "adapter_version": DYNAMIC_ADAPTER_VERSION,
        },
        "dynamic_pooling": {
            "arm_group": "all-arms",
            "arms": list(DYNAMIC_ARMS),
        },
        "metric_measurement_coverage": {
            "unit": "selected program profiles",
            "records": measurement_coverage,
            "reason_definitions": {
                "MEASUREMENT_FAILED": "The metric adapter did not produce a numeric value."
            },
            "notes": [],
        },
        "program_count": len(profiles),
        "planned_prediction_count": len(expected),
        "prediction_count": len(lookup),
        "not_collected_prediction_count": len(missing),
        "eligible_prediction_count": len(lookup) - sum(excluded.values()),
        "point_count": len(rows),
        "series_count": len({str(row["series_id"]) for row in rows}),
        "inputs": {
            "results": {
                "path": display_path(results_path),
                "sha256": sha256(results_path),
            },
            "profiles": {
                "path": display_path(profiles_path),
                "sha256": sha256(profiles_path),
            },
        },
    }
    return rows, manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--profiles", type=Path, default=DEFAULT_PROFILES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    arguments = parser.parse_args()
    rows, manifest = prepare(arguments.results, arguments.profiles)
    atomic_write(arguments.output, csv_content(rows))
    atomic_write(
        arguments.manifest,
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    print(f"Prepared {len(rows)} points across {manifest['series_count']} series")
    print(f"Wrote {arguments.output}")
    print(f"Wrote {arguments.manifest}")


if __name__ == "__main__":
    main()
