#!/usr/bin/env python3
"""Analyze raw (factor value, correctness) points with a permutation U test."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_COLUMNS = (
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
RESULT_COLUMNS = (
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

METRIC_DESCRIPTIONS = {
    "Omega_CC": "Independent control-flow paths in the source.",
    "Omega_hat_NativeTrace": "Target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.",
    "Omega_hat_StateSize": "Greatest number of runtime value cells reachable from live program variables at one observation point.",
    "Omega_hat_StateLoad": "Reachable runtime value cells summed over every state observation in the run.",
}

CANONICAL_DYNAMIC_ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)

LOGISTIC_POINT_COLUMNS = (
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
LOGISTIC_RESULT_COLUMNS = (
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
LOGISTIC_CURVE_COLUMNS = (
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

    def as_row(self) -> dict[str, str]:
        return {
            "series_id": self.series_id,
            "prediction_id": self.prediction_id,
            "program_id": self.program_id,
            "execution_id": self.execution_id,
            "model_id": self.model_id,
            "arm_id": self.arm_id,
            "arm_group": self.arm_group,
            "scope": self.scope,
            "metric_name": self.metric_name,
            "x": format(self.x, ".17g"),
            "y": str(self.y),
        }


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

    def as_row(self) -> dict[str, str]:
        return {
            "series_id": self.series_id,
            "model_id": self.model_id,
            "arm_group": self.arm_group,
            "scope": self.scope,
            "metric_name": self.metric_name,
            "theta_obs": "" if self.theta_obs is None else format(self.theta_obs, ".12g"),
            "p_value": "" if self.p_value is None else format(self.p_value, ".12g"),
            "n_success": str(self.n_success),
            "n_failure": str(self.n_failure),
            "n_total": str(self.n_total),
            "permutations": str(self.permutations),
            "series_seed": str(self.series_seed),
            "status": self.status,
        }


@dataclass(frozen=True)
class LogisticSpecification:
    regression_id: str
    metric_name: str
    scope: str
    arm_group: str
    include_arms: tuple[str, ...]


@dataclass
class LogisticFit:
    specification: LogisticSpecification
    model_id: str
    points: list[Point]
    parameters: object | None
    covariance: object | None
    se_beta1: float | None
    ci_low: float | None
    ci_high: float | None
    p_value: float | None
    status: str

    @property
    def n_wrong(self) -> int:
        return sum(point.y == 0 for point in self.points)

    @property
    def beta0(self) -> float | None:
        return None if self.parameters is None else float(self.parameters[0])

    @property
    def beta1(self) -> float | None:
        return None if self.parameters is None else float(self.parameters[1])

    @property
    def odds_ratio(self) -> float | None:
        return None if self.beta1 is None else math.exp(self.beta1)


def require_text(row: dict[str, str], field: str, line_number: int) -> str:
    value = (row.get(field) or "").strip()
    if not value:
        raise ValueError(f"line {line_number}: {field} must not be empty")
    return value


def load_points(path: Path) -> list[Point]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("points CSV has no header")
        missing = [name for name in REQUIRED_COLUMNS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"points CSV is missing columns: {', '.join(missing)}")
        points: list[Point] = []
        for line_number, row in enumerate(reader, start=2):
            scope = require_text(row, "scope", line_number)
            if scope not in {"static", "dynamic"}:
                raise ValueError(f"line {line_number}: scope must be static or dynamic")
            execution_id = (row.get("execution_id") or "").strip()
            if scope == "dynamic" and not execution_id:
                raise ValueError(f"line {line_number}: dynamic point needs execution_id")
            try:
                x = float(require_text(row, "x", line_number))
            except ValueError as error:
                raise ValueError(f"line {line_number}: x must be numeric") from error
            if not math.isfinite(x):
                raise ValueError(f"line {line_number}: x must be finite")
            y_text = require_text(row, "y", line_number)
            if y_text not in {"0", "1"}:
                raise ValueError(f"line {line_number}: y must be 0 or 1")
            points.append(
                Point(
                    series_id=require_text(row, "series_id", line_number),
                    prediction_id=require_text(row, "prediction_id", line_number),
                    program_id=require_text(row, "program_id", line_number),
                    execution_id=execution_id,
                    model_id=require_text(row, "model_id", line_number),
                    arm_id=require_text(row, "arm_id", line_number),
                    arm_group=require_text(row, "arm_group", line_number),
                    scope=scope,
                    metric_name=require_text(row, "metric_name", line_number),
                    x=x,
                    y=int(y_text),
                )
            )
    if not points:
        raise ValueError("points CSV contains no points")
    validate_points(points)
    return points


def validate_points(points: Iterable[Point]) -> None:
    series_metadata: dict[str, tuple[str, str, str, str]] = {}
    series_arms: dict[str, set[str]] = defaultdict(set)
    series_identities: set[tuple[str, str]] = set()
    execution_measurements: dict[tuple[str, str], float] = {}
    prediction_metadata: dict[str, tuple[str, str, str, int]] = {}
    prediction_ids: dict[tuple[str, str, str], str] = {}
    for point in points:
        if point.arm_id not in CANONICAL_DYNAMIC_ARMS:
            raise ValueError(
                f"series contains non-canonical arm {point.arm_id!r}"
            )
        metadata = (point.model_id, point.arm_group, point.scope, point.metric_name)
        previous_series = series_metadata.setdefault(point.series_id, metadata)
        if previous_series != metadata:
            raise ValueError(f"series {point.series_id!r} has inconsistent metadata")
        series_arms[point.series_id].add(point.arm_id)
        identity = point.program_id if point.scope == "static" else point.prediction_id
        series_identity = (point.series_id, identity)
        if series_identity in series_identities:
            raise ValueError(
                f"series {point.series_id!r} repeats analysis identity {identity!r}"
            )
        series_identities.add(series_identity)
        if point.scope == "dynamic":
            execution_metric = (point.execution_id, point.metric_name)
            previous_x = execution_measurements.setdefault(execution_metric, point.x)
            if previous_x != point.x:
                raise ValueError(
                    f"execution {point.execution_id!r} has inconsistent values for "
                    f"{point.metric_name!r}"
                )
        prediction = (point.model_id, point.arm_id, point.program_id, point.y)
        previous_prediction = prediction_metadata.setdefault(point.prediction_id, prediction)
        if previous_prediction != prediction:
            raise ValueError(
                f"prediction {point.prediction_id!r} has inconsistent metadata or outcome"
            )
        prediction_cell = (point.model_id, point.arm_id, point.program_id)
        previous_id = prediction_ids.setdefault(prediction_cell, point.prediction_id)
        if previous_id != point.prediction_id:
            raise ValueError(
                f"prediction cell {prediction_cell!r} uses multiple prediction_id values"
            )
    for series_id, arms in series_arms.items():
        scope = series_metadata[series_id][2]
        if scope == "static" and len(arms) != 1:
            raise ValueError(
                f"static series {series_id!r} combines multiple arms: {sorted(arms)}"
            )


def midranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=values.__getitem__)
    ranks = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start + 1
        while end < len(order) and values[order[end]] == values[order[start]]:
            end += 1
        rank = ((start + 1) + end) / 2.0
        for index in order[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def normalized_u(failure_ranks: Iterable[float], n_failure: int, n_success: int) -> float:
    rank_sum = math.fsum(failure_ranks)
    u_failure = rank_sum - n_failure * (n_failure + 1) / 2.0
    return u_failure / (n_failure * n_success)


def stable_series_seed(global_seed: int, series_id: str) -> int:
    digest = hashlib.sha256(f"{global_seed}\0{series_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def analyze_series(points: list[Point], permutations: int, global_seed: int) -> SeriesResult:
    first = points[0]
    n_failure = sum(point.y == 0 for point in points)
    n_success = len(points) - n_failure
    series_seed = stable_series_seed(global_seed, first.series_id)
    if n_failure == 0 or n_success == 0:
        return SeriesResult(
            first.series_id,
            first.model_id,
            first.arm_group,
            first.scope,
            first.metric_name,
            None,
            None,
            n_success,
            n_failure,
            len(points),
            permutations,
            series_seed,
            "ALL_WRONG" if n_success == 0 else "ALL_CORRECT",
        )
    ranks = midranks([point.x for point in points])
    theta_obs = normalized_u(
        (rank for rank, point in zip(ranks, points) if point.y == 0),
        n_failure,
        n_success,
    )
    rng = random.Random(series_seed)
    at_least_observed = 0
    for _ in range(permutations):
        failure_ranks = rng.sample(ranks, n_failure)
        theta_permuted = normalized_u(failure_ranks, n_failure, n_success)
        if theta_permuted + 1e-15 >= theta_obs:
            at_least_observed += 1
    p_value = (1 + at_least_observed) / (1 + permutations)
    return SeriesResult(
        first.series_id,
        first.model_id,
        first.arm_group,
        first.scope,
        first.metric_name,
        theta_obs,
        p_value,
        n_success,
        n_failure,
        len(points),
        permutations,
        series_seed,
        "OK",
    )


def load_logistic_specifications(path: Path) -> list[LogisticSpecification]:
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid logistic regression config: {error}") from error
    if not isinstance(config, dict):
        raise ValueError("logistic regression config root must be an object")
    declared = config.get("analyses")
    if not isinstance(declared, list) or not declared:
        raise ValueError("logistic regression config needs a nonempty analyses list")
    specifications = []
    identifiers = set()
    for index, item in enumerate(declared):
        if not isinstance(item, dict):
            raise ValueError(f"analyses[{index}] must be an object")
        required = ("regression_id", "metric_name", "scope", "arm_group")
        for field in required:
            if not isinstance(item.get(field), str) or not item[field]:
                raise ValueError(f"analyses[{index}].{field} must be nonempty")
        if item["regression_id"] in identifiers:
            raise ValueError(f"duplicate regression_id: {item['regression_id']}")
        identifiers.add(item["regression_id"])
        if item["scope"] not in {"static", "dynamic"}:
            raise ValueError(f"analyses[{index}].scope must be static or dynamic")
        include_arms = item.get("include_arms")
        if (
            not isinstance(include_arms, list)
            or not include_arms
            or not all(isinstance(arm, str) and arm for arm in include_arms)
            or len(include_arms) != len(set(include_arms))
        ):
            raise ValueError(
                f"analyses[{index}].include_arms must contain unique nonempty strings"
            )
        unknown_arms = sorted(set(include_arms) - set(CANONICAL_DYNAMIC_ARMS))
        if unknown_arms:
            raise ValueError(
                f"analyses[{index}].include_arms contains non-canonical arms: "
                + ", ".join(unknown_arms)
            )
        if item["scope"] == "dynamic" and set(include_arms) != set(
            CANONICAL_DYNAMIC_ARMS
        ):
            raise ValueError(
                f"analyses[{index}].include_arms must contain all four "
                "canonical arms for dynamic regression"
            )
        specifications.append(
            LogisticSpecification(
                item["regression_id"],
                item["metric_name"],
                item["scope"],
                item["arm_group"],
                tuple(include_arms),
            )
        )
    return specifications


def logistic_design(points: list[Point]):
    import numpy as np

    values = np.asarray([point.x for point in points], dtype=float)
    if np.any(values <= 0):
        raise ValueError("logistic regression requires positive metric values")
    matrix = np.column_stack([np.ones(len(points)), np.log2(values)])
    outcome = np.asarray([1 - point.y for point in points], dtype=float)
    return matrix, outcome


def fit_logistic_parameters(matrix, outcome):
    import numpy as np
    from scipy.optimize import minimize
    from scipy.special import expit

    def objective(value):
        linear = matrix @ value
        return float(np.sum(np.logaddexp(0, linear) - outcome * linear))

    optimized = minimize(
        objective,
        np.zeros(matrix.shape[1]),
        method="BFGS",
        options={"gtol": 1e-8, "maxiter": 500},
    )
    parameters = np.asarray(optimized.x, dtype=float)
    if (
        not np.all(np.isfinite(parameters))
        or not np.isfinite(optimized.fun)
        or np.max(np.abs(parameters)) > 50
    ):
        raise ValueError("MLE logistic regression did not converge")
    probability = np.clip(expit(matrix @ parameters), 1e-10, 1 - 1e-10)
    weights = probability * (1 - probability)
    information = matrix.T @ (weights[:, None] * matrix)
    covariance = np.linalg.inv(information)
    if not np.all(np.isfinite(covariance)):
        raise ValueError("MLE covariance is not finite")
    return parameters, covariance


def fit_logistic_series(
    specification: LogisticSpecification,
    model_id: str,
    points: list[Point],
) -> LogisticFit:
    import numpy as np
    from scipy.stats import norm

    matrix, outcome = logistic_design(points)
    minority = min(int(outcome.sum()), int(len(outcome) - outcome.sum()))
    if minority == 0:
        return LogisticFit(
            specification, model_id, points, None, None, None, None, None, None,
            "SINGLE_OUTCOME",
        )
    try:
        parameters, covariance = fit_logistic_parameters(matrix, outcome)
    except (ValueError, ArithmeticError):
        return LogisticFit(
            specification, model_id, points, None, None, None, None, None, None,
            "NOT_ESTIMATED",
        )
    se_beta1 = math.sqrt(float(covariance[1, 1]))
    z_score = float(parameters[1]) / se_beta1
    p_value = float(2 * norm.sf(abs(z_score)))
    lower = float(parameters[1]) - 1.959963984540054 * se_beta1
    upper = float(parameters[1]) + 1.959963984540054 * se_beta1
    return LogisticFit(
        specification,
        model_id,
        points,
        parameters,
        covariance,
        se_beta1,
        math.exp(lower),
        math.exp(upper),
        p_value,
        "OK",
    )


def analyze_logistic_regressions(
    points: list[Point],
    specifications: list[LogisticSpecification],
) -> list[LogisticFit]:
    fits = []
    for specification in specifications:
        selected = [
            point
            for point in points
            if point.metric_name == specification.metric_name
            and point.scope == specification.scope
            and point.arm_id in specification.include_arms
        ]
        if not selected:
            raise ValueError(
                f"regression {specification.regression_id!r} selected no points"
            )
        for model_id in sorted({point.model_id for point in selected}):
            model_points = sorted(
                (point for point in selected if point.model_id == model_id),
                key=lambda point: (point.program_id, point.arm_id, point.prediction_id),
            )
            fits.append(
                fit_logistic_series(specification, model_id, model_points)
            )
    return fits


def logistic_point_rows(fits: list[LogisticFit]) -> list[dict[str, str]]:
    rows = []
    for fit in fits:
        for point in fit.points:
            rows.append(
                {
                    "regression_id": fit.specification.regression_id,
                    "prediction_id": point.prediction_id,
                    "program_id": point.program_id,
                    "execution_id": point.execution_id,
                    "model_id": point.model_id,
                    "arm_id": point.arm_id,
                    "arm_group": fit.specification.arm_group,
                    "scope": fit.specification.scope,
                    "metric_name": fit.specification.metric_name,
                    "x": format(point.x, ".17g"),
                    "wrong": str(1 - point.y),
                }
            )
    return rows


def logistic_result_rows(fits: list[LogisticFit]) -> list[dict[str, str]]:
    rows = []
    for fit in fits:
        rows.append(
            {
                "regression_id": fit.specification.regression_id,
                "model_id": fit.model_id,
                "arm_group": fit.specification.arm_group,
                "scope": fit.specification.scope,
                "metric_name": fit.specification.metric_name,
                "included_arms": ",".join(fit.specification.include_arms),
                "n": str(len(fit.points)),
                "n_wrong": str(fit.n_wrong),
                "beta0": "" if fit.beta0 is None else format(fit.beta0, ".17g"),
                "beta1": "" if fit.beta1 is None else format(fit.beta1, ".17g"),
                "se_beta1": "" if fit.se_beta1 is None else format(fit.se_beta1, ".17g"),
                "odds_ratio": "" if fit.odds_ratio is None else format(fit.odds_ratio, ".17g"),
                "ci_low": "" if fit.ci_low is None else format(fit.ci_low, ".17g"),
                "ci_high": "" if fit.ci_high is None else format(fit.ci_high, ".17g"),
                "p_value": "" if fit.p_value is None else format(fit.p_value, ".17g"),
                "status": fit.status,
            }
        )
    return rows


def logistic_curve_rows(fits: list[LogisticFit]) -> list[dict[str, str]]:
    import numpy as np
    from scipy.special import expit

    rows = []
    for fit in fits:
        if fit.status != "OK":
            continue
        minimum = min(point.x for point in fit.points)
        maximum = max(point.x for point in fit.points)
        grid_log2 = np.linspace(math.log2(minimum), math.log2(maximum), 240)
        design = np.column_stack([np.ones(len(grid_log2)), grid_log2])
        fitted = expit(design @ fit.parameters)
        eta = design @ fit.parameters
        eta_variance = np.einsum("ij,jk,ik->i", design, fit.covariance, design)
        eta_margin = 1.959963984540054 * np.sqrt(np.maximum(0, eta_variance))
        lower = expit(eta - eta_margin)
        upper = expit(eta + eta_margin)
        for index, (log2_x, probability, low, high) in enumerate(
            zip(grid_log2, fitted, lower, upper, strict=True)
        ):
            rows.append(
                {
                    "regression_id": fit.specification.regression_id,
                    "model_id": fit.model_id,
                    "arm_group": fit.specification.arm_group,
                    "scope": fit.specification.scope,
                    "metric_name": fit.specification.metric_name,
                    "grid_index": str(index),
                    "x": format(2 ** float(log2_x), ".17g"),
                    "p_wrong": format(float(probability), ".17g"),
                    "ci_low": format(float(low), ".17g"),
                    "ci_high": format(float(high), ".17g"),
                }
            )
    return rows


def format_logistic_p(value: float | None) -> str:
    if value is None:
        return "NOT_ESTIMATED"
    return "< 0.0001" if value < 0.0001 else f"{value:.4f}"


def markdown_logistic_regressions(fits: list[LogisticFit]) -> str:
    lines = [
        "# Logistic regressions",
        "",
        "Each section asks how the odds of `wrong=1` change when the named",
        "metric doubles. `OR` is that multiplier: above 1 means greater error",
        "odds at larger values. The 95% interval and two-sided p-value come",
        "from the standard maximum-likelihood logistic model. These are",
        "associations, not causal effects, and p-values are not adjusted for",
        "multiple testing.",
        "",
    ]
    by_specification: dict[str, list[LogisticFit]] = defaultdict(list)
    for fit in fits:
        by_specification[fit.specification.regression_id].append(fit)
    for regression_id in sorted(by_specification):
        selected = by_specification[regression_id]
        specification = selected[0].specification
        lines.extend(
            [
                f"## `{specification.metric_name}` — {specification.arm_group}",
                "",
                "Included arms: "
                + ", ".join(f"`{arm}`" for arm in specification.include_arms)
                + ".",
                "",
                "`n` counts the pooled `(metric value, wrong-or-correct)` points",
                "included in this regression. Arms are not separate statistical",
                "groups; `arm_id` remains only for auditing the selected points.",
                "",
                "| Model | n | Wrong | OR per doubling (95% CI) | p |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for fit in selected:
            estimate = (
                "NOT_ESTIMATED"
                if fit.odds_ratio is None
                else f"{fit.odds_ratio:.2f} ({fit.ci_low:.2f}–{fit.ci_high:.2f})"
            )
            lines.append(
                f"| `{fit.model_id}` | {len(fit.points)} | {fit.n_wrong} | "
                f"{estimate} | {format_logistic_p(fit.p_value)} |"
            )
        lines.append("")
    return "\n".join(lines)


def write_csv(path: Path, fieldnames: Iterable[str], rows: Iterable[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def format_p_value(p_value: float, permutations: int) -> str:
    """Report the permutation floor as an inequality.

    `(1 + 0) / (1 + permutations)` is the smallest value the test can return, so
    printing its digits would claim precision the test does not have.
    """
    floor = 1 / (1 + permutations)
    if p_value <= floor:
        return f"< {floor:.4f}"
    return f"{p_value:.4f}"


def format_outcome_only(result: SeriesResult) -> str:
    """State the outcome that left theta undefined, rather than a status word."""
    total = result.n_success + result.n_failure
    return f"— ({result.n_success}/{total} correct)"


def format_result(result: SeriesResult | None) -> str:
    if result is None:
        return "no data"
    if result.status != "OK":
        return format_outcome_only(result)
    assert result.theta_obs is not None and result.p_value is not None
    return (
        f"({result.theta_obs:.2f},"
        f" p {format_p_value(result.p_value, result.permutations)})"
    )


def markdown_association_tables(results: list[SeriesResult], scope: str) -> str:
    selected = [result for result in results if result.scope == scope]
    title = "Static factor association tables" if scope == "static" else "Dynamic factor association tables"
    lines = [
        f"# {title}",
        "",
        "Cells show `(theta_obs, p)` for one metric, arm, and model.",
        "",
        "- `theta_obs`: how often a failed prediction has a larger metric value",
        "  than a successful one, ties counting half. `0.5` means no ordering",
        "  tendency; above `0.5` means failures had larger values.",
        "- `p`: the share of 10,000 shuffled correct/wrong labelings that",
        "  separated the two groups at least as much as the observed data.",
        "  `< 0.0001` is the smallest value this many shuffles can produce and",
        "  means no shuffle reached the observed separation.",
        "- `— (k/n correct)`: every prediction in the series had the same",
        "  outcome, so there is no failure-success pair to order and",
        "  `theta_obs` does not exist. The score itself is a real result.",
        "- `no data`: this model and arm produced no gradable prediction,\n"
        "  either because it was never run or because every answer was\n"
        "  ungradable. It is not a score of zero.",
        "",
    ]
    metrics = sorted({result.metric_name for result in selected})
    models = sorted({result.model_id for result in selected})
    lookup = {
        (result.metric_name, result.arm_group, result.model_id): result
        for result in selected
    }
    for metric in metrics:
        groups = list(
            dict.fromkeys(
                result.arm_group
                for result in selected
                if result.metric_name == metric
            )
        )
        lines.extend(
            [
                f"## `{metric}`",
                "",
                METRIC_DESCRIPTIONS.get(
                    metric,
                    f"Numeric factor `{metric}` supplied by the upstream measurement.",
                ),
                "",
                "| Arm group | " + " | ".join(models) + " |",
                "| --- | " + " | ".join("---" for _ in models) + " |",
            ]
        )
        for group in groups:
            cells = [format_result(lookup.get((metric, group, model))) for model in models]
            lines.append("| " + group + " | " + " | ".join(cells) + " |")
        lines.append("")
    return "\n".join(lines)


@dataclass(frozen=True)
class CrossFactorResult:
    model_id: str
    static_metric: str
    dynamic_metric: str
    static_threshold: float
    dynamic_threshold: float
    cells: dict[tuple[str, str], tuple[int, int]]
    difference: float | None
    p_value: float | None
    permutations: int
    seed: int
    status: str


def cross_factor_analysis(
    points: list[Point],
    static_metric: str,
    dynamic_metric: str,
    permutations: int,
    global_seed: int,
) -> list[CrossFactorResult]:
    """Ask which of two factors dominates when they disagree.

    The declared question is whether a structurally simple program with a long
    execution is harder to predict than a structurally complex program with a
    short one. Only the two disagreeing cells answer it; the agreeing cells are
    reported for context and are not tested.

    Thresholds are the medians of each factor over all measured predictions, so
    `high` means the same thing for every model.
    """
    by_prediction: dict[str, dict[str, float]] = defaultdict(dict)
    outcome: dict[str, tuple[str, int]] = {}
    for point in points:
        if point.metric_name in (static_metric, dynamic_metric):
            by_prediction[point.prediction_id][point.metric_name] = point.x
            outcome[point.prediction_id] = (point.model_id, point.y)
    paired = {
        prediction: values
        for prediction, values in by_prediction.items()
        if static_metric in values and dynamic_metric in values
    }
    if not paired:
        return []
    static_threshold = median(sorted(values[static_metric] for values in paired.values()))
    dynamic_threshold = median(
        sorted(values[dynamic_metric] for values in paired.values())
    )

    grouped: dict[str, dict[tuple[str, str], list[int]]] = defaultdict(
        lambda: defaultdict(list)
    )
    for prediction, values in paired.items():
        model, correct = outcome[prediction]
        cell = (
            "high" if values[static_metric] > static_threshold else "low",
            "high" if values[dynamic_metric] > dynamic_threshold else "low",
        )
        grouped[model][cell].append(correct)

    results = []
    for model in sorted(grouped):
        cells = grouped[model]
        simple_long = cells.get(("low", "high"), [])
        complex_short = cells.get(("high", "low"), [])
        summary = {
            key: (sum(values), len(values))
            for key, values in cells.items()
        }
        if not simple_long or not complex_short:
            results.append(
                CrossFactorResult(
                    model, static_metric, dynamic_metric,
                    static_threshold, dynamic_threshold, summary,
                    None, None, permutations, 0, "NO_DISAGREEING_CELL",
                )
            )
            continue
        observed = sum(simple_long) / len(simple_long) - sum(complex_short) / len(
            complex_short
        )
        pool = simple_long + complex_short
        seed = stable_series_seed(global_seed, f"cross::{model}::{static_metric}::{dynamic_metric}")
        rng = random.Random(seed)
        at_least_observed = 0
        for _ in range(permutations):
            shuffled = rng.sample(pool, len(pool))
            left = shuffled[: len(simple_long)]
            right = shuffled[len(simple_long) :]
            if sum(left) / len(left) - sum(right) / len(right) <= observed:
                at_least_observed += 1
        results.append(
            CrossFactorResult(
                model, static_metric, dynamic_metric,
                static_threshold, dynamic_threshold, summary,
                observed, (1 + at_least_observed) / (1 + permutations),
                permutations, seed, "OK",
            )
        )
    return results


def median(ordered: list[float]) -> float:
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def markdown_cross_factor(results: list[CrossFactorResult]) -> str:
    if not results:
        return "# Cross-factor comparison\n\nNo prediction carried both factors.\n"
    first = results[0]
    lines = [
        "# Cross-factor comparison",
        "",
        f"Does a structurally simple program that runs a long time defeat a model",
        f"more often than a structurally complex program that runs briefly?",
        "",
        f"Every prediction carrying both `{first.static_metric}` and",
        f"`{first.dynamic_metric}` is placed in one of four cells by whether each",
        "factor is above its median. The medians are computed once over all such",
        f"predictions — `{first.static_metric}` at {first.static_threshold:g} and",
        f"`{first.dynamic_metric}` at {first.dynamic_threshold:g} — so `high` means",
        "the same thing for every model.",
        "",
        "Only the two disagreeing cells answer the question. The agreeing cells",
        "are shown for context and are not tested.",
        "",
        "Each cohort cell is `correct/eligible (accuracy)`. `difference` is the",
        "first cohort's accuracy minus the second's, in percentage points. `p`",
        "is the share of shuffled labels that produced a difference at least as",
        "negative; smaller values support the declared first-cohort-is-harder",
        "direction.",
        "",
        "| Model | simple source, long run | complex source, short run | difference | p |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        simple_long = result.cells.get(("low", "high"), (0, 0))
        complex_short = result.cells.get(("high", "low"), (0, 0))

        def cell(value: tuple[int, int]) -> str:
            correct, total = value
            if not total:
                return "no data"
            return f"{correct}/{total} ({100 * correct / total:.1f}%)"

        if result.status != "OK":
            lines.append(
                f"| `{result.model_id}` | {cell(simple_long)} | {cell(complex_short)}"
                " | — | one cell is empty |"
            )
            continue
        lines.append(
            f"| `{result.model_id}` | {cell(simple_long)} | {cell(complex_short)}"
            f" | {100 * result.difference:+.1f} pt"
            f" | {format_p_value(result.p_value, result.permutations)} |"
        )
    lines.extend(
        [
            "",
            "`difference` is the first cell's accuracy minus the second's. A"
            " negative value means the long-running simple program was harder,"
            " which is the declared direction.",
            "",
            "`p` is the share of label shuffles between those two cells that"
            " reproduced a difference at least as negative. This is one further"
            " test on the same data and is not corrected for the factor tests"
            " reported elsewhere.",
            "",
            "For context, the agreeing cells:",
            "",
            "| Model | simple source, short run | complex source, long run |",
            "| --- | ---: | ---: |",
        ]
    )
    for result in results:
        def cell(key: tuple[str, str]) -> str:
            correct, total = result.cells.get(key, (0, 0))
            if not total:
                return "no data"
            return f"{correct}/{total} ({100 * correct / total:.1f}%)"

        lines.append(
            f"| `{result.model_id}` | {cell(('low', 'low'))} | {cell(('high', 'high'))} |"
        )
    lines.append("")
    return "\n".join(lines)


def markdown_supported_associations(results: list[SeriesResult]) -> str:
    """Audit evidence: every series meeting the predeclared rule, in one place."""
    supported = sorted(
        (
            result
            for result in results
            if result.status == "OK"
            and result.theta_obs is not None
            and result.p_value is not None
            and result.theta_obs > 0.5
            and result.p_value < 0.05
        ),
        key=lambda result: (-result.theta_obs, result.metric_name, result.model_id),
    )
    lines = [
        "# Supported associations",
        "",
        "Every statistical series meeting the predeclared rule `theta_obs > 0.5`",
        "and unadjusted permutation `p_value < 0.05`, strongest ordering first.",
        "This is the audit list behind the analysis report; read the report for",
        "what it means and the metric support matrix for cross-model consistency.",
        "",
        "A row here is one model, one arm group, and one metric. Support for",
        "only one model is weak cross-model evidence even with a small p-value,",
        "because these p-values are not corrected for multiple testing.",
        "",
        "| Metric | Model | Arm group | theta_obs | p | Correct | Wrong | n |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for result in supported:
        lines.append(
            f"| `{result.metric_name}` | `{result.model_id}` | {result.arm_group} "
            f"| {result.theta_obs:.2f} "
            f"| {format_p_value(result.p_value, result.permutations)} "
            f"| {result.n_success} | {result.n_failure} | {result.n_total} |"
        )
    lines.extend(
        [
            "",
            "Column meanings:",
            "",
            "- `theta_obs`: how often a failed prediction had the larger metric",
            "  value than a successful one, ties counting half.",
            "- `p`: share of 10,000 shuffled labelings at least as separated as",
            "  the observed data. `< 0.0001` is the floor this many shuffles can",
            "  reach and means no shuffle matched the observed separation.",
            "- `Correct` / `Wrong`: predictions in the series carrying a numeric",
            "  value for this metric. Predictions without a value are not counted.",
            "- `n`: `Correct + Wrong`, the series denominator.",
            "",
            "Full precision for every series, supported or not, is in",
            "`series-results.csv`.",
            "",
        ]
    )
    return "\n".join(lines)


EXCLUSION_CAUSES = {
    "not_run": "never sent to the model",
    "no_response": "sent, but the model returned no gradable answer",
}


def markdown_exclusion_note(manifest: dict | None) -> list[str]:
    """State, under every accuracy table, what the denominator leaves out."""
    if not manifest:
        return []
    counts = manifest.get("excluded_by_model_arm_status") or {}
    if not counts:
        return []
    by_model: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for key, value in counts.items():
        model, _, status = key.split("::")
        by_model[model][status] += int(value)
    statuses = sorted({s for row in by_model.values() for s in row})
    lines = [
        "",
        "## What these denominators leave out",
        "",
        "A prediction counts only when the model returned an answer that could",
        "be graded. Records below are excluded from every cell above: they are",
        "**not** counted as wrong, so each denominator is smaller than the arm's",
        "problem count.",
        "",
        "| Model | " + " | ".join(f"`{s}`" for s in statuses) + " | total excluded |",
        "| --- | " + " | ".join("---:" for _ in statuses) + " | ---: |",
    ]
    for model in sorted(by_model):
        row = by_model[model]
        total = sum(row.values())
        cells = " | ".join(str(row.get(s, 0)) for s in statuses)
        lines.append(f"| `{model}` | {cells} | {total} |")
    lines.extend(["", "Meaning of each cause:", ""])
    for status in statuses:
        lines.append(f"- `{status}`: {EXCLUSION_CAUSES.get(status, 'see the cohort manifest')}.")
    lines.extend(
        [
            "",
            "Excluding a `no_response` record is optimistic for a model that used",
            "its whole token budget without answering: that failure is removed",
            "rather than counted against it. Excluding a provider or transport",
            "failure is correct, because it measures the provider, not the model.",
            "The per-arm split is in `cohort-manifest.json`.",
            "",
        ]
    )
    return lines


def markdown_measurement_coverage(manifest: dict | None) -> str | None:
    coverage = (manifest or {}).get("metric_measurement_coverage")
    if not coverage:
        return None
    records = coverage.get("records") or []
    if not records:
        return None
    arms = list(dict.fromkeys(record["arm_id"] for record in records))
    metrics = list(dict.fromkeys(record["metric_name"] for record in records))
    lookup = {
        (record["arm_id"], record["metric_name"]): record for record in records
    }
    has_lower_bounds = any(int(record.get("lower_bound", 0)) for record in records)
    lines = [
        "# Dynamic metric measurement coverage",
        "",
        "This table answers which program profiles actually carry each dynamic",
        "metric before model outcomes are joined. Rows are experiment arms and",
        (
            "columns are metrics. Every cell is `exact + >= / selected (usable)` in"
            if has_lower_bounds
            else "columns are metrics. Every cell is `measured / selected (coverage)` in"
        ),
        "program profiles; it is not an accuracy, model-prediction, or execution",
        "count.",
    ]
    if has_lower_bounds:
        lines.extend(
            [
                "",
                "Exact measurements and retained numeric bounds are both used.",
            ]
        )
    lines.extend(
        [
            "Missing values are never treated as zero. The reason table below",
            "separates an adapter that did not run from a measurement that failed.",
            "",
            "| Arm | " + " | ".join(metrics) + " |",
            "| --- | " + " | ".join("---:" for _ in metrics) + " |",
        ]
    )
    for arm in arms:
        cells = []
        for metric in metrics:
            record = lookup[(arm, metric)]
            measured = int(record["measured"])
            lower_bound = int(record.get("lower_bound", 0))
            usable = measured + lower_bound
            selected = int(record["selected_profiles"])
            percentage = 100 * usable / selected if selected else 0
            if has_lower_bounds:
                cells.append(
                    f"{measured} exact + {lower_bound} >= / {selected} "
                    f"({percentage:.1f}%)"
                )
            else:
                cells.append(f"{measured} / {selected} ({percentage:.1f}%)")
        lines.append(f"| `{arm}` | " + " | ".join(cells) + " |")

    reasons: dict[tuple[str, str], dict[str, object]] = {}
    for record in records:
        for reason, count in (record.get("unavailable_by_reason") or {}).items():
            key = (record["metric_name"], reason)
            summary = reasons.setdefault(key, {"count": 0, "arms": []})
            summary["count"] = int(summary["count"]) + int(count)
            summary["arms"].append(f"{record['arm_id']} ({count})")
    definitions = coverage.get("reason_definitions") or {}
    lines.extend(
        [
            "",
            "## Why measurements are unavailable",
            "",
            "Rows below count unavailable program profiles, not model predictions.",
            "`Affected arms` gives the profile count per arm. Prompt/instrumented",
            "arms that reuse one execution are still separate profile rows here.",
            "",
            "| Metric | Status or reason | Profiles | Affected arms | Meaning |",
            "| --- | --- | ---: | --- | --- |",
        ]
    )
    for (metric, reason), summary in sorted(reasons.items()):
        lines.append(
            f"| `{metric}` | `{reason}` | {summary['count']} | "
            f"{', '.join(summary['arms'])} | {definitions.get(reason, reason)} |"
        )
    notes = coverage.get("notes") or []
    if notes:
        lines.extend(["", "Notes:", ""])
        lines.extend(f"- {note}" for note in notes)
    lines.extend(["", "Metric meanings:", ""])
    for metric in metrics:
        description = METRIC_DESCRIPTIONS.get(metric)
        if description:
            lines.append(f"- `{metric}`: {description[0].lower() + description[1:]}")
    lines.append("")
    return "\n".join(lines)


DATA_DICTIONARY = """# Data files

