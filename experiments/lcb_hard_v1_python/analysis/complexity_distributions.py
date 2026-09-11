#!/usr/bin/env python3
"""Plot full-benchmark static complexity distributions by language."""

from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.lcb_hard_v1_python.analysis.program_complexity import (  # noqa: E402
    NOT_MEASURED,
    atomic_write_text,
    load_jsonl,
    write_program_complexity_readme,
)


@dataclass(frozen=True)
class MetricSpec:
    name: str
    slug: str
    label: str
    description: str
    log1p: bool


METRICS = (
    MetricSpec(
        "Omega_CC",
        "omega-cc",
        "extended cyclomatic complexity",
        "control-flow decisions",
        True,
    ),
)
LANGUAGES = (("python", "Python", "#1875d1"), ("cpp", "C++", "#f05a28"))
SEED = 20260812


def numeric_values(records: list[dict[str, Any]], metric: str) -> list[float]:
    return [
        float(record["metrics"][metric])
        for record in records
        if isinstance(record["metrics"].get(metric), (int, float))
    ]


def summarize(
    metric: MetricSpec, language: str, records: list[dict[str, Any]]
) -> dict[str, Any]:
    import numpy as np

    values = np.asarray(numeric_values(records, metric.name), dtype=float)
    result = {
        "metric": metric.name,
        "language": language,
        "total_profiles": len(records),
        "measured_profiles": len(values),
        "not_measured_profiles": len(records) - len(values),
    }
    if not len(values):
        return {
            **result,
            "minimum": NOT_MEASURED,
            "q25": NOT_MEASURED,
            "median": NOT_MEASURED,
            "q75": NOT_MEASURED,
            "maximum": NOT_MEASURED,
            "mean": NOT_MEASURED,
            "population_standard_deviation": NOT_MEASURED,
        }
    q25, median, q75 = np.percentile(values, [25, 50, 75])
    return {
        **result,
        "minimum": float(values.min()),
        "q25": float(q25),
        "median": float(median),
        "q75": float(q75),
        "maximum": float(values.max()),
        "mean": float(values.mean()),
        "population_standard_deviation": float(values.std(ddof=0)),
    }


def format_value(value: float) -> str:
    if value >= 1000:
        return f"{value:,.0f}"
    if value >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}"


def format_tick(value: float) -> str:
    if math.isclose(value, round(value), abs_tol=1e-8):
        return f"{round(value):,}"
    return format_value(value)


def log1p_ticks(minimum: float, maximum: float) -> list[float]:
    candidates = []
    for exponent in range(-1, math.ceil(math.log10(maximum)) + 1):
        scale = 10**exponent
        candidates.extend(multiplier * scale for multiplier in (1, 2, 5))
    ticks = [value for value in candidates if minimum <= value <= maximum]
    if len(ticks) <= 7:
        return ticks
    step = math.ceil(len(ticks) / 7)
    selected = ticks[::step]
    if ticks[-1] not in selected and len(selected) < 7:
        selected.append(ticks[-1])
    return selected


