#!/usr/bin/env python3
"""Check published evidence or regenerate its analyses without model calls."""

from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import shlex
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PYTHON = "3.12.11"
ELIGIBLE = {"correct_valid", "correct_invalid", "wrong_valid", "wrong_invalid"}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def verify_hash(path: Path, expected: str) -> None:
    require(path.is_file(), f"Missing artifact: {path}")
    require(digest(path) == expected, f"SHA-256 mismatch: {path}")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def load_script(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def verify_release_manifest() -> int:
    manifest = ROOT / "MANIFEST.sha256"
    if not manifest.exists():
        return 0
    count = 0
    for line in manifest.read_text(encoding="utf-8").splitlines():
        expected, relative = line.split("  ", 1)
        path = ROOT / relative
        require(path.resolve().is_relative_to(ROOT), f"Invalid manifest path: {relative}")
        verify_hash(path, expected)
        count += 1
    print(f"Release manifest: {count:,} file hashes verified", flush=True)
    return count


def manifest_files(document: object, base: Path) -> None:
    """Check file/hash pairs emitted by the analysis and chart generators."""
    if isinstance(document, list):
        for item in document:
            manifest_files(item, base)
    elif isinstance(document, dict):
        for key, value in document.items():
            if key.endswith("_file") and isinstance(value, str):
                expected = document.get(key[:-5] + "_sha256")
                if expected:
                    path = ROOT / value if value.startswith("experiments/") else base / value
                    verify_hash(path, expected)
            elif key == "output_sha256" and isinstance(value, dict):
                for relative, expected in value.items():
                    verify_hash(base / relative, expected)
            elif isinstance(value, (dict, list)):
                manifest_files(value, base)


def native_grades(benchmark) -> dict[tuple[str, str, str], str]:
    """Use each experiment's original selection and semantic grading rule."""
    import workbench
    from attempt_selection import load_attempt_selections, selected_session_path
    from output_grading import classify_response

    experiment_id = benchmark.root.name
    prefix = f"experiments.{experiment_id}"
    if experiment_id in {
        "classic_algorithms_state_prediction", "lcb_hard_v1_python", "lcb_hard_v1_cpp"
    }:
        grading = importlib.import_module(prefix + ".analysis.grading")
        return {
            (model.id, *problem.id.rsplit("/", 1)): grading.grade_problem(
                benchmark, model, problem
            ).status
            for model in benchmark.models
            for problem in benchmark.problems
        }

    grading = importlib.import_module(prefix + ".grade")
    selections = load_attempt_selections(benchmark.root / "analysis/selected-attempts.json")
    result = {}
    for model in benchmark.models:
        for problem in benchmark.problems:
            attempt_root = benchmark.root / "runs" / model.id / problem.id
            sessions = sorted(attempt_root.glob("r[0-9][0-9][0-9]/session.jsonl"))
            selected = selected_session_path(attempt_root, benchmark.root, selections)
            selected = selected or next(
                (path for path in sessions if workbench.parse_session(path) is not None),
                sessions[-1] if sessions else None,
            )
            require(selected is not None, f"Missing prediction: {attempt_root}")
            if experiment_id == "codecontests_reasoning_state_prediction":
                message = grading.load_session(selected, grading.MODELS[model.id])
                response_status, prediction, response, _ = grading.parse_answer(message)
                comparator = grading.semantic_outputs_equal
            else:
                prediction, response_status = workbench.parse_prediction(selected)
                response = workbench.parse_session(selected)
                comparator = lambda left, right: left == right
            if response_status in {"parsed_output", "invalid_format"}:
                status, _ = classify_response(
                    response_status, prediction, response,
                    (problem.program.parent / "ground-output.txt").read_text(encoding="utf-8"),
                    comparator,
                )
            else:
                status = response_status
            result[(model.id, *problem.id.rsplit("/", 1))] = status
    return result


def check_experiment(experiment: Path) -> None:
    import workbench

    benchmark = workbench.load_benchmark(experiment)
    report = experiment / "reports/prediction-factor-analysis"
    data = report / "data/analysis"
    grades = native_grades(benchmark)
    outcomes = {}
    series = Counter()
    for point in read_csv(data / "raw-points.csv"):
        key = (point["model_id"], point["program_id"], point["arm_id"])
        status = grades.get(key)
        require(status in ELIGIBLE, f"Analysis includes an ungradable prediction: {key}")
        expected = int(status.startswith("correct_"))
        require(int(point["y"]) == expected, f"Native grade disagrees with analysis: {key}")
        require(key not in outcomes or outcomes[key] == expected, f"Inconsistent outcome: {key}")
        outcomes[key] = expected
        series[(point["series_id"], expected)] += 1
    eligible = {key for key, status in grades.items() if status in ELIGIBLE}
    require(set(outcomes) == eligible, f"Analysis prediction coverage disagrees with native grades: {experiment.name}")
    accuracy = {}
    for key, correct in outcomes.items():
        counts = accuracy.setdefault((key[0], key[2]), [0, 0])
        counts[0] += correct
        counts[1] += 1
    observed_accuracy = {}
    for row in read_csv(data / "overall-accuracy.csv"):
        key = (row["model_id"], row["arm_id"])
        observed_accuracy[key] = [int(row["correct"]), int(row["total"])]
        require(abs(float(row["accuracy"]) - int(row["correct"]) / int(row["total"])) < 1e-10,
                f"Incorrect accuracy percentage: {key}")
    require(observed_accuracy == accuracy, f"Accuracy table disagrees with native grades: {experiment.name}")
    for row in read_csv(data / "series-results.csv"):
        counts = (series[(row["series_id"], 1)], series[(row["series_id"], 0)])
        require(counts == (int(row["n_success"]), int(row["n_failure"]))
                and sum(counts) == int(row["n_total"]), f"Series counts disagree: {row['series_id']}")
    analysis_manifest = json.loads((data / "analysis-manifest.json").read_text())
    chart_manifest = json.loads((report / "chart-manifest.json").read_text())
    manifest_files(analysis_manifest, data)
    manifest_files(chart_manifest, report)
    verify_hash(ROOT / "shared/analysis/scripts/analyze.py", analysis_manifest["analyzer_sha256"])
    verify_hash(ROOT / "shared/charts/scripts/generate_analysis.py", chart_manifest["generator_sha256"])
    validator = load_script("benchmark_report_validator", ROOT / "shared/reports/scripts/validate_report.py")
    validator.validate(
        experiment / "reports/README.md", data / "supported-associations.md",
        data / "series-results.csv", data / "series-results.csv",
        report / "chart-data.csv", report / "chart-manifest.json",
        report / "logistic-chart-data.csv" if (report / "logistic-chart-data.csv").exists() else None,
    )
    print(f"{experiment.name}: {len(grades):,} predictions regraded; "
          f"{len(eligible):,} eligible; tables, charts and report verified", flush=True)


def regenerate(experiment: Path) -> None:
    require(shutil.which("uv") is not None, "Install uv to regenerate analyses: https://docs.astral.sh/uv/")
    command = [
        "uv", "run", "--python", PYTHON, "--with-requirements",
        str(experiment.relative_to(ROOT) / "analysis/requirements.txt"),
        "python", str(experiment.relative_to(ROOT) / "analysis/generate_report.py"),
    ]
    print("+ " + shlex.join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> int:
    import workbench

    experiments = {path.parent.name: path.parent for path in sorted((ROOT / "experiments").glob("*/workbench.toml"))}
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="regrade predictions and verify published artifacts (default)")
    mode.add_argument("--regenerate", action="store_true", help="regenerate statistics and figures from committed measurements and runs, then check")
    parser.add_argument("experiments", nargs="*", metavar="EXPERIMENT", help="experiment directory names; omitted means all five")
    args = parser.parse_args()
    unknown = set(args.experiments) - experiments.keys()
    if unknown:
        parser.error("Unknown experiments: " + ", ".join(sorted(unknown)))
    selected = [experiments[name] for name in dict.fromkeys(args.experiments)] if args.experiments else list(experiments.values())
    try:
        if not args.regenerate:
            verify_release_manifest()
        for experiment in selected:
            if args.regenerate:
                regenerate(experiment)
            check_experiment(experiment)
        if args.regenerate:
            verify_release_manifest()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, workbench.WorkbenchError) as error:
        print(f"Verification failed: {error}", file=sys.stderr)
        return 1
    print(f"Verified {len(selected)} experiment(s). No model calls were made.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
