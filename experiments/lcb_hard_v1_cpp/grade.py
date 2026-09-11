#!/usr/bin/env python3
"""Grade lcb_hard_v1_cpp predictions by semantic output equality."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import workbench  # noqa: E402
from experiments.lcb_hard_v1_cpp.analysis.grading import (  # noqa: E402
    GradeResult,
    grade_problem as shared_grade_problem,
)

ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)


def grade_problem(
    benchmark: workbench.Benchmark,
    model: workbench.Model,
    problem: workbench.Problem,
) -> GradeResult:
    return shared_grade_problem(benchmark, model, problem)


def aggregate(
    benchmark: workbench.Benchmark,
    model: workbench.Model,
    limit_per_arm: int | None = None,
) -> dict[str, Counter[str]]:
    results = {arm: Counter() for arm in ARMS}
    selected = Counter()
    for problem in benchmark.problems:
        arm = problem.id.rsplit("/", 1)[-1]
        if arm not in results:
            raise workbench.WorkbenchError(f"Unknown lcb_hard_v1_cpp arm: {arm}")
        if limit_per_arm is not None and selected[arm] >= limit_per_arm:
            continue
        selected[arm] += 1
        results[arm][grade_problem(benchmark, model, problem).status] += 1
    return results


def graded_accuracy(counts: Counter[str]) -> float:
    correct = counts["correct_valid"] + counts["correct_invalid"]
    total = sum(counts.values())
    return correct / total if total else 0.0


def print_report(
    model: workbench.Model,
    results: dict[str, Counter[str]],
) -> None:
    print(f"MODEL {model.id}")
    arm_width = max(14, *(len(arm) for arm in ARMS))
    print(
        f"{'ARM':{arm_width}} {'CORRECT&VALID':>14} "
        f"{'CORRECT&INVALID':>16} {'WRONG&VALID':>12} "
        f"{'WRONG&INVALID':>14} {'OTHERS':>7} {'ACCURACY':>9}"
    )
    for arm in ARMS:
        counts = results[arm]
        others = counts["no_response"] + counts["not_run"]
        print(
            f"{arm:{arm_width}} {counts['correct_valid']:14d} "
            f"{counts['correct_invalid']:16d} {counts['wrong_valid']:12d} "
            f"{counts['wrong_invalid']:14d} {others:7d} "
            f"{graded_accuracy(counts):8.2%}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Model id in workbench.toml")
    parser.add_argument(
        "--limit-per-arm",
        type=int,
        help="Grade only the first N problems in each arm.",
    )
    arguments = parser.parse_args(argv)
    try:
        benchmark = workbench.load_benchmark(ROOT / "experiments/lcb_hard_v1_cpp")
        model = workbench.select_models(benchmark, [arguments.model])[0]
        print_report(model, aggregate(benchmark, model, arguments.limit_per_arm))
        return 0
    except workbench.WorkbenchError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