def write_plot(
    output: Path,
    metric: MetricSpec,
    records_by_language: dict[str, list[dict[str, Any]]],
) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import FuncFormatter

    plt.rcParams.update(
        {
            "font.size": 10,
            "axes.titlesize": 12,
            "axes.labelsize": 11,
            "figure.facecolor": "white",
            "axes.facecolor": "white",
        }
    )
    languages = [item for item in LANGUAGES if records_by_language.get(item[0])]
    figure, axes = plt.subplots(
        1, len(languages), figsize=(6 * len(languages), 4.8), sharey=False,
        squeeze=False,
    )
    for axis, (language, title, color) in zip(axes[0], languages, strict=True):
        records = records_by_language[language]
        raw = np.asarray(numeric_values(records, metric.name), dtype=float)
        if not len(raw):
            axis.text(
                0.5,
                0.54,
                "NOT_MEASURED",
                transform=axis.transAxes,
                ha="center",
                va="center",
                fontsize=15,
                fontweight="semibold",
            )
            axis.text(
                0.5,
                0.43,
                f"0 of {len(records)} programs have numeric values",
                transform=axis.transAxes,
                ha="center",
                va="center",
                color="#555550",
            )
            axis.set_xticks([])
            axis.set_yticks([])
            axis.set_title(f"{title} - n=0/{len(records)}", loc="left")
            axis.spines[:].set_visible(False)
            continue
        shown = np.log1p(raw) if metric.log1p else raw
        if not metric.log1p and np.allclose(raw, np.round(raw)):
            minimum = int(raw.min())
            maximum = int(raw.max())
            bins = np.arange(minimum - 0.5, maximum + 1.5, 1)
        else:
            bins = min(28, max(8, round(math.sqrt(len(raw)) * 1.5)))
        axis.hist(shown, bins=bins, color=color, alpha=0.78, edgecolor="white")
        q25, median, q75 = np.percentile(raw, [25, 50, 75])
        transformed = (
            np.log1p([q25, median, q75]) if metric.log1p else [q25, median, q75]
        )
        axis.axvline(
            transformed[0], color="#555550", linestyle=(0, (2, 3)), linewidth=1.3
        )
        axis.axvline(transformed[1], color="#222220", linewidth=2)
        axis.axvline(
            transformed[2], color="#555550", linestyle=(0, (2, 3)), linewidth=1.3
        )
        rug_height = max(axis.get_ylim()[1] * 0.035, 0.2)
        axis.vlines(shown, 0, rug_height, color="#222220", alpha=0.14, linewidth=0.7)
        axis.set_title(f"{title} - n={len(raw)}/{len(records)}", loc="left")
        axis.set_ylabel("Number of programs")
        axis.set_xlabel("Metric value" + (" (log1p spacing)" if metric.log1p else ""))
        if metric.log1p:
            ticks = log1p_ticks(float(raw.min()), float(raw.max()))
            axis.set_xticks(np.log1p(ticks))
            axis.xaxis.set_major_formatter(
                FuncFormatter(lambda value, _: format_tick(max(0.0, np.expm1(value))))
            )
        axis.grid(axis="y", color="#e7e7e3", linewidth=0.8)
        axis.spines[["top", "right"]].set_visible(False)
        axis.text(
            0.98,
            0.96,
            f"median {format_value(median)}\nIQR {format_value(q25)}-{format_value(q75)}",
            transform=axis.transAxes,
            ha="right",
            va="top",
            color="#444440",
        )
    figure.suptitle(
        f"{metric.name} distribution - {metric.description}",
        x=0.06,
        ha="left",
        fontsize=15,
        fontweight="semibold",
    )
    figure.tight_layout(rect=(0.02, 0.02, 1, 0.92))
    figure.savefig(
        output / f"{metric.slug}-distribution.png",
        dpi=220,
        bbox_inches="tight",
        metadata={"Software": "matplotlib"},
    )
    figure.savefig(
        output / f"{metric.slug}-distribution.pdf",
        bbox_inches="tight",
        metadata={
            "Creator": "matplotlib",
            "Producer": "matplotlib",
            "CreationDate": None,
            "ModDate": None,
        },
    )
    plt.close(figure)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    atomic_write_text(path, handle.getvalue())


def run(arguments: argparse.Namespace) -> int:
    program_root = arguments.program_root.resolve()
    output = (
        arguments.output.resolve()
        if arguments.output
        else program_root / "distributions"
    )
    output.mkdir(parents=True, exist_ok=True)
    records_by_language = {
        language: list(
            load_jsonl(
                program_root / arguments.arm / language / "profiles.jsonl"
            ).values()
        )
        for language, _, _ in LANGUAGES
    }
    expected = {
        language: len(records_by_language[language])
        for language, _, _ in LANGUAGES
        if records_by_language[language]
    }
    if not any(expected.values()):
        raise RuntimeError(f"no profiles found below {program_root / arguments.arm}")
    rows = [
        summarize(metric, language, records_by_language[language])
        for metric in METRICS
        for language in expected
    ]
    write_csv(output / "summary.csv", rows)
    config = {
        "schema_version": 1,
        "benchmark": arguments.benchmark_name or program_root.parents[1].name,
        "arm": arguments.arm,
        "languages": expected,
        "metrics": [metric.name for metric in METRICS],
        "pool_languages": False,
        "histogram": "language-specific counts",
        "rug": "one mark per numeric program profile",
        "quartiles": "linear percentile",
        "x_transform": {
            metric.name: "log1p spacing with original-value tick labels"
            if metric.log1p
            else "linear"
            for metric in METRICS
        },
        "seed": SEED,
    }
    atomic_write_text(
        output / "analysis-config.json",
        json.dumps(config, indent=2, sort_keys=True) + "\n",
    )
    for metric in METRICS:
        write_plot(output, metric, records_by_language)
    print(
        f"COMPLETE metrics={len(METRICS)} profiles={sum(expected.values())} output={output}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument(
        "--program-root",
        type=Path,
        default=ROOT
        / "experiments"
        / "lcb_hard_v1_python"
        / "measurements"
        / "program-complexity",
    )
    result.add_argument("--benchmark-name")
    result.add_argument("--arm", default="short-trace-final")
    result.add_argument("--output", type=Path)
    return result


if __name__ == "__main__":
    raise SystemExit(run(parser().parse_args()))