Every file here is generated. Do not edit them by hand; rerun the analysis.

Values are written at full precision because these files are the machine-readable
source. Reader-facing documents round them.

## `measurement-coverage.md`

Per-arm dynamic metric availability before model outcomes are joined. Every
cell divides numeric measurements by selected profiles. The adjacent reason
table distinguishes an adapter that did not run from a measurement that failed.

## `raw-points.csv`

One row per (prediction, metric). This is the input to every statistic.

| Column | Meaning |
| --- | --- |
| `series_id` | The statistical series this point belongs to. |
| `prediction_id` | One graded model answer. Stable across metrics, so the same answer keeps one id when joined to multiple metrics. |
| `program_id` | The source program the prediction is about. |
| `execution_id` | One exact source-plus-input runtime identity. Empty for static points. |
| `model_id` | The configured model and reasoning setting. |
| `arm_id` | The real arm the prediction came from. |
| `arm_group` | The label the series is reported under: the arm itself for static series, `all-arms` for the four-arm dynamic pool. |
| `scope` | `static` for source metrics, `dynamic` for execution metrics. |
| `metric_name` | Which factor this row measures. |
| `x` | The measured factor value. |
| `y` | `1` if the prediction was correct, `0` if it was wrong. |

## `series-results.csv`

One row per statistical series: one model, one arm group, one metric.

