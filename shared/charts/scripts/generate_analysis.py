#!/usr/bin/env python3
"""Generate metric-accuracy charts from analyzed prediction-factor series."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import sys
import textwrap
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np


STYLE_CONTRACT = {
    "schema": "prediction-factor-chart-style-v1",
    "prediction_outcome": {
        "color": "#8b8b86",
        "marker": "circle",
        "matplotlib_marker": "o",
        "alpha": 0.45,
        "size": 18,
        "label": "prediction outcome",
    },
    "overall_accuracy": {
        "color": "#81817c",
        "dash_pattern": [3, 3],
        "linewidth": 1.4,
        "label": "overall accuracy",
    },
    "binned_accuracy": {
        "color": "#f05a28",
        "marker": "square",
        "matplotlib_marker": "s",
        "markersize": 6,
        "elinewidth": 1.4,
        "capsize": 3,
        "label": "binned accuracy + Wilson 95% CI",
    },
    "logistic_fit": {
        "color": "#2478d4",
        "linewidth": 2,
        "band_alpha": 0.16,
        "label": "logistic fit + 95% confidence band",
    },
    "statistics_annotation": {
        "placement": "panel-header",
        "color": "#555550",
        "fontsize": 7.5,
        "lines": 2,
    },
}


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
RESULT_FIELDS = (
    "series_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "theta_obs",
    "p_value",
    "n_success",
    "n_failure",
    "n_total",
    "permutations",
    "series_seed",
    "status",
)
CHART_DATA_FIELDS = (
    "series_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "bin_index",
    "x",
    "accuracy",
    "wilson_low",
    "wilson_high",
    "n_success",
    "n_failure",
    "n_total",
)
LOGISTIC_POINT_FIELDS = (
    "regression_id",
    "prediction_id",
    "program_id",
    "execution_id",
    "model_id",
    "arm_id",
    "arm_group",
    "scope",
    "metric_name",
    "x",
    "wrong",
)
LOGISTIC_RESULT_FIELDS = (
    "regression_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "included_arms",
    "n",
    "n_wrong",
    "beta0",
    "beta1",
    "se_beta1",
    "odds_ratio",
    "ci_low",
    "ci_high",
    "p_value",
    "status",
)
LOGISTIC_CURVE_FIELDS = (
    "regression_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "grid_index",
    "x",
    "p_wrong",
    "ci_low",
    "ci_high",
)
LOGISTIC_CHART_DATA_FIELDS = (
    "regression_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "bin_index",
    "x",
    "wrong_rate",
    "wilson_low",
    "wilson_high",
    "n_wrong",
    "n_correct",
    "n_total",
)
Z_95 = 1.959963984540054
CANONICAL_ARMS = {
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
}


class AnalysisError(ValueError):
    pass


@dataclass(frozen=True)
class Point:
    series_id: str
    prediction_id: str
    program_id: str
    execution_id: str
    model_id: str
    arm_id: str
    arm_group: str
    scope: str
    metric_name: str
    x: float
    y: int


@dataclass(frozen=True)
class SeriesResult:
    series_id: str
    model_id: str
    arm_group: str
    scope: str
    metric_name: str
    theta_obs: float | None
    p_value: float | None
    n_success: int
    n_failure: int
    n_total: int
    permutations: int
    series_seed: int
    status: str


@dataclass(frozen=True)
class LogisticPoint:
    regression_id: str
    prediction_id: str
    program_id: str
    execution_id: str
    model_id: str
    arm_id: str
    arm_group: str
    scope: str
    metric_name: str
    x: float
    wrong: int


@dataclass(frozen=True)
class LogisticResult:
    regression_id: str
    model_id: str
    arm_group: str
    scope: str
    metric_name: str
    included_arms: str
    n: int
    n_wrong: int
    odds_ratio: float | None
    ci_low: float | None
    ci_high: float | None
    p_value: float | None
    status: str


@dataclass(frozen=True)
class LogisticCurvePoint:
    regression_id: str
    model_id: str
    arm_group: str
    scope: str
    metric_name: str
    grid_index: int
    x: float
    p_wrong: float
    ci_low: float
    ci_high: float


def require_text(row: dict[str, str], field: str, line: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise AnalysisError(f"line {line}: {field} must not be empty")
    return value


def parse_float(value: str, field: str, line: int) -> float:
    try:
        number = float(value)
    except ValueError as error:
        raise AnalysisError(f"line {line}: {field} must be numeric") from error
    if not math.isfinite(number):
        raise AnalysisError(f"line {line}: {field} must be finite")
    return number


def parse_optional_float(value: str, field: str, line: int) -> float | None:
    return None if not value.strip() else parse_float(value, field, line)


def parse_nonnegative_int(value: str, field: str, line: int) -> int:
    try:
        number = int(value)
    except ValueError as error:
        raise AnalysisError(f"line {line}: {field} must be an integer") from error
    if number < 0:
        raise AnalysisError(f"line {line}: {field} must be nonnegative")
    return number


def read_rows(path: Path, fields: Sequence[str]) -> list[tuple[int, dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise AnalysisError(f"{path}: missing CSV header")
        missing = [field for field in fields if field not in reader.fieldnames]
        if missing:
            raise AnalysisError(f"{path}: missing fields: {', '.join(missing)}")
        return [(line, row) for line, row in enumerate(reader, start=2)]


def load_points(path: Path) -> list[Point]:
    points = []
    for line, row in read_rows(path, POINT_FIELDS):
        scope = require_text(row, "scope", line)
        if scope not in {"static", "dynamic"}:
            raise AnalysisError(f"line {line}: scope must be static or dynamic")
        execution_id = (row.get("execution_id") or "").strip()
        if scope == "dynamic" and not execution_id:
            raise AnalysisError(f"line {line}: dynamic point needs execution_id")
        arm_id = require_text(row, "arm_id", line)
        if arm_id not in CANONICAL_ARMS:
            raise AnalysisError(
                f"line {line}: chart point uses non-canonical arm {arm_id!r}"
            )
        y = require_text(row, "y", line)
        if y not in {"0", "1"}:
            raise AnalysisError(f"line {line}: y must be 0 or 1")
        points.append(
            Point(
                series_id=require_text(row, "series_id", line),
                prediction_id=require_text(row, "prediction_id", line),
                program_id=require_text(row, "program_id", line),
                execution_id=execution_id,
                model_id=require_text(row, "model_id", line),
                arm_id=arm_id,
                arm_group=require_text(row, "arm_group", line),
                scope=scope,
                metric_name=require_text(row, "metric_name", line),
                x=parse_float(row["x"], "x", line),
                y=int(y),
            )
        )
    if not points:
        raise AnalysisError("points CSV contains no points")
    return points


def load_results(path: Path) -> dict[str, SeriesResult]:
    results = {}
    for line, row in read_rows(path, RESULT_FIELDS):
        result = SeriesResult(
            series_id=require_text(row, "series_id", line),
            model_id=require_text(row, "model_id", line),
            arm_group=require_text(row, "arm_group", line),
            scope=require_text(row, "scope", line),
            metric_name=require_text(row, "metric_name", line),
            theta_obs=parse_optional_float(row["theta_obs"], "theta_obs", line),
            p_value=parse_optional_float(row["p_value"], "p_value", line),
            n_success=parse_nonnegative_int(row["n_success"], "n_success", line),
            n_failure=parse_nonnegative_int(row["n_failure"], "n_failure", line),
            n_total=parse_nonnegative_int(row["n_total"], "n_total", line),
            permutations=parse_nonnegative_int(
                row["permutations"], "permutations", line
            ),
            series_seed=parse_nonnegative_int(row["series_seed"], "series_seed", line),
            status=require_text(row, "status", line),
        )
        if result.series_id in results:
            raise AnalysisError(f"line {line}: duplicate series {result.series_id}")
        if result.status == "OK" and (
            result.theta_obs is None or result.p_value is None
        ):
            raise AnalysisError(f"line {line}: OK result needs theta_obs and p_value")
        results[result.series_id] = result
    if not results:
        raise AnalysisError("series results CSV contains no results")
    return results


def load_logistic_points(path: Path) -> list[LogisticPoint]:
    points = []
    for line, row in read_rows(path, LOGISTIC_POINT_FIELDS):
        wrong = require_text(row, "wrong", line)
        if wrong not in {"0", "1"}:
            raise AnalysisError(f"line {line}: wrong must be 0 or 1")
        arm_id = require_text(row, "arm_id", line)
        if arm_id not in CANONICAL_ARMS:
            raise AnalysisError(
                f"line {line}: logistic chart uses non-canonical arm {arm_id!r}"
            )
        points.append(
            LogisticPoint(
                regression_id=require_text(row, "regression_id", line),
                prediction_id=require_text(row, "prediction_id", line),
                program_id=require_text(row, "program_id", line),
                execution_id=(row.get("execution_id") or "").strip(),
                model_id=require_text(row, "model_id", line),
                arm_id=arm_id,
                arm_group=require_text(row, "arm_group", line),
                scope=require_text(row, "scope", line),
                metric_name=require_text(row, "metric_name", line),
                x=parse_float(row["x"], "x", line),
                wrong=int(wrong),
            )
        )
    if not points:
        raise AnalysisError("logistic points CSV contains no points")
    return points


def load_logistic_results(path: Path) -> dict[tuple[str, str], LogisticResult]:
    results = {}
    for line, row in read_rows(path, LOGISTIC_RESULT_FIELDS):
        result = LogisticResult(
            regression_id=require_text(row, "regression_id", line),
            model_id=require_text(row, "model_id", line),
            arm_group=require_text(row, "arm_group", line),
            scope=require_text(row, "scope", line),
            metric_name=require_text(row, "metric_name", line),
            included_arms=require_text(row, "included_arms", line),
            n=parse_nonnegative_int(row["n"], "n", line),
            n_wrong=parse_nonnegative_int(row["n_wrong"], "n_wrong", line),
            odds_ratio=parse_optional_float(row["odds_ratio"], "odds_ratio", line),
            ci_low=parse_optional_float(row["ci_low"], "ci_low", line),
            ci_high=parse_optional_float(row["ci_high"], "ci_high", line),
            p_value=parse_optional_float(row["p_value"], "p_value", line),
            status=require_text(row, "status", line),
        )
        key = (result.regression_id, result.model_id)
        if key in results:
            raise AnalysisError(f"line {line}: duplicate logistic result {key}")
        if result.status == "OK" and None in (
            result.odds_ratio,
            result.ci_low,
            result.ci_high,
            result.p_value,
        ):
            raise AnalysisError(f"line {line}: OK logistic result is incomplete")
        results[key] = result
    if not results:
        raise AnalysisError("logistic results CSV contains no results")
    return results


def load_logistic_curves(path: Path) -> list[LogisticCurvePoint]:
    curves = []
    for line, row in read_rows(path, LOGISTIC_CURVE_FIELDS):
        curves.append(
            LogisticCurvePoint(
                regression_id=require_text(row, "regression_id", line),
                model_id=require_text(row, "model_id", line),
                arm_group=require_text(row, "arm_group", line),
                scope=require_text(row, "scope", line),
                metric_name=require_text(row, "metric_name", line),
                grid_index=parse_nonnegative_int(row["grid_index"], "grid_index", line),
                x=parse_float(row["x"], "x", line),
                p_wrong=parse_float(row["p_wrong"], "p_wrong", line),
                ci_low=parse_float(row["ci_low"], "ci_low", line),
                ci_high=parse_float(row["ci_high"], "ci_high", line),
            )
        )
    return curves


def load_config(path: Path) -> dict[str, Any]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise AnalysisError(f"invalid config JSON: {error}") from error
    if not isinstance(config, dict):
        raise AnalysisError("config root must be an object")
    formats = config.get("formats", ["png", "pdf"])
    if (
        not isinstance(formats, list)
        or not formats
        or not all(item in {"png", "pdf"} for item in formats)
        or len(formats) != len(set(formats))
    ):
        raise AnalysisError("formats must contain unique png and/or pdf values")
    target_bins = config.get("target_bins", 4)
    dpi = config.get("dpi", 220)
    if not isinstance(target_bins, int) or target_bins < 1:
        raise AnalysisError("target_bins must be positive")
    if not isinstance(dpi, int) or dpi < 72:
        raise AnalysisError("dpi must be at least 72")
    for field in ("model_order", "group_order"):
        value = config.get(field)
        if value is not None and (
            not isinstance(value, list)
            or not all(isinstance(item, str) and item for item in value)
            or len(value) != len(set(value))
        ):
            raise AnalysisError(f"{field} must contain unique nonempty strings")
    mappings = {}
    for field in ("model_labels", "group_labels", "metric_units", "metric_descriptions"):
        labels = config.get(field, {})
        if not isinstance(labels, dict) or not all(
            isinstance(key, str)
            and key
            and isinstance(value, str)
            and value
            for key, value in labels.items()
        ):
            raise AnalysisError(f"{field} must map nonempty strings")
        mappings[field] = labels
    log1p_metrics = config.get("log1p_metrics", [])
    if (
        not isinstance(log1p_metrics, list)
        or not all(isinstance(item, str) and item for item in log1p_metrics)
        or len(log1p_metrics) != len(set(log1p_metrics))
    ):
        raise AnalysisError("log1p_metrics must contain unique nonempty strings")
    sources = config.get("analysis_sources")
    if sources is not None:
        if not isinstance(sources, list) or not sources:
            raise AnalysisError("analysis_sources must be a nonempty list")
        names = set()
        for index, source in enumerate(sources):
            if not isinstance(source, dict):
                raise AnalysisError(f"analysis_sources[{index}] must be an object")
            for field in ("name", "points", "series_results"):
                if not isinstance(source.get(field), str) or not source[field]:
                    raise AnalysisError(
                        f"analysis_sources[{index}].{field} must be nonempty"
                    )
            if source["name"] in names:
                raise AnalysisError(f"duplicate analysis source name: {source['name']}")
            names.add(source["name"])
            for field in ("include_scopes", "include_groups"):
                value = source.get(field)
                if value is not None and (
                    not isinstance(value, list)
                    or not value
                    or not all(isinstance(item, str) and item for item in value)
                    or len(value) != len(set(value))
                ):
                    raise AnalysisError(
                        f"analysis_sources[{index}].{field} must contain unique nonempty strings"
                    )
    regression_sources = config.get("logistic_regression_sources", [])
    if not isinstance(regression_sources, list):
        raise AnalysisError("logistic_regression_sources must be a list")
    source_names = set()
    for index, source in enumerate(regression_sources):
        if not isinstance(source, dict):
            raise AnalysisError(
                f"logistic_regression_sources[{index}] must be an object"
            )
        for field in ("name", "points", "results", "curves"):
            if not isinstance(source.get(field), str) or not source[field]:
                raise AnalysisError(
                    f"logistic_regression_sources[{index}].{field} must be nonempty"
                )
        if source["name"] in source_names:
            raise AnalysisError(
                f"duplicate logistic regression source name: {source['name']}"
            )
        source_names.add(source["name"])
    return {
        **config,
        "formats": formats,
        "target_bins": target_bins,
        "dpi": dpi,
        "log1p_metrics": log1p_metrics,
        **mappings,
    }


def validate_inputs(
    points: Sequence[Point], results: dict[str, SeriesResult], config: dict[str, Any]
) -> dict[str, list[Point]]:
    grouped: dict[str, list[Point]] = defaultdict(list)
    for point in points:
        grouped[point.series_id].append(point)
    if set(grouped) != set(results):
        missing = sorted(set(grouped) - set(results))
        extra = sorted(set(results) - set(grouped))
        raise AnalysisError(
            f"series mismatch; missing results={missing}, results without points={extra}"
        )
    for series_id, series_points in grouped.items():
        metadata = {
            (point.model_id, point.arm_group, point.scope, point.metric_name)
            for point in series_points
        }
        if len(metadata) != 1:
            raise AnalysisError(f"series {series_id} has inconsistent point metadata")
        model, group, scope, metric = next(iter(metadata))
        result = results[series_id]
        if (model, group, scope, metric) != (
            result.model_id,
            result.arm_group,
            result.scope,
            result.metric_name,
        ):
            raise AnalysisError(f"series {series_id} result metadata does not match")
        successes = sum(point.y for point in series_points)
        failures = len(series_points) - successes
        if (successes, failures, len(series_points)) != (
            result.n_success,
            result.n_failure,
            result.n_total,
        ):
            raise AnalysisError(f"series {series_id} result counts do not match points")
    models = {point.model_id for point in points}
    model_order = config.get("model_order")
    if model_order is not None and set(model_order) != models:
        raise AnalysisError("model_order must contain every input model exactly once")
    unknown_labels = set(config["model_labels"]) - models
    if unknown_labels:
        raise AnalysisError(f"model_labels contains unknown models: {unknown_labels}")
    return grouped


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not result:
        raise AnalysisError(f"value has no usable filename slug: {value}")
    return result


def ordinary_chart_title(group_label: str, metric: str) -> str:
    return f"{group_label}\nAccuracy versus {metric}"


def group_seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


def tie_preserving_bins(values: Sequence[float], target_bins: int) -> list[int]:
    grouped: list[tuple[float, list[int]]] = []
    for index in sorted(range(len(values)), key=lambda item: (values[item], item)):
        if not grouped or grouped[-1][0] != values[index]:
            grouped.append((values[index], []))
        grouped[-1][1].append(index)
    bin_count = min(target_bins, len(grouped))
    if not bin_count:
        return []
    counts = [len(indices) for _, indices in grouped]
    prefix = [0]
    for count in counts:
        prefix.append(prefix[-1] + count)
    target = len(values) / bin_count
    costs = [[math.inf] * (bin_count + 1) for _ in range(len(grouped) + 1)]
    previous = [[-1] * (bin_count + 1) for _ in range(len(grouped) + 1)]
    costs[0][0] = 0.0
    for end in range(1, len(grouped) + 1):
        for bins in range(1, min(bin_count, end) + 1):
            for start in range(bins - 1, end):
                size = prefix[end] - prefix[start]
                candidate = costs[start][bins - 1] + (size - target) ** 2
                if candidate < costs[end][bins]:
                    costs[end][bins] = candidate
                    previous[end][bins] = start
    boundaries = []
    end = len(grouped)
    bins = bin_count
    while bins:
        start = previous[end][bins]
        boundaries.append((start, end))
        end = start
        bins -= 1
    assignments = [0] * len(values)
    for bin_index, (start, end) in enumerate(reversed(boundaries), 1):
        for _, indices in grouped[start:end]:
            for index in indices:
                assignments[index] = bin_index
    return assignments


def wilson_interval(successes: int, total: int) -> tuple[float, float]:
    proportion = successes / total
    denominator = 1 + Z_95**2 / total
    center = (proportion + Z_95**2 / (2 * total)) / denominator
    margin = (
        Z_95
        * math.sqrt(proportion * (1 - proportion) / total + Z_95**2 / (4 * total**2))
        / denominator
    )
    return center - margin, center + margin


def binned_accuracy(points: Sequence[Point], target_bins: int) -> list[dict[str, float]]:
    assignments = tie_preserving_bins([point.x for point in points], target_bins)
    summaries = []
    for bin_index in sorted(set(assignments)):
        group = [
            point
            for point, assignment in zip(points, assignments, strict=True)
            if assignment == bin_index
        ]
        successes = sum(point.y for point in group)
        low, high = wilson_interval(successes, len(group))
        summaries.append(
            {
                "x": float(np.median([point.x for point in group])),
                "accuracy": successes / len(group),
                "low": low,
                "high": high,
                "successes": successes,
                "failures": len(group) - successes,
                "total": len(group),
            }
        )
    return summaries


def binned_wrong_rate(
    points: Sequence[LogisticPoint], target_bins: int
) -> list[dict[str, float]]:
    assignments = tie_preserving_bins([point.x for point in points], target_bins)
    summaries = []
    for bin_index in sorted(set(assignments)):
        group = [
            point
            for point, assignment in zip(points, assignments, strict=True)
            if assignment == bin_index
        ]
        wrong = sum(point.wrong for point in group)
        low, high = wilson_interval(wrong, len(group))
        summaries.append(
            {
                "x": float(np.median([point.x for point in group])),
                "wrong_rate": wrong / len(group),
                "low": low,
                "high": high,
                "wrong": wrong,
                "correct": len(group) - wrong,
                "total": len(group),
            }
        )
    return summaries


def format_tick(value: float) -> str:
    if math.isclose(value, round(value), rel_tol=1e-9, abs_tol=1e-8):
        value = float(round(value))
    for scale, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(value) >= scale:
            return f"{value / scale:g}{suffix}"
    if math.isclose(value, round(value), abs_tol=1e-8):
        return f"{round(value):,}"
    return f"{value:,.2g}"


def log1p_ticks(minimum: float, maximum: float) -> list[float]:
    ticks = [0.0] if minimum <= 0 else []
    if maximum <= 0:
        return ticks
    candidates = []
    for exponent in range(-1, math.ceil(math.log10(maximum)) + 1):
        scale = 10**exponent
        candidates.extend(multiplier * scale for multiplier in (1, 2, 5))
    ticks.extend(value for value in candidates if max(0.0, minimum) <= value <= maximum)
    if len(ticks) <= 5:
        return ticks
    indices = [round(index * (len(ticks) - 1) / 4) for index in range(5)]
    return [ticks[index] for index in dict.fromkeys(indices)]


def annotation(result: SeriesResult) -> str:
    if result.status == "OK":
        floor = 1 / (1 + result.permutations)
        p_text = f"< {floor:.4f}" if result.p_value <= floor else f"{result.p_value:.4f}"
        return (
            f"failure-larger rate (θ) = {result.theta_obs:.2f} · p {p_text}\n"
            f"failures={result.n_failure}, successes={result.n_success}"
        )
    total = result.n_success + result.n_failure
    return (
        f"every prediction had the same outcome: {result.n_success}/{total} correct\n"
        f"no failure-success pair, so θ does not exist"
    )


def write_chart(
    output_base: Path,
    title: str,
    metric: str,
    metric_unit: str | None,
    metric_description: str | None,
    models: Sequence[str],
    labels: dict[str, str],
    points: dict[str, list[Point]],
    results: dict[str, SeriesResult],
    bins_by_model: dict[str, list[dict[str, float]]],
    config: dict[str, Any],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter
    from matplotlib.lines import Line2D

    outcome_style = STYLE_CONTRACT["prediction_outcome"]
    accuracy_style = STYLE_CONTRACT["overall_accuracy"]
    bin_style = STYLE_CONTRACT["binned_accuracy"]
    annotation_style = STYLE_CONTRACT["statistics_annotation"]

    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    columns = min(3, len(models))
    rows = math.ceil(len(models) / columns)
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(5.4 * columns, 5.2 * rows + 1.7),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    log1p = metric in config["log1p_metrics"]
    all_values = np.asarray(
        [point.x for model in models for point in points[model]], dtype=float
    )
    if log1p and np.any(all_values < 0):
        raise AnalysisError(f"metric {metric} has negative values on a log1p axis")
    for axis, model in zip(axes.flat, models, strict=False):
        series_points = points[model]
        result = results[model]
        axis.text(
            0,
            1.20,
            labels[model],
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=11,
            fontweight="semibold",
            clip_on=False,
        )
        values = np.asarray([point.x for point in series_points], dtype=float)
        shown_values = np.log1p(values) if log1p else values
        outcomes = np.asarray([point.y for point in series_points], dtype=float)
        span = max(1.0, float(np.ptp(shown_values)))
        rng = np.random.default_rng(group_seed(f"chart\0{title}\0{model}"))
        axis.scatter(
            shown_values + rng.normal(0, span * 0.0025, len(values)),
            outcomes,
            s=outcome_style["size"],
            color=outcome_style["color"],
            alpha=outcome_style["alpha"],
            marker=outcome_style["matplotlib_marker"],
            linewidths=0,
            zorder=2,
        )
        axis.axhline(
            float(outcomes.mean()),
            color=accuracy_style["color"],
            linestyle=(0, tuple(accuracy_style["dash_pattern"])),
            linewidth=accuracy_style["linewidth"],
            zorder=1,
        )
        bins = bins_by_model[model]
        raw_bin_x = np.asarray([item["x"] for item in bins])
        bin_x = np.log1p(raw_bin_x) if log1p else raw_bin_x
        bin_y = np.asarray([item["accuracy"] for item in bins])
        lower = np.maximum(0.0, bin_y - np.asarray([item["low"] for item in bins]))
        upper = np.maximum(0.0, np.asarray([item["high"] for item in bins]) - bin_y)
        axis.errorbar(
            bin_x,
            bin_y,
            yerr=np.vstack([lower, upper]),
            fmt=bin_style["matplotlib_marker"],
            markersize=bin_style["markersize"],
            color=bin_style["color"],
            ecolor=bin_style["color"],
            elinewidth=bin_style["elinewidth"],
            capsize=bin_style["capsize"],
            zorder=4,
        )
        axis.text(
            0,
            1.05,
            annotation(result),
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=annotation_style["fontsize"],
            color=annotation_style["color"],
            linespacing=1.05,
            clip_on=False,
        )
        axis.grid(axis="y", color="#e7e7e3", linewidth=0.8)
        axis.set_ylim(-0.04, 1.04)
        axis.set_yticks([0, 0.25, 0.5, 0.75, 1])
        axis.spines[["top", "right"]].set_visible(False)
    for axis in axes.flat[len(models) :]:
        axis.axis("off")
    if log1p:
        ticks = log1p_ticks(float(all_values.min()), float(all_values.max()))
        for axis in axes.flat[: len(models)]:
            axis.set_xticks(np.log1p(ticks))
            axis.xaxis.set_major_formatter(
                FuncFormatter(
                    lambda value, _: format_tick(max(0.0, np.expm1(value)))
                )
            )
    figure.legend(
        handles=[
            Line2D(
                [0],
                [0],
                color=accuracy_style["color"],
                linestyle=(0, tuple(accuracy_style["dash_pattern"])),
                label=accuracy_style["label"],
            ),
            Line2D(
                [0],
                [0],
                marker=bin_style["matplotlib_marker"],
                color=bin_style["color"],
                linestyle="none",
                label=bin_style["label"],
            ),
            Line2D(
                [0],
                [0],
                marker=outcome_style["matplotlib_marker"],
                color=outcome_style["color"],
                alpha=0.5,
                linestyle="none",
                label=outcome_style["label"],
            ),
        ],
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.01),
    )
    x_label = metric
    if metric_unit:
        x_label += f" ({metric_unit})"
    if metric in config["log1p_metrics"]:
        x_label += " · log1p spacing, ticks show original values"
    figure.supxlabel(x_label, y=0.085)
    figure.supylabel("Prediction accuracy", x=0.012)
    title_lines = []
    for title_part in title.splitlines():
        title_lines.extend(textwrap.wrap(title_part, width=88) or [""])
    displayed_title = "\n".join(title_lines)
    title_line_count = len(title_lines)
    figure.suptitle(
        displayed_title,
        x=0.04,
        y=0.985,
        ha="left",
        va="top",
        fontsize=16,
        fontweight="semibold",
    )
    explanation = "What it tracks: "
    explanation += metric_description or "No description was configured."
    figure.text(
        0.04,
        0.86 if title_line_count > 1 else 0.925,
        textwrap.fill(explanation, width=155),
        ha="left",
        va="top",
        fontsize=9,
        color="#555550",
    )
    figure.subplots_adjust(
        left=0.07,
        right=0.99,
        bottom=0.17,
        top=0.64 if title_line_count > 1 else 0.72,
        hspace=0.68,
        wspace=0.04,
    )
    output_base.parent.mkdir(parents=True, exist_ok=True)
    if "png" in config["formats"]:
        figure.savefig(
            output_base.with_suffix(".png"),
            dpi=config["dpi"],
            metadata={"Software": "generate-analysis"},
        )
    if "pdf" in config["formats"]:
        figure.savefig(
            output_base.with_suffix(".pdf"),
            metadata={"Creator": "generate-analysis", "Producer": "matplotlib", "CreationDate": None, "ModDate": None},
        )
    plt.close(figure)


def logistic_annotation(result: LogisticResult) -> str:
    if result.status != "OK":
        return (
            f"{result.status.lower().replace('_', ' ')}\n"
            f"wrong predictions={result.n_wrong}, predictions={result.n}"
        )
    p_text = "< 0.0001" if result.p_value < 0.0001 else f"= {result.p_value:.4f}"
    return (
        f"OR per doubling = {result.odds_ratio:.2f} "
        f"({result.ci_low:.2f}–{result.ci_high:.2f}) · p {p_text}\n"
        f"wrong={result.n_wrong}/{result.n} pooled points"
    )


def log2_ticks(minimum: float, maximum: float) -> list[float]:
    low = math.floor(math.log2(minimum))
    high = math.ceil(math.log2(maximum))
    step = max(1, math.ceil((high - low) / 4))
    ticks = [2.0**power for power in range(low, high + 1, step)]
    if ticks[-1] < maximum:
        ticks.append(2.0**high)
    return ticks


def write_logistic_chart(
    output_base: Path,
    title: str,
    metric: str,
    metric_unit: str | None,
    metric_description: str | None,
    models: Sequence[str],
    labels: dict[str, str],
    points: dict[str, list[LogisticPoint]],
    results: dict[str, LogisticResult],
    curves: dict[str, list[LogisticCurvePoint]],
    bins_by_model: dict[str, list[dict[str, float]]],
    config: dict[str, Any],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.ticker import FuncFormatter

    outcome_style = STYLE_CONTRACT["prediction_outcome"]
    bin_style = STYLE_CONTRACT["binned_accuracy"]
    fit_style = STYLE_CONTRACT["logistic_fit"]
    annotation_style = STYLE_CONTRACT["statistics_annotation"]
    columns = min(3, len(models))
    rows = math.ceil(len(models) / columns)
    figure, axes = plt.subplots(
        rows,
        columns,
        figsize=(5.4 * columns, 5.2 * rows + 1.7),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    all_values = np.asarray(
        [point.x for model in models for point in points[model]], dtype=float
    )
    if np.any(all_values <= 0):
        raise AnalysisError(f"logistic metric {metric} must contain positive values")
    for axis, model in zip(axes.flat, models, strict=False):
        model_points = points[model]
        values = np.asarray([point.x for point in model_points], dtype=float)
        shown_values = np.log2(values)
        outcomes = np.asarray([point.wrong for point in model_points], dtype=float)
        span = max(1.0, float(np.ptp(shown_values)))
        rng = np.random.default_rng(group_seed(f"logistic-chart\0{title}\0{model}"))
        axis.text(
            0,
            1.20,
            labels[model],
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=11,
            fontweight="semibold",
            clip_on=False,
        )
        axis.scatter(
            shown_values + rng.normal(0, span * 0.0025, len(values)),
            outcomes,
            s=outcome_style["size"],
            color=outcome_style["color"],
            alpha=outcome_style["alpha"],
            marker=outcome_style["matplotlib_marker"],
            linewidths=0,
            zorder=2,
        )
        model_curve = sorted(curves.get(model, []), key=lambda item: item.grid_index)
        if results[model].status == "OK" and not model_curve:
            raise AnalysisError(f"missing logistic curve for {metric} and {model}")
        if model_curve:
            curve_x = np.log2([item.x for item in model_curve])
            curve_y = np.asarray([item.p_wrong for item in model_curve])
            curve_low = np.asarray([item.ci_low for item in model_curve])
            curve_high = np.asarray([item.ci_high for item in model_curve])
            axis.fill_between(
                curve_x,
                curve_low,
                curve_high,
                color=fit_style["color"],
                alpha=fit_style["band_alpha"],
                zorder=1,
            )
            axis.plot(
                curve_x,
                curve_y,
                color=fit_style["color"],
                linewidth=fit_style["linewidth"],
                zorder=3,
            )
        bins = bins_by_model[model]
        bin_x = np.log2([item["x"] for item in bins])
        bin_y = np.asarray([item["wrong_rate"] for item in bins])
        lower = np.maximum(0.0, bin_y - np.asarray([item["low"] for item in bins]))
        upper = np.maximum(0.0, np.asarray([item["high"] for item in bins]) - bin_y)
        axis.errorbar(
            bin_x,
            bin_y,
            yerr=np.vstack([lower, upper]),
            fmt=bin_style["matplotlib_marker"],
            markersize=bin_style["markersize"],
            color=bin_style["color"],
            ecolor=bin_style["color"],
            elinewidth=bin_style["elinewidth"],
            capsize=bin_style["capsize"],
            zorder=4,
        )
        axis.text(
            0,
            1.05,
            logistic_annotation(results[model]),
            transform=axis.transAxes,
            ha="left",
            va="bottom",
            fontsize=annotation_style["fontsize"],
            color=annotation_style["color"],
            linespacing=1.05,
            clip_on=False,
        )
        axis.grid(axis="y", color="#e7e7e3", linewidth=0.8)
        axis.set_ylim(-0.04, 1.04)
        axis.set_yticks([0, 0.25, 0.5, 0.75, 1])
        axis.spines[["top", "right"]].set_visible(False)
    for axis in axes.flat[len(models) :]:
        axis.axis("off")
    ticks = log2_ticks(float(all_values.min()), float(all_values.max()))
    shown_min = float(np.log2(all_values.min()))
    shown_max = float(np.log2(all_values.max()))
    shown_span = max(1.0, shown_max - shown_min)
    edge_padding = min(2.0, max(0.2, shown_span * 0.04))
    for axis in axes.flat[: len(models)]:
        axis.set_xticks(np.log2(ticks))
        axis.set_xlim(shown_min - edge_padding, shown_max + edge_padding)
        axis.xaxis.set_major_formatter(
            FuncFormatter(lambda value, _: format_tick(2.0**value))
        )
    figure.legend(
        handles=[
            Line2D(
                [0],
                [0],
                color=fit_style["color"],
                linewidth=fit_style["linewidth"],
                label=fit_style["label"],
            ),
            Line2D(
                [0],
                [0],
                marker=bin_style["matplotlib_marker"],
                color=bin_style["color"],
                linestyle="none",
                label="binned wrong rate + Wilson 95% CI",
            ),
            Line2D(
                [0],
                [0],
                marker=outcome_style["matplotlib_marker"],
                color=outcome_style["color"],
                alpha=0.5,
                linestyle="none",
                label=outcome_style["label"],
            ),
        ],
        loc="lower center",
        ncol=3,
        frameon=False,
        bbox_to_anchor=(0.5, 0.01),
    )
    x_label = metric + (f" ({metric_unit})" if metric_unit else "")
    x_label += " · log2 spacing, ticks show original values"
    figure.supxlabel(x_label, y=0.085)
    figure.supylabel("P(wrong = 1)", x=0.012)
    title_lines = []
    for title_part in title.splitlines():
        title_lines.extend(textwrap.wrap(title_part, width=88) or [""])
    displayed_title = "\n".join(title_lines)
    title_line_count = len(title_lines)
    figure.suptitle(
        displayed_title,
        x=0.04,
        y=0.985,
        ha="left",
        va="top",
        fontsize=16,
        fontweight="semibold",
    )
    explanation = "What it tracks: " + (
        metric_description or "No description was configured."
    )
    figure.text(
        0.04,
        0.86 if title_line_count > 1 else 0.925,
        textwrap.fill(explanation, width=155),
        ha="left",
        va="top",
        fontsize=9,
        color="#555550",
    )
    figure.subplots_adjust(
        left=0.07,
        right=0.965,
        bottom=0.17,
        top=0.64 if title_line_count > 1 else 0.72,
        hspace=0.68,
        wspace=0.12,
    )
    output_base.parent.mkdir(parents=True, exist_ok=True)
    if "png" in config["formats"]:
        figure.savefig(
            output_base.with_suffix(".png"),
            dpi=config["dpi"],
            metadata={"Software": "generate-analysis"},
        )
    if "pdf" in config["formats"]:
        figure.savefig(
            output_base.with_suffix(".pdf"),
            metadata={
                "Creator": "generate-analysis",
                "Producer": "matplotlib",
                "CreationDate": None,
                "ModDate": None,
            },
        )
    plt.close(figure)


def ordered(values: set[str], preferred: list[str] | None) -> list[str]:
    if preferred is None:
        return sorted(values)
    return [value for value in preferred if value in values] + sorted(values - set(preferred))


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8", newline="")
    os.replace(temporary, path)


def csv_content(fields: Sequence[str], rows: Sequence[dict[str, object]]) -> str:
    from io import StringIO

    output = StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def select_analysis_inputs(
    config_path: Path,
    config: dict[str, Any],
    points_path: Path | None,
    results_path: Path | None,
) -> tuple[list[Point], dict[str, SeriesResult], list[dict[str, Any]]]:
    declared = config.get("analysis_sources")
    if declared is not None and (points_path is not None or results_path is not None):
        raise AnalysisError(
            "do not combine analysis_sources with --points or --series-results"
        )
    if declared is None:
        if points_path is None or results_path is None:
            raise AnalysisError(
                "--points and --series-results are required without analysis_sources"
            )
        declared = [
            {
                "name": "default",
                "points": str(points_path),
                "series_results": str(results_path),
                "absolute": True,
            }
        ]
    selected_points: list[Point] = []
    selected_results: dict[str, SeriesResult] = {}
    provenance = []
    for source in declared:
        if source.get("absolute"):
            source_points_path = Path(source["points"])
            source_results_path = Path(source["series_results"])
        else:
            source_points_path = (config_path.parent / source["points"]).resolve()
            source_results_path = (
                config_path.parent / source["series_results"]
            ).resolve()
        source_points = load_points(source_points_path)
        source_results = load_results(source_results_path)
        source_series = validate_inputs(source_points, source_results, config)
        include_scopes = set(source.get("include_scopes", []))
        include_groups = set(source.get("include_groups", []))
        available_scopes = {result.scope for result in source_results.values()}
        available_groups = {result.arm_group for result in source_results.values()}
        if include_scopes - available_scopes:
            raise AnalysisError(
                f"analysis source {source['name']} requests unavailable scopes"
            )
        if include_groups - available_groups:
            raise AnalysisError(
                f"analysis source {source['name']} requests unavailable groups"
            )
        selected_ids = {
            series_id
            for series_id, result in source_results.items()
            if (not include_scopes or result.scope in include_scopes)
            and (not include_groups or result.arm_group in include_groups)
        }
        duplicates = selected_ids & set(selected_results)
        if duplicates:
            raise AnalysisError(
                f"duplicate selected series across analysis sources: {sorted(duplicates)}"
            )
        for series_id in sorted(selected_ids):
            selected_points.extend(source_series[series_id])
            selected_results[series_id] = source_results[series_id]
        provenance.append(
            {
                "name": source["name"],
                "points_file": str(source_points_path),
                "points_sha256": hashlib.sha256(
                    source_points_path.read_bytes()
                ).hexdigest(),
                "series_results_file": str(source_results_path),
                "series_results_sha256": hashlib.sha256(
                    source_results_path.read_bytes()
                ).hexdigest(),
                "include_scopes": sorted(include_scopes),
                "include_groups": sorted(include_groups),
                "available_series_count": len(source_results),
                "selected_series_count": len(selected_ids),
                "excluded_series_count": len(source_results) - len(selected_ids),
            }
        )
    if not selected_points:
        raise AnalysisError("analysis source selection contains no points")
    return selected_points, selected_results, provenance


def select_logistic_inputs(
    config_path: Path, config: dict[str, Any]
) -> tuple[
    list[LogisticPoint],
    dict[tuple[str, str], LogisticResult],
    list[LogisticCurvePoint],
    list[dict[str, Any]],
]:
    points = []
    results = {}
    curves = []
    provenance = []
    for source in config.get("logistic_regression_sources", []):
        paths = {
            field: (config_path.parent / source[field]).resolve()
            for field in ("points", "results", "curves")
        }
        source_points = load_logistic_points(paths["points"])
        source_results = load_logistic_results(paths["results"])
        source_curves = load_logistic_curves(paths["curves"])
        duplicate_results = set(results) & set(source_results)
        if duplicate_results:
            raise AnalysisError(
                f"duplicate logistic results across sources: {sorted(duplicate_results)}"
            )
        point_counts: dict[tuple[str, str], list[LogisticPoint]] = defaultdict(list)
        for point in source_points:
            point_counts[(point.regression_id, point.model_id)].append(point)
        for key, result in source_results.items():
            selected = point_counts.get(key, [])
            if len(selected) != result.n:
                raise AnalysisError(f"logistic result {key} point count does not match")
            if sum(point.wrong for point in selected) != result.n_wrong:
                raise AnalysisError(f"logistic result {key} wrong count does not match")
            metadata = {
                (point.arm_group, point.scope, point.metric_name)
                for point in selected
            }
            if metadata != {(result.arm_group, result.scope, result.metric_name)}:
                raise AnalysisError(f"logistic result {key} metadata does not match")
        unknown_points = set(point_counts) - set(source_results)
        if unknown_points:
            raise AnalysisError(
                f"logistic points without results: {sorted(unknown_points)}"
            )
        curve_keys = {(curve.regression_id, curve.model_id) for curve in source_curves}
        required_curve_keys = {
            key for key, result in source_results.items() if result.status == "OK"
        }
        if curve_keys != required_curve_keys:
            raise AnalysisError(
                "logistic curve series must exactly match successful results"
            )
        points.extend(source_points)
        results.update(source_results)
        curves.extend(source_curves)
        provenance.append(
            {
                "name": source["name"],
                **{
                    f"{field}_file": source[field]
                    for field in paths
                },
                **{
                    f"{field}_sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                    for field, path in paths.items()
                },
                "point_count": len(source_points),
                "result_count": len(source_results),
                "curve_point_count": len(source_curves),
            }
        )
    return points, results, curves, provenance


def generate(
    points_path: Path | None,
    results_path: Path | None,
    config_path: Path,
    output: Path,
) -> dict[str, int]:
    config = load_config(config_path)
    points, results, input_provenance = select_analysis_inputs(
        config_path, config, points_path, results_path
    )
    logistic_points, logistic_results, logistic_curves, logistic_provenance = (
        select_logistic_inputs(config_path, config)
    )
    series_points = validate_inputs(points, results, config)
    model_values = {point.model_id for point in points}
    models = ordered(model_values, config.get("model_order"))
    labels = {model: config["model_labels"].get(model, model) for model in models}
    group_labels = config.get("group_labels", {})
    metric_units = config.get("metric_units", {})
    metric_descriptions = config.get("metric_descriptions", {})
    chart_series: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    for series_id, result in results.items():
        key = (result.scope, result.arm_group, result.metric_name)
        if result.model_id in chart_series[key]:
            raise AnalysisError(f"duplicate chart series for {key} and {result.model_id}")
        chart_series[key][result.model_id] = series_id
    logistic_by_regression: dict[str, dict[str, LogisticResult]] = defaultdict(dict)
    logistic_key_by_regression: dict[str, tuple[str, str, str]] = {}
    for (regression_id, model_id), result in logistic_results.items():
        logistic_by_regression[regression_id][model_id] = result
        key = (result.scope, result.arm_group, result.metric_name)
        previous = logistic_key_by_regression.setdefault(regression_id, key)
        if previous != key:
            raise AnalysisError(
                f"logistic regression {regression_id} has inconsistent metadata"
            )
    logistic_keys = set(logistic_key_by_regression.values())
    if len(logistic_keys) != len(logistic_key_by_regression):
        raise AnalysisError("multiple logistic regressions target the same chart path")
    for key in logistic_keys:
        chart_series.pop(key, None)
    groups = ordered({key[1] for key in chart_series}, config.get("group_order"))
    group_index = {value: index for index, value in enumerate(groups)}
    keys = sorted(
        chart_series,
        key=lambda key: ({"static": 0, "dynamic": 1}[key[0]], group_index[key[1]], key[2]),
    )
    markdown = [
        "# Metric-accuracy charts",
        "",
        "Gray dots are eligible prediction outcomes. Orange squares are tie-preserving binned accuracies with Wilson 95% intervals. The dashed line is overall accuracy. Right-skewed metrics use zero-safe log1p spacing with tick labels in original metric units.",
        "",
        "The panel's failure-larger rate (`theta`) is how often a failed prediction has a larger metric value than a successful prediction, ties counting half; `0.5` means no ordering tendency. The permutation `p` is how often shuffled correct/wrong labels produced at least as much separation.",
        "",
        "Panel annotations are read unchanged from `series-results.csv`; this generator does not recalculate theta or permutation p-values. Every chart uses the exact metric identifier and explains what it tracks directly below the title.",
        "",
        "Configured logistic-regression metrics replace the ordinary accuracy chart at the same `charts/<scope>/<group>/<metric>` path. Their gray dots use `wrong=1`, orange squares show binned wrong rates, and the blue line and 95% confidence band are read unchanged from upstream regression outputs. OR, its 95% interval, and p are likewise rendered without refitting.",
        "",
    ]
    chart_count = 0
    chart_counts_by_scope: dict[str, int] = defaultdict(int)
    chart_data_rows: list[dict[str, object]] = []
    logistic_chart_data_rows: list[dict[str, object]] = []
    current_scope = None
    current_group = None
    for scope, group, metric in keys:
        if scope != current_scope:
            markdown.extend([f"## {scope.title()} metrics", ""])
            current_scope = scope
            current_group = None
        if group != current_group:
            markdown.extend([f"### {group_labels.get(group, group)}", ""])
            current_group = group
        series_by_model = chart_series[(scope, group, metric)]
        chart_models = [model for model in models if model in series_by_model]
        bins_by_model = {
            model: binned_accuracy(
                series_points[series_by_model[model]], config["target_bins"]
            )
            for model in chart_models
        }
        for model in chart_models:
            result = results[series_by_model[model]]
            for bin_index, item in enumerate(bins_by_model[model], 1):
                chart_data_rows.append(
                    {
                        "series_id": result.series_id,
                        "model_id": model,
                        "arm_group": group,
                        "scope": scope,
                        "metric_name": metric,
                        "bin_index": bin_index,
                        "x": format(item["x"], ".17g"),
                        "accuracy": format(item["accuracy"], ".17g"),
                        "wilson_low": format(item["low"], ".17g"),
                        "wilson_high": format(item["high"], ".17g"),
                        "n_success": int(item["successes"]),
                        "n_failure": int(item["failures"]),
                        "n_total": int(item["total"]),
                    }
                )
        path = Path("charts") / scope / slug(group) / slug(metric)
        group_label = group_labels.get(group, group)
        write_chart(
            output / path,
            ordinary_chart_title(group_label, metric),
            metric,
            metric_units.get(metric),
            metric_descriptions.get(metric),
            chart_models,
            labels,
            {model: series_points[series_by_model[model]] for model in chart_models},
            {model: results[series_by_model[model]] for model in chart_models},
            bins_by_model,
            config,
        )
        markdown.extend(
            [
                f"#### `{metric}`",
                "",
                metric_descriptions.get(metric, "No plain-English description was configured."),
                "",
                f"![{group_label} {metric}]({path.with_suffix('.png')})",
                "",
            ]
        )
        chart_count += 1
        chart_counts_by_scope[scope] += 1
    if logistic_by_regression:
        markdown.extend(["## Logistic error-probability charts", ""])
    logistic_points_by_series: dict[tuple[str, str], list[LogisticPoint]] = defaultdict(list)
    for point in logistic_points:
        logistic_points_by_series[(point.regression_id, point.model_id)].append(point)
    logistic_curves_by_series: dict[tuple[str, str], list[LogisticCurvePoint]] = defaultdict(list)
    for curve in logistic_curves:
        logistic_curves_by_series[(curve.regression_id, curve.model_id)].append(curve)
    for regression_id in sorted(
        logistic_by_regression,
        key=lambda identifier: logistic_key_by_regression[identifier],
    ):
        scope, group, metric = logistic_key_by_regression[regression_id]
        selected_results = logistic_by_regression[regression_id]
        chart_models = [model for model in models if model in selected_results]
        if set(chart_models) != set(selected_results):
            missing = set(selected_results) - set(chart_models)
            raise AnalysisError(f"logistic results contain unknown models: {missing}")
        points_by_model = {
            model: logistic_points_by_series[(regression_id, model)]
            for model in chart_models
        }
        curves_by_model = {
            model: logistic_curves_by_series.get((regression_id, model), [])
            for model in chart_models
        }
        bins_by_model = {
            model: binned_wrong_rate(points_by_model[model], config["target_bins"])
            for model in chart_models
        }
        included_arm_sets = {
            result.included_arms for result in selected_results.values()
        }
        if len(included_arm_sets) != 1:
            raise AnalysisError(
                f"logistic regression {regression_id} has inconsistent included arms"
            )
        for model in chart_models:
            for bin_index, item in enumerate(bins_by_model[model], 1):
                logistic_chart_data_rows.append(
                    {
                        "regression_id": regression_id,
                        "model_id": model,
                        "arm_group": group,
                        "scope": scope,
                        "metric_name": metric,
                        "bin_index": bin_index,
                        "x": format(item["x"], ".17g"),
                        "wrong_rate": format(item["wrong_rate"], ".17g"),
                        "wilson_low": format(item["low"], ".17g"),
                        "wilson_high": format(item["high"], ".17g"),
                        "n_wrong": int(item["wrong"]),
                        "n_correct": int(item["correct"]),
                        "n_total": int(item["total"]),
                    }
                )
        path = Path("charts") / scope / slug(group) / slug(metric)
        included_arms = next(iter(included_arm_sets)).split(",")
        group_label = "Pooled: " + ", ".join(included_arms)
        write_logistic_chart(
            output / path,
            f"{group_label}\nError probability versus {metric}",
            metric,
            metric_units.get(metric),
            metric_descriptions.get(metric),
            chart_models,
            labels,
            points_by_model,
            selected_results,
            curves_by_model,
            bins_by_model,
            config,
        )
        markdown.extend(
            [
                f"### `{metric}` — {group_label}",
                "",
                metric_descriptions.get(
                    metric, "No plain-English description was configured."
                ),
                "",
                "`n` is the number of pooled `(metric value, wrong-or-correct)`",
                "points in the fit. The included arms are not separate regression",
                "groups; their `arm_id` values remain only for audit.",
                "",
                f"![{group_label} {metric} logistic regression]({path.with_suffix('.png')})",
                "",
            ]
        )
        chart_count += 1
        chart_counts_by_scope[scope] += 1
    atomic_write(output / "charts.md", "\n".join(markdown))
    chart_data = csv_content(CHART_DATA_FIELDS, chart_data_rows)
    atomic_write(output / "chart-data.csv", chart_data)
    logistic_chart_data = csv_content(
        LOGISTIC_CHART_DATA_FIELDS, logistic_chart_data_rows
    )
    if logistic_chart_data_rows:
        atomic_write(output / "logistic-chart-data.csv", logistic_chart_data)
    output_files = sorted(
        [
            output / "charts.md",
            output / "chart-data.csv",
            *(
                [output / "logistic-chart-data.csv"]
                if logistic_chart_data_rows
                else []
            ),
        ],
        key=lambda path: path.as_posix(),
    ) + sorted(
        (path for path in (output / "charts").rglob("*") if path.is_file()),
        key=lambda path: path.as_posix(),
    )
    manifest = {
        "schema": "generate-analysis-charts-v4",
        "analysis_sources": input_provenance,
        "logistic_regression_sources": logistic_provenance,
        "config_file": str(config_path),
        "config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "style": STYLE_CONTRACT,
        "python_version": sys.version.split()[0],
        "numpy_version": np.__version__,
        "point_count": len(points),
        "series_count": len(results),
        "chart_count": chart_count,
        "chart_counts_by_scope": dict(sorted(chart_counts_by_scope.items())),
        "chart_data_file": "chart-data.csv",
        "chart_data_sha256": hashlib.sha256(chart_data.encode("utf-8")).hexdigest(),
        "chart_data_row_count": len(chart_data_rows),
        "logistic_chart_data_file": (
            "logistic-chart-data.csv" if logistic_chart_data_rows else None
        ),
        "logistic_chart_data_sha256": (
            hashlib.sha256(logistic_chart_data.encode("utf-8")).hexdigest()
            if logistic_chart_data_rows
            else None
        ),
        "logistic_chart_data_row_count": len(logistic_chart_data_rows),
        "output_sha256": {
            path.relative_to(output).as_posix(): hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
            for path in output_files
        },
    }
    atomic_write(output / "chart-manifest.json", json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return {"points": len(points), "series": len(results), "charts": chart_count}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--points", type=Path)
    parser.add_argument("--series-results", type=Path)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        summary = generate(
            arguments.points,
            arguments.series_results,
            arguments.config,
            arguments.output,
        )
    except (AnalysisError, OSError) as error:
        parser.error(str(error))
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
