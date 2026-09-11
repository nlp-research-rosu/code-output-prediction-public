from __future__ import annotations

import hashlib
import json
from pathlib import Path


def load_attempt_selections(
    path: Path,
) -> dict[tuple[str, str], tuple[str, str]]:
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise ValueError(f"{path}: schema_version must be 1")
    selections = {}
    for entry in payload.get("selections", []):
        key = (entry["model_id"], entry["problem_id"])
        if key in selections:
            raise ValueError(f"{path}: duplicate selected attempt: {key}")
        selections[key] = (entry["attempt"], entry["session_sha256"])
    return selections


def selected_session_path(
    run_directory: Path,
    experiment_root: Path,
    selections: dict[tuple[str, str], tuple[str, str]],
) -> Path | None:
    try:
        relative = run_directory.resolve().relative_to(
            (experiment_root / "runs").resolve()
        )
    except ValueError:
        return None
    if len(relative.parts) < 2:
        return None
    key = (relative.parts[0], Path(*relative.parts[1:]).as_posix())
    selection = selections.get(key)
    if selection is None:
        return None
    attempt, expected_sha256 = selection
    path = run_directory / attempt / "session.jsonl"
    if not path.is_file():
        raise ValueError(f"selected attempt does not exist: {path}")
    actual_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_sha256 != expected_sha256:
        raise ValueError(f"selected attempt hash drift: {path}")
    return path