| Column | Meaning |
| --- | --- |
| `series_id` | Matches `raw-points.csv`. |
| `model_id`, `arm_group`, `scope`, `metric_name` | What the series covers. |
| `theta_obs` | How often a failed prediction had the larger metric value than a successful one, ties counting half. `0.5` means no ordering tendency. Empty when the series has only one outcome. |
| `p_value` | Share of shuffled correct/wrong labelings that separated the groups at least as much as the observed data. The smallest possible value is `1 / (1 + permutations)`; at that floor no shuffle reached the observed separation. Empty when `theta_obs` is empty. |
| `n_success` | Correct predictions carrying a measurement for this metric. |
| `n_failure` | Wrong predictions carrying a measurement for this metric. |
| `n_total` | `n_success + n_failure`. |
| `permutations` | Label shuffles performed. |
| `series_seed` | Seed for this series, derived from the global seed and `series_id`, so a rerun reproduces it exactly. |
| `status` | `OK`: theta and p were computed. `ALL_WRONG` / `ALL_CORRECT`: every prediction had the same outcome, so no failure-success pair exists and theta is undefined. That is a real result about the model, not a measurement problem. |

## Optional logistic-regression files

Produced only with `--logistic-regression-config`:

- `logistic-regression-points.csv` contains the selected numeric observations,
  with `wrong=1-y` and the real arm retained.
