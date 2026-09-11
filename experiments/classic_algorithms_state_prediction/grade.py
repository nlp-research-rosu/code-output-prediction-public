#!/usr/bin/env python3

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
import sys


EXPERIMENT = Path(__file__).resolve().parent
ROOT = EXPERIMENT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import workbench  # noqa: E402
from experiments.classic_algorithms_state_prediction.analysis import grading  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", action="append")
    arguments = parser.parse_args()
    benchmark = workbench.load_benchmark(EXPERIMENT)
    models = workbench.select_models(benchmark, arguments.model)
    counts: Counter[str] = Counter()
    for model in models:
        for problem in benchmark.problems:
            result = grading.grade_problem(benchmark, model, problem)
            counts[result.status] += 1

    for status in (
        "correct_valid",
        "correct_invalid",
        "wrong_valid",
        "wrong_invalid",
        "transport_error",
        "no_response",
        "not_run",
    ):
        print(f"{status}: {counts[status]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
