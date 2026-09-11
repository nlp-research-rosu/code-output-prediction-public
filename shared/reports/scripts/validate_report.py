#!/usr/bin/env python3
"""Validate a benchmark analysis README against upstream machine artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

RETAINED_METRICS = {
    "Omega_CC",
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
}
METRIC_DEFINITIONS_PATH = (
    Path(__file__).resolve().parents[3] / "shared/metrics/README.md"
)
REQUIRED_COLUMNS = (
    "Metric",
    "Model",
    "Arm group",
    "theta_obs",
    "p",
    "Correct",
    "Wrong",
    "n",
)
THETA_TOLERANCE = 0.005
REQUIRED_FIELD_DEFINITIONS = (
    "`theta_obs`:",
    "`p`:",
    "`correct` / `wrong`:",
    "`n`:",
)


class ValidationError(ValueError):
    pass


@dataclass(frozen=True)
class Association:
    metric: str
    model: str
    group: str
    theta: str
    p_value: str
    successes: int
    failures: int
    total: int


def significant_associations(path: Path, scope: str) -> list[Association]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    result = []
    for row in rows:
        if row["scope"] != scope or row["status"] != "OK":
            continue
        if float(row["theta_obs"]) <= 0.5 or float(row["p_value"]) >= 0.05:
            continue
        result.append(
            Association(
                row["metric_name"],
                row["model_id"],
                row["arm_group"],
                row["theta_obs"],
                row["p_value"],
                int(row["n_success"]),
                int(row["n_failure"]),
                int(row["n_total"]),
            )
        )
    return result


def parse_markdown_table(report: str) -> list[Association]:
    lines = [line.strip() for line in report.splitlines() if line.strip().startswith("|")]
    if len(lines) < 2:
        raise ValidationError("supported-associations table is missing")
    headers = tuple(cell.strip() for cell in lines[0].strip("|").split("|"))
    if headers != REQUIRED_COLUMNS:
        raise ValidationError(
            "supported-associations columns must be: " + ", ".join(REQUIRED_COLUMNS)
        )
    result = []
    for line in lines[2:]:
        cells = [cell.strip().strip("`") for cell in line.strip("|").split("|")]
        if len(cells) != len(REQUIRED_COLUMNS):
            raise ValidationError("malformed supported-associations row")
        try:
            result.append(
                Association(
                    cells[0],
                    cells[1],
                    cells[2],
                    cells[3],
                    cells[4],
                    int(cells[5]),
                    int(cells[6]),
                    int(cells[7]),
                )
            )
        except ValueError as error:
            raise ValidationError("invalid supported-associations value") from error
    return result


def normalized(value: Association) -> tuple[object, ...]:
    """Key an association for comparison.

    theta is rounded because the audit table shows two decimals: requiring the
    report to echo full float precision is what forced unreadable digits like
    9.99900009999e-05 into human-facing documents.
    """
    return (
        value.metric,
        value.model,
        value.group,
        round(float(value.theta), 2),
        value.successes,
        value.failures,
        value.total,
    )


def validate_links(report_path: Path, report: str) -> None:
    for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", report):
        target = target.strip().strip("<>")
        if target.startswith(("http://", "https://", "#")):
            continue
        path_text = target.split("#", 1)[0]
        if path_text and not (report_path.parent / path_text).resolve().exists():
            raise ValidationError(f"linked artifact does not exist: {target}")


def validate_metric_definitions_link(report_path: Path, report: str) -> None:
    for target in re.findall(r"\[[^]]*\]\(([^)]+)\)", report):
        path_text = target.strip().strip("<>").split("#", 1)[0]
        if (report_path.parent / path_text).resolve() == METRIC_DEFINITIONS_PATH:
            return
    raise ValidationError("report does not link the shared metric definitions")


def validate_field_definitions(report: str) -> None:
    lowered = report.lower()
    for marker in REQUIRED_FIELD_DEFINITIONS:
        if marker not in lowered:
            raise ValidationError(
                f"supported-associations table lacks a column definition: {marker}"
            )


def validate_chart_data(
    paths: Sequence[Path], expected: Sequence[Association]
) -> None:
    available = set()
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            available.update(
                (row["metric_name"], row["model_id"], row["arm_group"])
                for row in csv.DictReader(handle)
            )
    missing = [
        (item.metric, item.model, item.group)
        for item in expected
        if (item.metric, item.model, item.group) not in available
    ]
    if missing:
        raise ValidationError(f"chart data lacks detected series: {missing}")


def validate(
    report_path: Path,
    associations_path: Path,
    primary_results_path: Path,
    pooled_results_path: Path,
    chart_data_path: Path,
    chart_manifest_path: Path,
    logistic_chart_data_path: Path | None = None,
) -> dict[str, int]:
    report = report_path.read_text(encoding="utf-8")
    associations = associations_path.read_text(encoding="utf-8")
    expected = [
        *significant_associations(primary_results_path, "static"),
        *significant_associations(pooled_results_path, "dynamic"),
    ]
    if sorted(map(normalized, expected)) != sorted(
        map(normalized, parse_markdown_table(associations))
    ):
        raise ValidationError(
            "supported-associations table differs from static plus dynamic results"
        )
    if not any(
        str(associations_path.name) in target
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", report)
    ):
        raise ValidationError("report does not link the supported-associations table")
    present_metrics = set()
    for path in (primary_results_path, pooled_results_path):
        with path.open(newline="", encoding="utf-8") as handle:
            present_metrics.update(row["metric_name"] for row in csv.DictReader(handle))
    for metric in sorted(present_metrics):
        if metric not in RETAINED_METRICS:
            raise ValidationError(f"unknown retained metric: {metric}")
    if not any(metric in report for metric in present_metrics):
        raise ValidationError("report names no measured factor")
    validate_metric_definitions_link(report_path, report)
    lowered = report.lower()
    for phrase in (
        "unadjusted",
        "not causation",
        "not proof of no relationship",
        "measurement coverage",
        "same language adapter",
    ):
        if phrase not in lowered:
            raise ValidationError(f"required limitation is missing: {phrase}")
    validate_field_definitions(associations)
    if re.search(r"not_measured[^\n]{0,50}(?:=|is|as)\s*0\b", lowered):
        raise ValidationError("report treats NOT_MEASURED as zero")
    validate_links(report_path, report)
    chart_paths = [chart_data_path]
    if logistic_chart_data_path is not None:
        chart_paths.append(logistic_chart_data_path)
    validate_chart_data(chart_paths, expected)
    manifest = json.loads(chart_manifest_path.read_text(encoding="utf-8"))
    actual_hash = hashlib.sha256(chart_data_path.read_bytes()).hexdigest()
    if manifest.get("chart_data_sha256") != actual_hash:
        raise ValidationError("chart-data.csv hash does not match chart manifest")
    if logistic_chart_data_path is not None:
        logistic_hash = hashlib.sha256(logistic_chart_data_path.read_bytes()).hexdigest()
        if manifest.get("logistic_chart_data_sha256") != logistic_hash:
            raise ValidationError(
                "logistic-chart-data.csv hash does not match chart manifest"
            )
    return {"supported_associations": len(expected), "metrics": len(present_metrics)}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--report", type=Path, required=True)
    result.add_argument("--associations", type=Path, required=True)
    result.add_argument("--primary-results", type=Path, required=True)
    result.add_argument("--pooled-results", type=Path, required=True)
    result.add_argument("--chart-data", type=Path, required=True)
    result.add_argument("--logistic-chart-data", type=Path)
    result.add_argument("--chart-manifest", type=Path, required=True)
    return result


def main(argv: Sequence[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    try:
        summary = validate(
            arguments.report,
            arguments.associations,
            arguments.primary_results,
            arguments.pooled_results,
            arguments.chart_data,
            arguments.chart_manifest,
            arguments.logistic_chart_data,
        )
    except (OSError, KeyError, json.JSONDecodeError, ValidationError) as error:
        raise SystemExit(str(error)) from error
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