- `logistic-regression-results.csv` contains one model fit per declared
  regression. `odds_ratio=exp(beta1)` is the error-odds multiplier when the
  metric doubles. `se_beta1`, `ci_low`, `ci_high`, and `p_value` come from the
  standard maximum-likelihood logistic model and its covariance matrix.
- `logistic-regression-curves.csv` contains the fitted error probability and
  model-based 95% band on a fixed x grid. Chart generation reads these values and
  does not refit the model.
- `logistic-regressions.md` is the reader-facing OR, 95% CI, and p-value table.

## `chart-data.csv`

The generated bins drawn in the figures.

| Column | Meaning |
| --- | --- |
| `series_id`, `model_id`, `arm_group`, `scope`, `metric_name` | Which series the bin belongs to. |
| `bin_index` | Bin position, lowest metric values first. |
| `x` | Representative metric value for the bin. |
| `accuracy` | Share correct within the bin. |
| `wilson_low`, `wilson_high` | Wilson 95% interval for that share. Wide bars mean few predictions. |
| `n_success`, `n_failure`, `n_total` | Counts behind the bin. |

## `overall-accuracy.csv`

Accuracy per arm and model, on each cell's own eligible predictions.

| Column | Meaning |
| --- | --- |
| `arm_id` | The arm. |
| `arm_group` | Its presentation label. |
| `model_id` | The model and reasoning setting. |
| `correct` | Correct predictions. |
| `total` | Predictions that produced a gradable answer. Differs between arms. |
| `accuracy` | `correct / total`. |

