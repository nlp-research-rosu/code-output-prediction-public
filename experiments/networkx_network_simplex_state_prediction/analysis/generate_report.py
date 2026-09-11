#!/usr/bin/env python3
"""Regenerate the committed prediction-factor analysis without model calls."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
REPORT = EXPERIMENT / "reports/prediction-factor-analysis"
DATA = REPORT / "data"


def run(*arguments: object) -> None:
    command = [
        str(argument.relative_to(ROOT))
        if isinstance(argument, Path) and argument.is_absolute()
        else str(argument)
        for argument in arguments
    ]
    subprocess.run([sys.executable, *command], cwd=ROOT, check=True)


def main() -> int:
    run(EXPERIMENT / "grade.py")
    run(
        "-m",
        "experiments.networkx_network_simplex_state_prediction.analysis.prediction_factors",
    )
    run(
        ROOT / "shared/analysis/scripts/analyze.py",
        "--points",
        DATA / "source-points.csv",
        "--output",
        DATA / "analysis",
        "--permutations",
        10000,
        "--seed",
        20260812,
        "--cohort-manifest",
        DATA / "cohort-manifest.json",
        "--logistic-regression-config",
        REPORT / "logistic-regression-config.json",
    )
    run(
        ROOT / "shared/charts/scripts/generate_analysis.py",
        "--points",
        DATA / "analysis/raw-points.csv",
        "--series-results",
        DATA / "analysis/series-results.csv",
        "--config",
        REPORT / "chart-config.json",
        "--output",
        REPORT,
    )
    run(
        ROOT / "shared/reports/scripts/validate_report.py",
        "--report",
        REPORT.parent / "README.md",
        "--associations",
        DATA / "analysis/supported-associations.md",
        "--primary-results",
        DATA / "analysis/series-results.csv",
        "--pooled-results",
        DATA / "analysis/series-results.csv",
        "--chart-data",
        REPORT / "chart-data.csv",
        "--logistic-chart-data",
        REPORT / "logistic-chart-data.csv",
        "--chart-manifest",
        REPORT / "chart-manifest.json",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
