#!/usr/bin/env python3

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import workbench
from attempt_selection import (
    load_attempt_selections as load_selection_manifest,
    selected_session_path as resolve_selected_session,
)
from output_grading import classify_response, outputs_equal


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


def latest_transport_error(path: Path) -> bool:
    final_message: dict[str, object] | None = None
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return True
    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return True
        if not isinstance(entry, dict) or entry.get("type") != "message":
            continue
        message = entry.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            final_message = message
    if final_message is None:
        return True
    return bool(
        final_message.get("stopReason") == "error"
        or final_message.get("errorMessage")
    )


@lru_cache(maxsize=1)
def load_attempt_selections() -> dict[tuple[str, str], tuple[str, str]]:
    return load_selection_manifest(ATTEMPT_SELECTIONS)


def selected_session_path(run_directory: Path) -> Path | None:
    return resolve_selected_session(
        run_directory,
        EXPERIMENT_ROOT,
        load_attempt_selections(),
    )


def select_response(run_directory: Path) -> tuple[str | None, str, str | None]:
    selected = selected_session_path(run_directory)
    paths = [selected] if selected is not None else session_paths(run_directory)
    if not paths:
        return None, "not_run", None
    latest_path = paths[-1]
    for path in paths:
        response = workbench.parse_session(path)
        if response is not None:
            prediction, status = workbench.parse_prediction(path)
            return prediction, status, response
    if latest_transport_error(latest_path):
        return None, "transport_error", None
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