## `cross-factor.md`

Produced only when a static/dynamic pair is requested. Splits every prediction
carrying both factors at each factor's median and compares the two cells where
the factors disagree, answering which kind of complexity dominates. The agreeing
cells are reported for context and are not tested.

## `matched-accuracy.csv`

Accuracy restricted, per model, to programs gradable in every arm that model
ran, so its arms share one denominator. Use it to compare arms; use
`overall-accuracy.csv` to see what each arm actually produced.

| Column | Meaning |
| --- | --- |
| `model_id` | The model and reasoning setting. |
| `arm_id`, `arm_group` | The arm and its label. |
| `arm_count` | How many arms this model ran. A model with fewer arms has an easier matched set and its rows are not comparable to a four-arm model's. |
| `correct` | Correct predictions within the matched set. |
| `total` | Size of the matched set. Identical across one model's arms. |
| `accuracy` | `correct / total`. Empty when no program was gradable in every arm. |
"""


def arm_coverage(points: list[Point]) -> dict[tuple[str, str, str], list[str]]:
    """Which real arms each model contributed to a group, so a pooled label cannot hide partial coverage."""
    coverage: dict[tuple[str, str, str], set[str]] = defaultdict(set)
    for point in points:
        coverage[(point.scope, point.arm_group, point.model_id)].add(point.arm_id)
    return {key: sorted(value) for key, value in coverage.items()}


def coverage_note(
    coverage: dict[tuple[str, str, str], list[str]] | None,
    scope: str,
    group: str,
    models: list[str],
) -> list[str]:
    """Warn when a pooled group means different arms for different models."""
    if not coverage:
        return []
    per_model = {model: coverage.get((scope, group, model), []) for model in models}
    widths = {len(arms) for arms in per_model.values() if arms}
    if len(widths) < 2:
        return []
    widest = max(widths)
    partial = sorted(
        (model, arms) for model, arms in per_model.items() if 0 < len(arms) < widest
    )
    lines = [
        f"The `{group}` label does not cover the same arms for every model, so"
        " these columns are not measuring equal workloads:",
        "",
    ]
    for model, arms in partial:
        listed = ", ".join(f"`{arm}`" for arm in arms)
        lines.append(
            f"- `{model}` pools {len(arms)} of {widest} arms ({listed}), so its"
            " values describe that narrower mix."
        )
    lines.append("")
    return lines


def metric_matrix_eligible_totals(
    results: list[SeriesResult], manifest: dict | None
) -> dict[tuple[str, str, str], int]:
    if not manifest:
        return {}
    included = manifest.get("included_by_model_arm") or {}
    if not isinstance(included, dict):
        return {}
    arm_labels = manifest.get("arm_labels") or {}
    dynamic_arms = (manifest.get("dynamic_pooling") or {}).get("arms") or []
    totals: dict[tuple[str, str, str], int] = {}
    for result in results:
        if result.scope == "dynamic":
            arms = dynamic_arms
        else:
            arms = [
                arm
                for arm, label in arm_labels.items()
                if label == result.arm_group or arm == result.arm_group
            ]
        total = sum(int(included.get(f"{result.model_id}::{arm}", 0)) for arm in arms)
        if total:
            totals[(result.scope, result.arm_group, result.model_id)] = total
    return totals


def validate_dynamic_pooling_manifest(points: list[Point], manifest: dict | None) -> None:
    if not any(point.scope == "dynamic" for point in points):
        return
    if not manifest:
        return
    arms = (manifest.get("dynamic_pooling") or {}).get("arms")
    if tuple(arms or ()) != CANONICAL_DYNAMIC_ARMS:
        expected = ", ".join(CANONICAL_DYNAMIC_ARMS)
        raise ValueError(
            "cohort manifest dynamic_pooling.arms must be " + expected
        )


def markdown_metric_matrix(
    results: list[SeriesResult],
    coverage: dict[tuple[str, str, str], list[str]] | None = None,
    eligible_totals: dict[tuple[str, str, str], int] | None = None,
) -> str:
    """One metric-by-model table per group, ordered by how often each metric is supported."""
    model_count = len({result.model_id for result in results})
    lines = [
        "# Metric support matrix",
        "",
        "One row is one measured factor and one column is one model. Every",
        "computed cell explicitly reports `theta`, `p`, and `n`:",
        "",
        "- `theta`: how often a failed prediction had the larger value, ties",
        "  counting half. `0.5` means no ordering tendency; values below `0.5`",
        "  mean failures had smaller values.",
        "- `p`: the one-sided permutation p-value. `< 0.0001` is the floor for",
        "  10,000 shuffles and means no shuffle reached the observed separation.",
        "- `n=measured/eligible`: predictions carrying this metric divided by all",
        "  gradable predictions for that model and group. When no cohort manifest",
        "  supplies the denominator, the cell shows measured `n` only. Here, a",
        "  measured point carries one numeric value for the metric.",
        "",
        "`n` counts prediction rows, not distinct programs or executions. Several",
        "predictions may share one execution measurement. Different `n` values",
        "mean the cells analyze different measured subsets; missing measurements",
        "and ungradable predictions are never converted to zero.",
        "",
        "**Bold** marks the predeclared rule `theta_obs > 0.5` and unadjusted",
        "`p_value < 0.05`. The `supported` column counts how many models met it,",
        "which is the cross-model consistency of that factor. Rows are ordered by",
        "that count, so the factors carrying the most evidence appear first.",
        "",
        f"A factor supported for one model out of {model_count} is weak evidence even when",
        "its single p-value is small, because these p-values are unadjusted.",
        "Read `theta_obs` for effect size and the `supported` count for",
        "consistency; neither alone ranks a factor.",
        "",
    ]
    for scope, group in sorted({(result.scope, result.arm_group) for result in results}):
        selected = [
            result
            for result in results
            if result.scope == scope and result.arm_group == group
        ]
        models = sorted({result.model_id for result in selected})
        lookup = {(result.metric_name, result.model_id): result for result in selected}
        metrics = sorted(
            {result.metric_name for result in selected},
            key=lambda metric: (
                -sum(
                    1
                    for model in models
                    if (found := lookup.get((metric, model))) is not None
                    and found.status == "OK"
                    and found.theta_obs > 0.5
                    and found.p_value < 0.05
                ),
                metric,
            ),
        )
        lines.extend(
            [
                f"## {scope}: {group}",
                "",
                "| Metric | " + " | ".join(models) + " | supported |",
                "| --- | " + " | ".join("---" for _ in models) + " | ---: |",
            ]
        )
        for metric in metrics:
            cells = []
            supported = 0
            for model in models:
                result = lookup.get((metric, model))
                if result is None:
                    cells.append("no data")
                elif result.status != "OK":
                    cells.append(format_outcome_only(result))
                else:
                    p_text = format_p_value(result.p_value, result.permutations)
                    eligible = (eligible_totals or {}).get((scope, group, model))
                    n_text = (
                        f"{result.n_total}/{eligible}" if eligible else str(result.n_total)
                    )
                    cell = (
                        f"theta={result.theta_obs:.2f}<br>"
                        f"p {p_text}<br>n={n_text}"
                    )
                    if result.theta_obs > 0.5 and result.p_value < 0.05:
                        supported += 1
                        cell = f"**{cell}**"
                    cells.append(cell)
            lines.append(
                f"| `{metric}` | "
                + " | ".join(cells)
                + f" | {supported}/{len(models)} |"
            )
        lines.append("")
        lines.extend(coverage_note(coverage, scope, group, models))
        for metric in metrics:
            description = METRIC_DESCRIPTIONS.get(metric)
            if description:
                lines.append(f"- `{metric}`: {description[0].lower() + description[1:]}")
        lines.append("")
    return "\n".join(lines)


def deduplicated_predictions(
    points: list[Point],
) -> tuple[dict[str, Point], dict[str, str]]:
    predictions: dict[str, Point] = {}
    prediction_labels: dict[str, str] = {}
    for point in points:
        predictions.setdefault(point.prediction_id, point)
        if point.scope == "static" or point.prediction_id not in prediction_labels:
            prediction_labels[point.prediction_id] = (
                point.arm_group if point.scope == "static" else point.arm_id
            )
    return predictions, prediction_labels


def accuracy_rows(points: list[Point]) -> list[dict[str, str]]:
    predictions, prediction_labels = deduplicated_predictions(points)
    totals: dict[tuple[str, str, str], list[int]] = defaultdict(lambda: [0, 0])
    for point in predictions.values():
        cell = totals[
            (
                point.arm_id,
                prediction_labels[point.prediction_id],
                point.model_id,
            )
        ]
        cell[0] += point.y
        cell[1] += 1
    return [
        {
            "arm_id": arm,
            "arm_group": arm_group,
            "model_id": model,
            "correct": str(correct),
            "total": str(total),
            "accuracy": format(correct / total, ".12g"),
        }
        for (arm, arm_group, model), (correct, total) in sorted(totals.items())
    ]


def matched_accuracy_rows(points: list[Point]) -> list[dict[str, str]]:
    """Per-model arm accuracy restricted to programs eligible in every arm.

    Arm denominators differ whenever an answer was ungradable, so raw armwise
    gaps mix an arm effect with a coverage effect. Restricting to the matched
    cohort removes the coverage effect but drops the hardest cases, so both
    views must be reported together.
    """
    predictions, prediction_labels = deduplicated_predictions(points)
    outcomes: dict[tuple[str, str], dict[str, int]] = defaultdict(dict)
    arm_labels: dict[str, str] = {}
    for point in predictions.values():
        arm_labels.setdefault(point.arm_id, prediction_labels[point.prediction_id])
        outcomes[(point.model_id, point.arm_id)][point.program_id] = point.y
    rows = []
    for model in sorted({model for model, _ in outcomes}):
        arms = sorted(arm for candidate, arm in outcomes if candidate == model)
        matched = set.intersection(*(set(outcomes[(model, arm)]) for arm in arms))
        for arm in arms:
            correct = sum(outcomes[(model, arm)][program] for program in matched)
            rows.append(
                {
                    "model_id": model,
                    "arm_id": arm,
                    "arm_group": arm_labels[arm],
                    "arm_count": str(len(arms)),
                    "correct": str(correct),
                    "total": str(len(matched)),
                    "accuracy": (
                        format(correct / len(matched), ".12g") if matched else ""
                    ),
                }
            )
    return rows


def markdown_matched_accuracy_table(rows: list[dict[str, str]]) -> str:
    models = sorted({row["model_id"] for row in rows})
    arms = sorted({row["arm_id"] for row in rows})
    lookup = {(row["arm_id"], row["model_id"]): row for row in rows}
    cohorts = {
        row["model_id"]: (row["total"], row["arm_count"]) for row in rows
    }
    lines = [
        "# Matched-cohort accuracy",
        "",
        "Each model is restricted to the programs that produced an eligible",
        "prediction in every arm that model ran, so all its arms share one",
        "denominator. Use this table to compare arms within a model. Use",
        "`overall-accuracy.md` to see how many predictions each arm actually",
        "produced.",
        "Every cell is `correct/matched programs (accuracy)`; `no data` means",
        "no program produced a gradable prediction in every arm for that model.",
        "",
        "This cohort excludes programs whose answer was ungradable in any arm.",
        "Those tend to be the hardest programs, so matched accuracy usually",
        "sits above the raw accuracy for the same arm. Neither table alone is",
        "the whole result.",
        "",
        "Matched cohort size per model:",
        "",
    ]
    for model in models:
        total, arm_count = cohorts[model]
        lines.append(f"- `{model}`: {total} programs across {arm_count} arms.")
    lines.extend(
        [
            "",
            "| Arm | " + " | ".join(models) + " |",
            "| --- | " + " | ".join("---" for _ in models) + " |",
        ]
    )
    for arm in arms:
        labels = {row["arm_group"] for row in rows if row["arm_id"] == arm}
        if len(labels) != 1:
            raise ValueError(f"arm {arm!r} has inconsistent presentation labels")
        cells = []
        for model in models:
            row = lookup.get((arm, model))
            if row is None:
                cells.append("no data")
            elif not row["accuracy"]:
                cells.append("no data")
            else:
                cells.append(
                    f"{row['correct']}/{row['total']}"
                    f" ({100 * float(row['accuracy']):.1f}%)"
                )
        lines.append("| " + next(iter(labels)) + " | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def markdown_accuracy_table(rows: list[dict[str, str]]) -> str:
    models = sorted({row["model_id"] for row in rows})
    arms = sorted({row["arm_id"] for row in rows})
    lookup = {(row["arm_id"], row["model_id"]): row for row in rows}
    lines = [
        "# Overall accuracy",
        "",
        "Predictions are deduplicated by `prediction_id` before counting.",
        "Each cell shows `correct/eligible (accuracy)` for one arm and model.",
        "",
        "Eligible counts differ between arms because ungradable answers are",
        "excluded, so a difference between two cells in the same column mixes",
        "an arm effect with a coverage difference. Compare arms within a model",
        "using `matched-accuracy.md`, which holds the program set fixed.",
        "",
        "| Arm | " + " | ".join(models) + " |",
        "| --- | " + " | ".join("---" for _ in models) + " |",
    ]
    for arm in arms:
        labels = {row["arm_group"] for row in rows if row["arm_id"] == arm}
        if len(labels) != 1:
            raise ValueError(f"arm {arm!r} has inconsistent presentation labels")
        label = next(iter(labels))
        cells = []
        for model in models:
            row = lookup.get((arm, model))
            if row is None:
                cells.append("no data")
            else:
                cells.append(
                    f"{row['correct']}/{row['total']} ({100 * float(row['accuracy']):.1f}%)"
                )
        lines.append("| " + label + " | " + " | ".join(cells) + " |")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--permutations", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=20_260_812)
    parser.add_argument(
        "--cross-factor",
        help="STATIC:DYNAMIC pair to compare when the two factors disagree",
    )
    parser.add_argument(
        "--cohort-manifest",
        type=Path,
        help=(
            "Cohort manifest whose eligibility and exclusion counts annotate "
            "the generated tables"
        ),
    )
    parser.add_argument(
        "--logistic-regression-config",
        type=Path,
        help=(
            "Optional JSON declaring metrics, arm cohorts, and output groups for "
            "logistic regressions of wrong on log2(metric)"
        ),
    )
    arguments = parser.parse_args()
    if arguments.permutations < 1:
        raise SystemExit("--permutations must be positive")

    try:
        points = load_points(arguments.points)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    grouped: dict[str, list[Point]] = defaultdict(list)
    for point in points:
        grouped[point.series_id].append(point)
    results = [
        analyze_series(
            sorted(
                grouped[series_id],
                key=lambda point: (
                    point.program_id,
                    point.execution_id,
                    point.prediction_id,
                ),
            ),
            arguments.permutations,
            arguments.seed,
        )
        for series_id in sorted(grouped)
    ]
    accuracy = accuracy_rows(points)
    cohort = (
        json.loads(arguments.cohort_manifest.read_text(encoding="utf-8"))
        if arguments.cohort_manifest
        else None
    )
    try:
        validate_dynamic_pooling_manifest(points, cohort)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    matched = matched_accuracy_rows(points)
    logistic_fits: list[LogisticFit] = []
    if arguments.logistic_regression_config:
        try:
            specifications = load_logistic_specifications(
                arguments.logistic_regression_config
            )
            logistic_fits = analyze_logistic_regressions(points, specifications)
        except ValueError as error:
            raise SystemExit(str(error)) from error

    arguments.output.mkdir(parents=True, exist_ok=True)
    write_csv(
        arguments.output / "raw-points.csv",
        REQUIRED_COLUMNS,
        (point.as_row() for point in sorted(points, key=lambda item: (item.series_id, item.program_id, item.execution_id))),
    )
    write_csv(
        arguments.output / "series-results.csv",
        RESULT_COLUMNS,
        (result.as_row() for result in results),
    )
    write_csv(
        arguments.output / "overall-accuracy.csv",
        ("arm_id", "arm_group", "model_id", "correct", "total", "accuracy"),
        accuracy,
    )
    (arguments.output / "static-tables.md").write_text(
        markdown_association_tables(results, "static"), encoding="utf-8"
    )
    (arguments.output / "dynamic-tables.md").write_text(
        markdown_association_tables(results, "dynamic"), encoding="utf-8"
    )
    (arguments.output / "metric-matrix.md").write_text(
        markdown_metric_matrix(
            results,
            arm_coverage(points),
            metric_matrix_eligible_totals(results, cohort),
        ),
        encoding="utf-8",
    )
    write_csv(
        arguments.output / "matched-accuracy.csv",
        ("model_id", "arm_id", "arm_group", "arm_count", "correct", "total", "accuracy"),
        matched,
    )
    exclusion_note = "\n".join(markdown_exclusion_note(cohort))
    (arguments.output / "overall-accuracy.md").write_text(
        markdown_accuracy_table(accuracy) + exclusion_note, encoding="utf-8"
    )
    (arguments.output / "matched-accuracy.md").write_text(
        markdown_matched_accuracy_table(matched) + exclusion_note, encoding="utf-8"
    )
    (arguments.output / "README.md").write_text(DATA_DICTIONARY, encoding="utf-8")
    measurement_coverage = markdown_measurement_coverage(cohort)
    if measurement_coverage is not None:
        (arguments.output / "measurement-coverage.md").write_text(
            measurement_coverage, encoding="utf-8"
        )
    (arguments.output / "supported-associations.md").write_text(
        markdown_supported_associations(results), encoding="utf-8"
    )
    if logistic_fits:
        write_csv(
            arguments.output / "logistic-regression-points.csv",
            LOGISTIC_POINT_COLUMNS,
            logistic_point_rows(logistic_fits),
        )
        write_csv(
            arguments.output / "logistic-regression-results.csv",
            LOGISTIC_RESULT_COLUMNS,
            logistic_result_rows(logistic_fits),
        )
        write_csv(
            arguments.output / "logistic-regression-curves.csv",
            LOGISTIC_CURVE_COLUMNS,
            logistic_curve_rows(logistic_fits),
        )
        (arguments.output / "logistic-regressions.md").write_text(
            markdown_logistic_regressions(logistic_fits), encoding="utf-8"
        )
    if arguments.cross_factor:
        static_metric, _, dynamic_metric = arguments.cross_factor.partition(":")
        if not static_metric or not dynamic_metric:
            raise SystemExit("--cross-factor must be STATIC:DYNAMIC")
        cross = cross_factor_analysis(
            points, static_metric, dynamic_metric,
            arguments.permutations, arguments.seed,
        )
        (arguments.output / "cross-factor.md").write_text(
            markdown_cross_factor(cross), encoding="utf-8"
        )
    manifest = {
        "schema": "prediction-factor-analysis-v1",
        "points_file": str(arguments.points),
        "points_sha256": hashlib.sha256(arguments.points.read_bytes()).hexdigest(),
        "analyzer_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "point_count": len(points),
        "prediction_count": len({point.prediction_id for point in points}),
        "series_count": len(results),
        "permutations": arguments.permutations,
        "global_seed": arguments.seed,
        "alternative": "failure factor values are larger than success factor values",
        "p_value_correction": "none",
        "logistic_regressions": {
            "config_file": str(arguments.logistic_regression_config),
            "config_sha256": (
                hashlib.sha256(arguments.logistic_regression_config.read_bytes()).hexdigest()
                if arguments.logistic_regression_config
                else None
            ),
            "fit_count": len(logistic_fits),
            "model": (
                "logit P(wrong=1) = beta0 + beta1 * log2(metric)"
                if logistic_fits
                else None
            ),
            "fit_method": (
                "standard maximum-likelihood logistic regression"
                if logistic_fits
                else None
            ),
            "interval": "Wald 95%" if logistic_fits else None,
        },
    }
    (arguments.output / "analysis-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"Analyzed {len(points)} points across {len(results)} series")
    print(f"Wrote {arguments.output}")


if __name__ == "__main__":
    main()
