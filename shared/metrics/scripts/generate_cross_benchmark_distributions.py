#!/usr/bin/env python3
"""Generate traceable cross-benchmark dynamic-complexity distributions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable


ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
METRICS = ("Omega_hat_NativeTrace", "Omega_hat_StateLoad")
LANGUAGES = ("python", "cpp")
POINT_COLUMNS = (
    "benchmark",
    "problem",
    "arm",
    "language",
    "execution_id",
    "metric",
    "value",
    "value_relation",
    "status",
    "source_sha256",
    "input_sha256",
    "adapter",
    "adapter_version",
    "runtime",
    "observation_convention",
    "comparability_cohort",
    "source_profile",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def repository_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / ".git").exists():
            return parent
    raise ValueError(f"could not find repository root above {path}")


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def csv_bytes(columns: Iterable[str], rows: Iterable[dict[str, Any]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(columns), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def percentile(values: list[int], probability: float) -> float:
    if not values:
        raise ValueError("percentile requires at least one value")
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def compact_number(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def cohort_key(row: dict[str, str]) -> str:
    return "|".join(
        (
            row["language"],
            row["metric"],
            row["adapter"],
            row["adapter_version"],
            row["runtime"],
            row["observation_convention"],
        )
    )


def load_rows(
    config: dict[str, Any], config_path: Path, root: Path
) -> tuple[list[dict[str, str]], list[dict[str, str]], dict[str, str]]:
    cohort_config = config["comparability_cohorts"]
    measured: list[dict[str, str]] = []
    eligible: list[dict[str, str]] = []
    source_hashes: dict[str, str] = {}
    seen: set[tuple[str, str, str, str]] = set()

    for source in config["sources"]:
        path = root / source
        source_hashes[source] = sha256_file(path)
        with path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                if row["metric"] not in METRICS:
                    continue
                if row["arm"] not in ARMS:
                    raise ValueError(f"unexpected arm in {source}: {row['arm']}")
                identity = (
                    row["benchmark"],
                    row["problem"],
                    row["arm"],
                    row["metric"],
                )
                if identity in seen:
                    raise ValueError(f"duplicate metric identity: {identity}")
                seen.add(identity)
                eligible.append(row)
                if row["status"] not in {"MEASURED", "LOWER_BOUND"}:
                    continue
                key = cohort_key(row)
                if key not in cohort_config:
                    raise ValueError(f"missing comparability cohort for {key}")
                output = {column: row[column] for column in POINT_COLUMNS if column in row}
                output["value"] = str(int(row["value"]))
                output["comparability_cohort"] = cohort_config[key]["id"]
                measured.append(output)

    if not eligible:
        raise ValueError("no eligible normalized measurements found")
    measured.sort(
        key=lambda row: (
            row["language"],
            row["metric"],
            row["comparability_cohort"],
            row["benchmark"],
            row["problem"],
            ARMS.index(row["arm"]),
        )
    )
    eligible.sort(
        key=lambda row: (
            row["language"],
            row["benchmark"],
            row["metric"],
            row["problem"],
            ARMS.index(row["arm"]),
        )
    )
    return measured, eligible, source_hashes


def coverage_rows(eligible: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str, str, str]] = Counter()
    totals: Counter[tuple[str, str, str]] = Counter()
    for row in eligible:
        base = (row["language"], row["benchmark"], row["metric"])
        totals[base] += 1
        counts[(*base, row["status"])] += 1
    result = []
    for language, benchmark, metric in sorted(totals):
        total = totals[(language, benchmark, metric)]
        measured = counts[(language, benchmark, metric, "MEASURED")]
        lower_bound = counts[(language, benchmark, metric, "LOWER_BOUND")]
        usable = measured + lower_bound
        result.append(
            {
                "language": language,
                "benchmark": benchmark,
                "metric": metric,
                "eligible": total,
                "measured": measured,
                "lower_bound": lower_bound,
                "usable": usable,
                "not_measured": counts[
                    (language, benchmark, metric, "NOT_MEASURED")
                ],
                "not_requested": counts[
                    (language, benchmark, metric, "NOT_REQUESTED")
                ],
                "measurement_rate": f"{measured / total:.6f}",
                "usable_rate": f"{usable / total:.6f}",
            }
        )
    return result


def missing_rows(eligible: list[dict[str, str]]) -> list[dict[str, Any]]:
    counts: Counter[tuple[str, str, str, str, str]] = Counter()
    for row in eligible:
        if row["status"] in {"MEASURED", "LOWER_BOUND"}:
            continue
        reason = row["not_measured_reason"] or row["status"]
        counts[
            (row["language"], row["benchmark"], row["metric"], row["status"], reason)
        ] += 1
    return [
        {
            "language": language,
            "benchmark": benchmark,
            "metric": metric,
            "status": status,
            "reason": reason,
            "count": count,
        }
        for (language, benchmark, metric, status, reason), count in sorted(
            counts.items()
        )
    ]


def summary_rows(
    measured: list[dict[str, str]], config: dict[str, Any]
) -> list[dict[str, Any]]:
    labels = {
        value["id"]: value["label"]
        for value in config["comparability_cohorts"].values()
    }
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in measured:
        groups[(row["language"], row["metric"], row["comparability_cohort"])].append(
            row
        )
    result = []
    for (language, metric, cohort), rows in sorted(groups.items()):
        usable_values = [int(row["value"]) for row in rows]
        exact_values = [int(row["value"]) for row in rows if row["status"] == "MEASURED"]
        lower_bounds = [
            int(row["value"]) for row in rows if row["status"] == "LOWER_BOUND"
        ]
        if not usable_values:
            continue
        result.append(
            {
                "language": language,
                "metric": metric,
                "comparability_cohort": cohort,
                "cohort_label": labels[cohort],
                "benchmarks": ";".join(sorted({row["benchmark"] for row in rows})),
                "measured": len(exact_values),
                "lower_bound": len(lower_bounds),
                "minimum": min(usable_values),
                "p25": compact_number(percentile(usable_values, 0.25)),
                "median": compact_number(percentile(usable_values, 0.5)),
                "p75": compact_number(percentile(usable_values, 0.75)),
                "maximum": max(usable_values),
            }
        )
    return result


def plot_distributions(
    measured: list[dict[str, str]],
    eligible: list[dict[str, str]],
    config: dict[str, Any],
    png_path: Path,
    pdf_path: Path,
) -> None:
    # Keep Matplotlib's font cache out of the user's profile and make clean
    # regeneration use a fresh, isolated cache just like CI.
    os.environ.setdefault("MPLBACKEND", "Agg")
    os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="mplconfig-"))
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.ticker import LogLocator, NullFormatter

    del config
    arm_labels = {
        "short-trace-final": "Short trace final",
        "long-trace-final": "Long trace final",
        "inside-loop-state": "Inside-loop state",
        "post-loop-state": "Post-loop state",
    }
    arm_colors = {
        "short-trace-final": "#60A5FA",
        "long-trace-final": "#FB923C",
        "inside-loop-state": "#4ADE80",
        "post-loop-state": "#F472B6",
    }
    metric_labels = {
        "Omega_hat_NativeTrace": "NativeTrace (instruction events)",
        "Omega_hat_StateLoad": "StateLoad (semantic state-cell observations)",
    }
    title_languages = {"python": "Python", "cpp": "C++"}
    groups: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    lower_bound_groups: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for row in measured:
        key = (row["language"], row["metric"], row["arm"])
        groups[key].append(int(row["value"]))
        if row["status"] == "LOWER_BOUND":
            lower_bound_groups[key].append(int(row["value"]))
    coverage: Counter[tuple[str, str, str]] = Counter()
    for row in eligible:
        coverage[(row["language"], row["metric"], row["status"])] += 1

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.5,
            "axes.titleweight": "bold",
            "axes.edgecolor": "#94A3B8",
            "axes.labelcolor": "#334155",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
        }
    )
    figure, axes = plt.subplots(2, 2, figsize=(13.5, 8.0))
    figure.patch.set_facecolor("#F8FAFC")
    figure.subplots_adjust(
        left=0.075, right=0.99, bottom=0.075, top=0.81, hspace=0.38, wspace=0.12
    )
    figure.suptitle(
        "Execution-complexity distributions by language",
        y=0.985,
        fontsize=17,
        fontweight="bold",
        color="#0F172A",
    )
    has_lower_bounds = any(lower_bound_groups.values())
    figure.text(
        0.5,
        0.947,
        (
            "Numeric observations, including retained bounds; log10 bins, KDE, and 5th-95th percentile"
            if has_lower_bounds
            else "Numeric observations; log10 bins, KDE, and 5th-95th percentile"
        ),
        ha="center",
        va="top",
        fontsize=10.5,
        color="#475569",
    )
    legend_handles = [
        Patch(facecolor=arm_colors[arm], label=arm_labels[arm]) for arm in ARMS
    ]
    legend_handles.extend(
        (
            Line2D([], [], color="#163E6C", linewidth=1.8, label="Log-space KDE"),
            Line2D(
                [],
                [],
                color="#C2412D",
                linewidth=1.4,
                linestyle="--",
                label="Median",
            ),
        )
    )
    if has_lower_bounds:
        legend_handles.append(
            Line2D(
                [],
                [],
                color="#111827",
                marker=">",
                linestyle="none",
                markersize=6,
                label="Retained bound (>=)",
            )
        )
    figure.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.5, 0.915),
        frameon=False,
        ncol=6,
        fontsize=8.2,
        handlelength=1.3,
        columnspacing=1.25,
    )

    for row_index, language in enumerate(LANGUAGES):
        for column_index, metric in enumerate(METRICS):
            axis = axes[row_index][column_index]
            axis.set_facecolor("white")
            values_by_arm = [groups[(language, metric, arm)] for arm in ARMS]
            usable_values = [value for values in values_by_arm for value in values]
            if not usable_values:
                raise ValueError(f"no plotted values for {language} {metric}")
            positive_values = [value for value in usable_values if value > 0]
            log_values = np.log10(np.asarray(usable_values, dtype=float))
            lower_power = np.floor(np.log10(min(positive_values)))
            upper_power = np.ceil(np.log10(max(positive_values)))
            if lower_power == upper_power:
                upper_power += 1
            log_bins = np.linspace(lower_power, upper_power, 24)
            bins = np.power(10.0, log_bins)
            log_bin_width = float(log_bins[1] - log_bins[0])
            weights = [
                np.full(len(values), 1.0 / (len(usable_values) * log_bin_width))
                for values in values_by_arm
            ]
            axis.hist(
                values_by_arm,
                bins=bins,
                weights=weights,
                stacked=True,
                color=[arm_colors[arm] for arm in ARMS],
                edgecolor="white",
                linewidth=0.35,
                alpha=0.88,
            )
            density_grid = np.linspace(lower_power, upper_power, 512)
            bandwidth = 1.06 * float(np.std(log_values, ddof=1)) * (
                len(log_values) ** (-1 / 5)
            )
            bandwidth = max(bandwidth, 0.05)
            standardized = (
                density_grid[:, np.newaxis] - log_values[np.newaxis, :]
            ) / bandwidth
            density = np.exp(-0.5 * standardized**2).mean(axis=1) / (
                bandwidth * np.sqrt(2 * np.pi)
            )
            axis.plot(
                np.power(10.0, density_grid),
                density,
                color="#163E6C",
                linewidth=1.8,
                alpha=0.95,
            )
            p05, median, p95 = np.percentile(log_values, [5, 50, 95])
            axis.axvspan(
                10**p05,
                10**p95,
                color="#F59E0B",
                alpha=0.065,
                linewidth=0,
            )
            axis.axvline(
                10**median,
                color="#C2412D",
                linewidth=1.4,
                linestyle="--",
                alpha=0.9,
            )
            for arm_index, arm in enumerate(ARMS):
                bounds = lower_bound_groups[(language, metric, arm)]
                if bounds:
                    axis.scatter(
                        bounds,
                        [0.035 + arm_index * 0.025] * len(bounds),
                        transform=axis.get_xaxis_transform(),
                        marker=">",
                        s=24,
                        color=arm_colors[arm],
                        edgecolor="#111827",
                        linewidth=0.35,
                        zorder=5,
                    )
            axis.set_xscale("log")
            axis.set_title(
                f"{title_languages[language]} - {metric.removeprefix('Omega_hat_')}",
                loc="left",
                pad=29,
            )
            axis.set_xlabel(metric_labels[metric])
            axis.set_ylabel("Density per log10 unit")
            exact_count = coverage[(language, metric, "MEASURED")]
            lower_bound_count = coverage[(language, metric, "LOWER_BOUND")]
            eligible_count = sum(
                count
                for (candidate_language, candidate_metric, _), count in coverage.items()
                if candidate_language == language and candidate_metric == metric
            )
            coverage_label = (
                f"{exact_count:,} exact + {lower_bound_count:,} >= / "
                f"{eligible_count:,} eligible"
                if lower_bound_count
                else f"{exact_count:,} measured / {eligible_count:,} eligible"
            )
            axis.text(
                0,
                1.012,
                coverage_label,
                transform=axis.transAxes,
                ha="left",
                va="bottom",
                fontsize=8.5,
                color="#64748B",
            )
            axis.text(
                0.985,
                0.96,
                (
                    f"median {int(round(10**median)):,}\n"
                    f"5th-95th {int(round(10**p05)):,}-{int(round(10**p95)):,}"
                ),
                transform=axis.transAxes,
                ha="right",
                va="top",
                fontsize=8.0,
                color="#475569",
                bbox={
                    "boxstyle": "round,pad=0.3",
                    "facecolor": "white",
                    "edgecolor": "#CBD5E1",
                    "alpha": 0.88,
                },
            )
            axis.grid(True, which="major", color="#CBD5E1", linewidth=0.8, alpha=0.65)
            axis.grid(True, which="minor", axis="x", color="#E2E8F0", linewidth=0.5, alpha=0.5)
            axis.xaxis.set_major_locator(LogLocator(base=10))
            axis.xaxis.set_minor_locator(LogLocator(base=10, subs=tuple(range(2, 10))))
            axis.xaxis.set_minor_formatter(NullFormatter())
            axis.spines["top"].set_visible(False)
            axis.spines["right"].set_visible(False)

    metadata = {
        "Title": "All-arm execution-complexity distributions by language",
        "Author": "obfuscated-code-output-prediction",
        "Creator": "generate_cross_benchmark_distributions.py",
        "CreationDate": None,
        "ModDate": None,
    }
    figure.savefig(
        png_path,
        dpi=220,
        facecolor=figure.get_facecolor(),
        metadata={"Software": "generate_cross_benchmark_distributions.py"},
    )
    figure.savefig(
        pdf_path,
        format="pdf",
        facecolor=figure.get_facecolor(),
        metadata=metadata,
    )
    plt.close(figure)


def generate(config_path: Path, root: Path, output: Path) -> list[Path]:
    config = json.loads(config_path.read_text(encoding="utf-8"))
    data_dir = output / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    measured, eligible, source_hashes = load_rows(config, config_path, root)
    points = csv_bytes(POINT_COLUMNS, measured)
    coverage = csv_bytes(
        (
            "language",
            "benchmark",
            "metric",
            "eligible",
            "measured",
            "lower_bound",
            "usable",
            "not_measured",
            "not_requested",
            "measurement_rate",
            "usable_rate",
        ),
        coverage_rows(eligible),
    )
    missing = csv_bytes(
        ("language", "benchmark", "metric", "status", "reason", "count"),
        missing_rows(eligible),
    )
    summary = csv_bytes(
        (
            "language",
            "metric",
            "comparability_cohort",
            "cohort_label",
            "benchmarks",
            "measured",
            "lower_bound",
            "minimum",
            "p25",
            "median",
            "p75",
            "maximum",
        ),
        summary_rows(measured, config),
    )
    outputs = {
        data_dir / "points.csv": points,
        data_dir / "coverage.csv": coverage,
        data_dir / "missing-causes.csv": missing,
        data_dir / "summary.csv": summary,
    }
    for path, content in outputs.items():
        path.write_bytes(content)

    png_path = output / "all-arm-complexity-distributions.png"
    pdf_path = output / "all-arm-complexity-distributions.pdf"
    plot_distributions(measured, eligible, config, png_path, pdf_path)

    generated = [*outputs, png_path, pdf_path]
    plotted_exact_points = sum(
        row["status"] == "MEASURED" for row in measured
    )
    manifest = {
        "schema_version": config["schema_version"],
        "arms": list(ARMS),
        "metrics": list(METRICS),
        "languages": list(LANGUAGES),
        "eligible_metric_cells": len(eligible),
        "retained_points": len(measured),
        "plotted_points": plotted_exact_points,
        "generator": relative_path(Path(__file__), root),
        "generator_sha256": sha256_file(Path(__file__)),
        "config_sha256": sha256_file(config_path),
        "sources": source_hashes,
        "outputs": {
            relative_path(config_path.parent / path.relative_to(output), root):
            sha256_file(path)
            for path in sorted(generated)
        },
    }
    manifest_path = output / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return [*generated, manifest_path]


def check_generated(config_path: Path, root: Path) -> int:
    with tempfile.TemporaryDirectory(prefix="complexity-distributions-") as temporary:
        temporary_output = Path(temporary)
        generated = generate(config_path, root, temporary_output)
        stale = []
        for generated_path in generated:
            relative = generated_path.relative_to(temporary_output)
            committed_path = config_path.parent / relative
            if not committed_path.exists() or (
                committed_path.read_bytes() != generated_path.read_bytes()
            ):
                stale.append(relative.as_posix())
    if stale:
        for path in stale:
            print(f"STALE {path}")
        return 1
    print(f"CURRENT {relative_path(config_path.parent, root)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in a temporary directory and compare every committed output",
    )
    args = parser.parse_args()
    config_path = args.config.resolve()
    root = repository_root(config_path)
    if args.check:
        return check_generated(config_path, root)
    generated = generate(config_path, root, config_path.parent)
    manifest_path = config_path.parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    print(
        f"WROTE {relative_path(config_path.parent, root)} "
        f"eligible={manifest['eligible_metric_cells']} "
        f"plotted={manifest['plotted_points']} "
        f"retained={manifest['retained_points']} files={len(generated)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
