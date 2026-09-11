#!/usr/bin/env python3
"""Grade workbench predictions by semantic output equality."""

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import workbench
from output_grading import (
    classify_response,
    outputs_equal,
)

REPETITION = re.compile(r"r(\d+)")
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
ATTEMPT_SELECTIONS = Path(__file__).with_name("selected-attempts.json")


@dataclass(frozen=True)
class GradeResult:
    status: str
    correct: bool | None
    attempted: bool

    def __post_init__(self) -> None:
        if self.attempted == (self.correct is None):
            raise ValueError("attempted results require boolean correctness")


def repetition_number(path: Path) -> int | None:
    match = REPETITION.fullmatch(path.parent.name)
    return int(match.group(1)) if match else None


def session_paths(run_directory: Path) -> list[Path]:
    paths = []
    for path in run_directory.glob("r*/session.jsonl"):
        repetition = repetition_number(path)
        if repetition is not None:
            paths.append((repetition, path))
    return [path for _, path in sorted(paths)]


@lru_cache(maxsize=1)
def load_attempt_selections() -> dict[tuple[str, str], tuple[str, str]]:
    if not ATTEMPT_SELECTIONS.is_file():
        return {}
    payload = json.loads(ATTEMPT_SELECTIONS.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError("selected-attempts.json schema_version must be 1")
    selections = {}
    for entry in payload.get("selections", []):
        key = (entry["model_id"], entry["problem_id"])
        if key in selections:
            raise ValueError(f"duplicate selected attempt: {key}")
        selections[key] = (entry["attempt"], entry["session_sha256"])
    return selections


@lru_cache(maxsize=1)
def load_invalidated_predictions() -> dict[tuple[str, str], str]:
    if not ATTEMPT_SELECTIONS.is_file():
        return {}
    payload = json.loads(ATTEMPT_SELECTIONS.read_text(encoding="utf-8"))
    return {
        (entry["model_id"], entry["problem_id"]): entry["reason_code"]
        for entry in payload.get("invalidated_predictions", [])
    }


def run_directory_key(run_directory: Path) -> tuple[str, str] | None:
    try:
        relative = run_directory.resolve().relative_to(
            (EXPERIMENT_ROOT / "runs").resolve()
        )
    except ValueError:
        return None
    if len(relative.parts) < 2:
        return None
    return relative.parts[0], Path(*relative.parts[1:]).as_posix()


def selected_session_path(run_directory: Path) -> Path | None:
    key = run_directory_key(run_directory)
    if key is None:
        return None
    selection = load_attempt_selections().get(key)
    if selection is None:
        return None
    attempt, expected_sha256 = selection
    path = run_directory / attempt / "session.jsonl"
    if not path.is_file():
        raise ValueError(f"selected attempt does not exist: {path}")
    if workbench.sha256_file(path) != expected_sha256:
        raise ValueError(f"selected attempt hash drift: {path}")
    return path


def select_response(run_directory: Path) -> tuple[str | None, str, str | None]:
    key = run_directory_key(run_directory)
    invalidation = load_invalidated_predictions().get(key)
    if invalidation is not None:
        status = (
            "no_response"
            if invalidation == "corrected_reasoning_transport_attempts_exhausted"
            else "not_run"
        )
        return None, status, None
    selected = selected_session_path(run_directory)
    paths = [selected] if selected is not None else session_paths(run_directory)
    if not paths:
        return None, "not_run", None
    for path in paths:
        response = workbench.parse_session(path)
        if response is not None:
            prediction, status = workbench.parse_prediction(path)
            return prediction, status, response
    return None, "no_response", None


def select_prediction(run_directory: Path) -> tuple[str | None, str]:
    prediction, status, _ = select_response(run_directory)
    return prediction, status


def select_raw_response(run_directory: Path) -> str | None:
    return select_response(run_directory)[2]


def grade_problem(
    benchmark: workbench.Benchmark,
    model: workbench.Model,
    problem: workbench.Problem,
) -> GradeResult:
    run_directory = benchmark.root / "runs" / model.id / Path(problem.id)
    prediction, status, response = select_response(run_directory)
    if status not in {"parsed_output", "invalid_format"}:
        attempted = status != "not_run"
        return GradeResult(status, False if attempted else None, attempted)
    oracle = workbench.read_utf8(problem.program.parent / "ground-output.txt")
    outcome, correct = classify_response(
        status,
        prediction,
        response,
        oracle,
        outputs_equal,
    )
    return GradeResult(outcome, correct, True)
