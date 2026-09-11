#!/usr/bin/env python3
"""Describe existing chart bins without recalculating them."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Sequence


def pattern(accuracies: Sequence[float]) -> str:
    if len(accuracies) < 2:
        return "insufficient bin variation"
    if all(value == accuracies[0] for value in accuracies):
        return "flat"
    if all(left >= right for left, right in zip(accuracies, accuracies[1:])):
        return "monotone non-increasing"
    if all(left <= right for left, right in zip(accuracies, accuracies[1:])):
        return "monotone non-decreasing"
    return "mixed"


def selected_series(primary: Path, pooled: Path) -> dict[str, dict[str, str]]:
    selected = {}
    for path, include_all_dynamic in ((primary, False), (pooled, True)):
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                significant = (
                    row["status"] == "OK"
                    and float(row["theta_obs"]) > 0.5
                    and float(row["p_value"]) < 0.05
                )
                if (row["scope"] == "static" and significant) or (
                    include_all_dynamic and row["scope"] == "dynamic"
                ):
                    selected[row["series_id"]] = row
    return selected


def describe(
    primary: Path,
    pooled: Path,
    chart_data: Path,
    logistic_chart_data: Path | None = None,
) -> list[dict[str, object]]:
    selected = selected_series(primary, pooled)
    bins: dict[str, list[dict[str, str]]] = defaultdict(list)
    measures: dict[str, str] = {}
    with chart_data.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["series_id"] in selected:
                bins[row["series_id"]].append(row)
                measures[row["series_id"]] = "accuracy"
    if logistic_chart_data is not None:
        identities = {
            (row["metric_name"], row["model_id"], row["arm_group"]): series_id
            for series_id, row in selected.items()
        }
        with logistic_chart_data.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                series_id = identities.get(
                    (row["metric_name"], row["model_id"], row["arm_group"])
                )
                if series_id is not None:
                    bins[series_id].append(row)
                    measures[series_id] = "wrong_rate"
    missing = sorted(set(selected) - set(bins))
    if missing:
        raise ValueError(f"chart data lacks selected series: {missing}")
    summaries = []
    for series_id, result in sorted(
        selected.items(),
        key=lambda item: (
            item[1]["scope"],
            item[1]["metric_name"],
            item[1]["arm_group"],
            item[1]["model_id"],
        ),
    ):
        ordered = sorted(bins[series_id], key=lambda row: int(row["bin_index"]))
        measure = measures[series_id]
        values = [float(row[measure]) for row in ordered]
        low = ordered[0]
        high = ordered[-1]
        summaries.append(
            {
                "series_id": series_id,
                "scope": result["scope"],
                "metric_name": result["metric_name"],
                "model_id": result["model_id"],
                "arm_group": result["arm_group"],
                "theta_obs": result["theta_obs"],
                "p_value": result["p_value"],
                "status": result["status"],
                "bin_measure": measure,
                "pattern": pattern(values),
                "endpoint_direction_consistent_with_failure_at_larger_values": (
                    values[-1] <= values[0]
                    if measure == "accuracy" and len(values) >= 2
                    else values[-1] >= values[0]
                    if len(values) >= 2
                    else None
                ),
                "lowest_x_bin": low,
                "highest_x_bin": high,
            }
        )
    return summaries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-results", type=Path, required=True)
    parser.add_argument("--pooled-results", type=Path, required=True)
    parser.add_argument("--chart-data", type=Path, required=True)
    parser.add_argument("--logistic-chart-data", type=Path)
    arguments = parser.parse_args()
    try:
        summaries = describe(
            arguments.primary_results,
            arguments.pooled_results,
            arguments.chart_data,
            arguments.logistic_chart_data,
        )
    except (OSError, KeyError, ValueError) as error:
        parser.error(str(error))
    print(json.dumps(summaries, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
