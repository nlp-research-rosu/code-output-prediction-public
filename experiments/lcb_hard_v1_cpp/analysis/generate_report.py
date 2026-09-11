#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXPERIMENT = Path(__file__).resolve().parents[1]
REPORT = EXPERIMENT / "reports" / "prediction-factor-analysis"
DATA = REPORT / "data"
ANALYZE = ROOT / "shared/analysis/scripts/analyze.py"
GENERATE = ROOT / "shared/charts/scripts/generate_analysis.py"
VALIDATE = ROOT / "shared/reports/scripts/validate_report.py"


def run(*arguments: object) -> None:
    normalized = []
    for argument in arguments:
        if isinstance(argument, Path) and argument.is_absolute():
            normalized.append(str(argument.relative_to(ROOT)))
        else:
            normalized.append(str(argument))
    subprocess.run(
        [sys.executable, *normalized],
        cwd=ROOT,
        check=True,
    )


def main() -> int:
    run(
        "-m",
        "experiments.lcb_hard_v1_cpp.analysis.prediction_factors",
        "--benchmark",
        EXPERIMENT,
        "--profiles-root",
        EXPERIMENT / "measurements/program-complexity",
        "--language",
        "cpp",
        "--output",
        DATA / "source-points.csv",
        "--manifest",
        DATA / "cohort-manifest.json",
    )
    run(
        ANALYZE,
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
        GENERATE,
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
        VALIDATE,
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
