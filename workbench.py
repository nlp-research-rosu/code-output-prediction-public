#!/usr/bin/env python3
"""Command-line interface for exact-output prediction benchmarks."""

import argparse
import base64
import csv
from collections import Counter
from concurrent.futures import as_completed, ThreadPoolExecutor
from dataclasses import dataclass
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

CONFIG_NAME = "workbench.toml"
PROBLEM_PROMPT_NAME = "prompt.txt"
PROMPT_PLACEHOLDERS = ("{{problem}}", "{{output}}")
PROMPT_PLACEHOLDER = re.compile(r"\{\{[^{}]+\}\}")
REASONING_LEVELS = {"off", "minimal", "low", "medium", "high", "xhigh", "max"}
MODEL_ID = re.compile(r"^[A-Za-z0-9._-]+$")
ENV_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
ATTEMPT_NAME = re.compile(r"^r([0-9]{3,})$")
CANONICAL_ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
NORMALIZED_PROFILE_SCHEMA = "program-complexity-normalized-v2"
NORMALIZED_PROFILE_METRICS = (
    "Omega_CC",
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
NORMALIZED_PROFILE_STATUSES = (
    "MEASURED",
    "LOWER_BOUND",
    "NOT_MEASURED",
    "NOT_REQUESTED",
)


class WorkbenchError(Exception):
    pass


@dataclass(frozen=True)
class Model:
    id: str
    provider: str
    model: str
    reasoning: str
    timeout_seconds: int
    pi_config_dir: Path | None = None


@dataclass(frozen=True)
class Problem:
    id: str
    program: Path
    input: Path
    prompt: Path | None
    context: tuple[Path, ...] = ()


@dataclass(frozen=True)
class Benchmark:
    root: Path
    system_prompt: str
    repetitions: int
    models: tuple[Model, ...]
    problems: tuple[Problem, ...]


@dataclass(frozen=True)
class SelectedPrediction:
    model: Model
    problem: Problem
    reason_code: str


def read_utf8(path: Path) -> str:
    try:
        return path.read_bytes().decode("utf-8")
    except FileNotFoundError as error:
        raise WorkbenchError(f"Missing file: {path}") from error
    except UnicodeDecodeError as error:
        raise WorkbenchError(f"File is not UTF-8: {path}") from error


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require_sha256(value: object, name: str) -> str:
    text = require_string(value, name)
    if not re.fullmatch(r"[0-9a-f]{64}", text):
        raise WorkbenchError(f"{name} must be a lowercase SHA-256 digest")
    return text


def render_context_file(path: Path, relative: str) -> str:
    data = path.read_bytes()
    try:
        content = data.decode("utf-8")
        return f'<file path="{relative}">\n{content}\n</file>'
    except UnicodeDecodeError:
        content = base64.b64encode(data).decode("ascii")
        return f'<file path="{relative}" encoding="base64">\n{content}\n</file>'


def require_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise WorkbenchError(f"{name} must be a non-empty string")
    return value


def validate_prompt_template(template: str, name: str) -> None:
    if not template.strip():
        raise WorkbenchError(f"The prompt template must not be blank: {name}")
    for placeholder in PROMPT_PLACEHOLDERS:
        if template.count(placeholder) != 1:
            raise WorkbenchError(
                f"The prompt template {name} must contain {placeholder} exactly once"
            )
    unknown = set(PROMPT_PLACEHOLDER.findall(template)) - set(PROMPT_PLACEHOLDERS)
    if unknown:
        raise WorkbenchError(
            f"The prompt template {name} has unknown placeholders: "
            f"{', '.join(sorted(unknown))}"
        )


def render_prompt_template(template: str, program: str, input_text: str) -> str:
    problem_text = (
        f"<program>\n{program}\n</program>\n\n"
        f"<input>\n{input_text}\n</input>"
    )
    return template.replace("{{problem}}", problem_text).replace(
        "{{output}}", '{"output":"<exact text>"}'
    )


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line_number, raw_line in enumerate(read_utf8(path).splitlines(), 1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").lstrip()
        name, separator, value = line.partition("=")
        name = name.strip()
        if not separator or not ENV_NAME.fullmatch(name):
            raise WorkbenchError(f"Invalid .env line {line_number}: {raw_line}")
        value = value.strip()
        if value.startswith(("'", '"')):
            if len(value) < 2 or value[-1] != value[0]:
                raise WorkbenchError(
                    f"Unterminated quoted value on .env line {line_number}"
                )
            value = value[1:-1]
        os.environ.setdefault(name, value)


def load_benchmark(root: Path) -> Benchmark:
    root = root.resolve()
    config_path = root / CONFIG_NAME
    try:
        config = tomllib.loads(read_utf8(config_path))
    except tomllib.TOMLDecodeError as error:
        raise WorkbenchError(f"Invalid TOML in {config_path}: {error}") from error

    allowed_keys = {"repetitions", "models"}
    unknown_keys = set(config) - allowed_keys
    if unknown_keys:
        raise WorkbenchError(
            f"Unknown {CONFIG_NAME} keys: {', '.join(sorted(unknown_keys))}"
        )

    system_prompt = read_utf8(Path(__file__).resolve().with_name("system-prompt.txt"))
    validate_prompt_template(system_prompt, "system-prompt.txt")

    repetitions = config.get("repetitions", 1)
    if (
        not isinstance(repetitions, int)
        or isinstance(repetitions, bool)
        or repetitions < 1
    ):
        raise WorkbenchError("repetitions must be a positive integer")

    raw_models = config.get("models")
    if not isinstance(raw_models, list) or not raw_models:
        raise WorkbenchError(
            "workbench.toml must contain at least one [[models]] entry"
        )

    models: list[Model] = []
    seen_model_ids: set[str] = set()
    for index, raw_model in enumerate(raw_models, 1):
        if not isinstance(raw_model, dict):
            raise WorkbenchError(f"models entry {index} must be a table")
        unknown_model_keys = set(raw_model) - {
            "id",
            "provider",
            "model",
            "reasoning",
            "timeout_seconds",
            "pi_config_dir",
        }
        if unknown_model_keys:
            raise WorkbenchError(
                f"Unknown keys in models entry {index}: "
                f"{', '.join(sorted(unknown_model_keys))}"
            )
        model_id = require_string(raw_model.get("id"), f"models[{index}].id")
        if not MODEL_ID.fullmatch(model_id):
            raise WorkbenchError(
                f"models[{index}].id may contain only letters, numbers, "
                "'.', '_' and '-'"
            )
        if model_id in seen_model_ids:
            raise WorkbenchError(f"Duplicate model id: {model_id}")
        seen_model_ids.add(model_id)
        reasoning = require_string(
            raw_model.get("reasoning"), f"models[{index}].reasoning"
        )
        if reasoning not in REASONING_LEVELS:
            raise WorkbenchError(
                f"models[{index}].reasoning must be one of: "
                f"{', '.join(sorted(REASONING_LEVELS))}"
            )
        timeout_seconds = raw_model.get("timeout_seconds")
        if (
            not isinstance(timeout_seconds, int)
            or isinstance(timeout_seconds, bool)
            or timeout_seconds < 1
        ):
            raise WorkbenchError(
                f"models[{index}].timeout_seconds must be a positive integer"
            )
        pi_config_dir = raw_model.get("pi_config_dir")
        if pi_config_dir is not None:
            pi_config_dir = (
                root
                / require_string(
                    pi_config_dir, f"models[{index}].pi_config_dir"
                )
            ).resolve()
            if not pi_config_dir.is_relative_to(root):
                raise WorkbenchError(
                    f"models[{index}].pi_config_dir must stay inside the experiment"
                )
            if not (pi_config_dir / "models.json").is_file():
                raise WorkbenchError(
                    f"models[{index}].pi_config_dir must contain models.json"
                )
        models.append(
            Model(
                id=model_id,
                provider=require_string(
                    raw_model.get("provider"), f"models[{index}].provider"
                ),
                model=require_string(
                    raw_model.get("model"), f"models[{index}].model"
                ),
                reasoning=reasoning,
                timeout_seconds=timeout_seconds,
                pi_config_dir=pi_config_dir,
            )
        )

    problems_root = root / "problems"
    if not problems_root.is_dir():
        raise WorkbenchError(f"Missing directory: {problems_root}")

    candidate_directories = {
        path.parent
        for pattern in ("program.*", "input.txt", "ground-output.txt")
        for path in problems_root.rglob(pattern)
        if path.is_file()
        and "context" not in path.relative_to(problems_root).parts
    }
    problems: list[Problem] = []
    for directory in sorted(candidate_directories):
        programs = sorted(
            path for path in directory.glob("program.*") if path.is_file()
        )
        problem_id = directory.relative_to(problems_root).as_posix()
        if len(programs) != 1:
            raise WorkbenchError(
                f"Problem {problem_id!r} must contain exactly one program.* file"
            )
        input_path = directory / "input.txt"
        ground_output_path = directory / "ground-output.txt"
        prompt_path = directory / PROBLEM_PROMPT_NAME
        context_root = directory / "context"
        if not input_path.is_file():
            raise WorkbenchError(f"Problem {problem_id!r} is missing input.txt")
        if not ground_output_path.is_file():
            raise WorkbenchError(f"Problem {problem_id!r} is missing ground-output.txt")
        for path in (programs[0], input_path, ground_output_path):
            read_utf8(path)
        if prompt_path.exists():
            if not prompt_path.is_file():
                raise WorkbenchError(
                    f"Problem {problem_id!r} has a non-file {PROBLEM_PROMPT_NAME}"
                )
            validate_prompt_template(read_utf8(prompt_path), str(prompt_path))
        context = (
            tuple(sorted(path for path in context_root.rglob("*") if path.is_file()))
            if context_root.is_dir()
            else ()
        )
        problems.append(
            Problem(
                id=problem_id,
                program=programs[0],
                input=input_path,
                prompt=prompt_path if prompt_path.is_file() else None,
                context=context,
            )
        )
    if not problems:
        raise WorkbenchError(f"No problems found under {problems_root}")

    benchmark = Benchmark(
        root=root,
        system_prompt=system_prompt,
        repetitions=repetitions,
        models=tuple(models),
        problems=tuple(problems),
    )
    validate_canonical_arms(benchmark)
    validate_normalized_profiles(benchmark)
    return benchmark


def select_models(
    benchmark: Benchmark, selected: list[str] | None
) -> tuple[Model, ...]:
    if not selected:
        return benchmark.models
    models = tuple(model for model in benchmark.models if model.id in selected)
    missing = set(selected) - {model.id for model in models}
    if missing:
        raise WorkbenchError(f"Unknown model ids: {', '.join(sorted(missing))}")
    return models


def select_problems(
    benchmark: Benchmark, patterns: list[str] | None, limit: int | None
) -> tuple[Problem, ...]:
    problems = benchmark.problems
    if patterns:
        problems = tuple(
            problem
            for problem in problems
            if any(fnmatch.fnmatchcase(problem.id, pattern) for pattern in patterns)
        )
        if not problems:
            raise WorkbenchError("No problems matched the requested patterns")
    if limit is not None:
        if limit < 1:
            raise WorkbenchError("--limit must be positive")
        problems = problems[:limit]
    return problems


def validate_canonical_arms(benchmark: Benchmark) -> None:
    cases_path = benchmark.root / "cases.json"
    if not cases_path.is_file():
        return

    manifest = json.loads(read_utf8(cases_path))
    case_records = manifest.get("cases", []) if isinstance(manifest, dict) else manifest
    if not isinstance(case_records, list):
        raise WorkbenchError("cases.json cases must be a list")
    for index, case in enumerate(case_records):
        if not isinstance(case, dict):
            raise WorkbenchError(f"cases.json entry {index} must be an object")
        validation = case.get("validation")
        if not isinstance(validation, dict):
            continue
        failed = sorted(
            name for name, value in validation.items() if value is False
        )
        if failed:
            identifier = (
                case.get("case_id")
                or case.get("problem_id")
                or "/".join(
                    str(case[key]) for key in ("platform", "question_id")
                    if key in case
                )
                or str(index)
            )
            raise WorkbenchError(
                f"Case {identifier!r} has failed validation evidence: "
                f"{', '.join(failed)}"
            )

    problems_by_case: dict[str, dict[str, Problem]] = {}
    for problem in benchmark.problems:
        case_id, separator, arm_id = problem.id.rpartition("/")
        if not separator:
            raise WorkbenchError(
                f"Canonical problem id must end in an arm id: {problem.id}"
            )
        if arm_id not in CANONICAL_ARMS:
            raise WorkbenchError(
                f"Problem {problem.id!r} uses non-canonical arm {arm_id!r}"
            )
        problems_by_case.setdefault(case_id, {})[arm_id] = problem

    expected = set(CANONICAL_ARMS)
    for case_id, arms in sorted(problems_by_case.items()):
        actual = set(arms)
        if actual != expected:
            missing = ", ".join(sorted(expected - actual)) or "none"
            extra = ", ".join(sorted(actual - expected)) or "none"
            raise WorkbenchError(
                f"Case {case_id!r} must contain exactly the canonical arms; "
                f"missing: {missing}; extra: {extra}"
            )

        short = arms["short-trace-final"]
        long = arms["long-trace-final"]
        inside = arms["inside-loop-state"]
        post = arms["post-loop-state"]
        if short.program.read_bytes() != long.program.read_bytes():
            raise WorkbenchError(
                f"Case {case_id!r} final arms must use identical source bytes"
            )
        long_input = long.input.read_bytes()
        if inside.input.read_bytes() != long_input or post.input.read_bytes() != long_input:
            raise WorkbenchError(
                f"Case {case_id!r} state arms must use the long-trace input"
            )
        state_oracles: list[tuple[Problem, dict[str, object]]] = []
        for state_problem in (inside, post):
            oracle_path = state_problem.program.parent / "ground-output.txt"
            try:
                state = json.loads(read_utf8(oracle_path))
            except json.JSONDecodeError as error:
                raise WorkbenchError(
                    f"Case {case_id!r} state oracle is not JSON: {oracle_path}"
                ) from error
            if not isinstance(state, dict) or not state:
                raise WorkbenchError(
                    f"Case {case_id!r} state oracle must be a non-empty JSON object"
                )
            canonical = (
                json.dumps(state, ensure_ascii=False, separators=(",", ":")) + "\n"
            ).encode("utf-8")
            if oracle_path.read_bytes() != canonical:
                raise WorkbenchError(
                    f"Case {case_id!r} state oracle must use canonical compact JSON"
                )
            state_oracles.append((state_problem, state))
        inside_state = state_oracles[0][1]
        post_state = state_oracles[1][1]
        if list(inside_state) != list(post_state):
            raise WorkbenchError(
                f"Case {case_id!r} state oracles must use the same ordered fields"
            )
        if any(
            type(inside_state[key]) is not type(post_state[key])
            for key in inside_state
        ):
            raise WorkbenchError(
                f"Case {case_id!r} state oracle field types must match"
            )
        if inside_state == post_state:
            raise WorkbenchError(
                f"Case {case_id!r} state projection must change after the loop"
            )


def validate_normalized_profiles(benchmark: Benchmark) -> None:
    package = benchmark.root / "measurements" / "program-complexity"
    config_path = package / "normalized-profiles-config.json"
    if not config_path.is_file():
        return
    csv_path = package / "normalized-profiles.csv"
    manifest_path = package / "normalized-profiles-manifest.json"
    if not csv_path.is_file() or not manifest_path.is_file():
        raise WorkbenchError(
            f"Normalized profile config requires {csv_path.name} and "
            f"{manifest_path.name}"
        )
    try:
        manifest = json.loads(read_utf8(manifest_path))
    except json.JSONDecodeError as error:
        raise WorkbenchError(f"Invalid JSON in {manifest_path}: {error}") from error
    if manifest.get("schema_version") != NORMALIZED_PROFILE_SCHEMA:
        raise WorkbenchError(
            f"Unsupported normalized profile schema in {manifest_path}"
        )
    if manifest.get("benchmark") != benchmark.root.name:
        raise WorkbenchError(
            f"Normalized profile benchmark does not match {benchmark.root.name}"
        )
    if manifest.get("status_vocabulary") != list(NORMALIZED_PROFILE_STATUSES):
        raise WorkbenchError("Normalized profile status vocabulary has drifted")
    output = manifest.get("output") or {}
    if output.get("sha256") != sha256_file(csv_path):
        raise WorkbenchError(f"Normalized profile output hash is stale: {csv_path}")
    repository = Path(__file__).resolve().parent
    for provenance_name in ("config", "generator"):
        provenance = manifest.get(provenance_name) or {}
        provenance_path = (
            repository
            / require_string(provenance.get("path"), f"{provenance_name} path")
        ).resolve()
        try:
            provenance_path.relative_to(repository)
        except ValueError as error:
            raise WorkbenchError(
                f"Normalized profile {provenance_name} escapes the repository"
            ) from error
        if (
            not provenance_path.is_file()
            or provenance.get("sha256") != sha256_file(provenance_path)
        ):
            raise WorkbenchError(
                f"Normalized profile {provenance_name} hash is stale: "
                f"{provenance_path}"
            )
    for source in manifest.get("inputs") or []:
        if not isinstance(source, dict):
            raise WorkbenchError("Normalized profile manifest input must be an object")
        source_path = (
            repository / require_string(source.get("path"), "input path")
        ).resolve()
        try:
            source_path.relative_to(repository)
        except ValueError as error:
            raise WorkbenchError(
                f"Normalized profile input escapes the repository: {source_path}"
            ) from error
        if (
            not source_path.is_file()
            or source.get("sha256") != sha256_file(source_path)
        ):
            raise WorkbenchError(
                f"Normalized profile input hash is stale: {source_path}"
            )
    with csv_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        columns = manifest.get("columns")
        if reader.fieldnames != columns:
            raise WorkbenchError(f"Normalized profile columns have drifted: {csv_path}")
        rows = list(reader)
    if len(rows) != manifest.get("row_count"):
        raise WorkbenchError(f"Normalized profile row count is stale: {csv_path}")
    coverage = {
        metric: {status: 0 for status in NORMALIZED_PROFILE_STATUSES}
        for metric in NORMALIZED_PROFILE_METRICS
    }
    profile_metrics: dict[tuple[str, str, str], set[str]] = {}
    for line_number, row in enumerate(rows, 2):
        label = f"{csv_path}:{line_number}"
        if row.get("schema_version") != NORMALIZED_PROFILE_SCHEMA:
            raise WorkbenchError(f"Wrong normalized schema at {label}")
        if row.get("benchmark") != benchmark.root.name:
            raise WorkbenchError(f"Wrong normalized benchmark at {label}")
        if row.get("language") not in {"python", "cpp"}:
            raise WorkbenchError(f"Wrong normalized language at {label}")
        arm = row.get("arm")
        if arm not in CANONICAL_ARMS:
            raise WorkbenchError(f"Non-canonical normalized arm at {label}: {arm}")
        metric = row.get("metric")
        if metric not in NORMALIZED_PROFILE_METRICS:
            raise WorkbenchError(f"Unknown normalized metric at {label}: {metric}")
        status = row.get("status")
        if status not in NORMALIZED_PROFILE_STATUSES:
            raise WorkbenchError(f"Unknown normalized status at {label}: {status}")
        value = row.get("value", "")
        relation = row.get("value_relation", "")
        reason = row.get("not_measured_reason", "")
        if status == "MEASURED":
            if not value.isdigit() or relation != "=" or reason:
                raise WorkbenchError(
                    "Measured normalized value must be numeric with relation = "
                    "and without a reason "
                    f"at {label}"
                )
        elif status == "LOWER_BOUND":
            if not value.isdigit() or relation != ">=" or reason:
                raise WorkbenchError(
                    "Lower-bound normalized value must be numeric with relation "
                    f">= and without a reason at {label}"
                )
        elif value or relation or not reason:
            raise WorkbenchError(
                "Unavailable normalized value needs an empty value and relation "
                "plus a reason "
                f"at {label}"
            )
        execution_id = row.get("execution_id", "")
        if not re.fullmatch(r"sha256:[0-9a-f]{64}", execution_id):
            raise WorkbenchError(f"Invalid normalized execution identity at {label}")
        for digest_name in ("source_sha256", "input_sha256"):
            if not re.fullmatch(r"[0-9a-f]{64}", row.get(digest_name, "")):
                raise WorkbenchError(f"Invalid {digest_name} at {label}")
        for field in ("adapter", "adapter_version", "runtime", "source_profile"):
            if not row.get(field):
                raise WorkbenchError(f"Missing normalized {field} at {label}")
        if metric != "Omega_CC" and not row.get("observation_convention"):
            raise WorkbenchError(
                f"Missing normalized observation convention at {label}"
            )
        try:
            repetitions = int(row.get("repetitions", ""))
        except ValueError as error:
            raise WorkbenchError(
                f"Invalid normalized repetitions at {label}"
            ) from error
        if repetitions < 1:
            raise WorkbenchError(f"Invalid normalized repetitions at {label}")
        key = (require_string(row.get("problem"), "problem"), arm, execution_id)
        if metric in profile_metrics.setdefault(key, set()):
            raise WorkbenchError(f"Duplicate normalized metric at {label}")
        profile_metrics[key].add(metric)
        coverage[metric][status] += 1
    expected_metrics = set(NORMALIZED_PROFILE_METRICS)
    if any(metrics != expected_metrics for metrics in profile_metrics.values()):
        raise WorkbenchError(
            "Normalized execution profiles must contain four metrics: "
            f"{csv_path}"
        )
    if len(profile_metrics) != manifest.get("execution_profile_count"):
        raise WorkbenchError(
            f"Normalized execution profile count is stale: {csv_path}"
        )
    if coverage != manifest.get("coverage"):
        raise WorkbenchError(f"Normalized profile coverage is stale: {csv_path}")


def load_selection_file(
    benchmark: Benchmark, path: Path
) -> tuple[tuple[SelectedPrediction, ...], int]:
    try:
        raw = json.loads(read_utf8(path.resolve()))
    except json.JSONDecodeError as error:
        raise WorkbenchError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(raw, dict):
        raise WorkbenchError("Selection file must contain one JSON object")

    required = {
        "schema_version",
        "experiment_id",
        "prepared_commit",
        "provider_group",
        "max_transport_attempts",
        "predictions",
    }
    if set(raw) != required:
        missing = ", ".join(sorted(required - set(raw))) or "none"
        extra = ", ".join(sorted(set(raw) - required)) or "none"
        raise WorkbenchError(
            f"Selection file keys do not match the contract; missing: {missing}; "
            f"extra: {extra}"
        )
    if raw["schema_version"] != 1:
        raise WorkbenchError("selection schema_version must be 1")
    if raw["experiment_id"] != benchmark.root.name:
        raise WorkbenchError(
            f"Selection experiment_id must be {benchmark.root.name!r}"
        )
    require_string(raw["prepared_commit"], "prepared_commit")
    require_string(raw["provider_group"], "provider_group")
    if raw["max_transport_attempts"] != 3:
        raise WorkbenchError("max_transport_attempts must be 3")
    predictions = raw["predictions"]
    if not isinstance(predictions, list) or not predictions:
        raise WorkbenchError("predictions must be a non-empty array")

    models = {model.id: model for model in benchmark.models}
    problems = {problem.id: problem for problem in benchmark.problems}
    selected: list[SelectedPrediction] = []
    seen: set[tuple[str, str]] = set()
    prediction_keys = {
        "model_id",
        "problem_id",
        "case_id",
        "arm_id",
        "source_sha256",
        "input_sha256",
        "oracle_sha256",
        "reason_code",
    }
    for index, prediction in enumerate(predictions):
        prefix = f"predictions[{index}]"
        if not isinstance(prediction, dict) or set(prediction) != prediction_keys:
            raise WorkbenchError(f"{prefix} keys do not match the contract")
        model_id = require_string(prediction["model_id"], f"{prefix}.model_id")
        problem_id = require_string(
            prediction["problem_id"], f"{prefix}.problem_id"
        )
        case_id = require_string(prediction["case_id"], f"{prefix}.case_id")
        arm_id = require_string(prediction["arm_id"], f"{prefix}.arm_id")
        reason_code = require_string(
            prediction["reason_code"], f"{prefix}.reason_code"
        )
        if arm_id not in CANONICAL_ARMS:
            raise WorkbenchError(f"{prefix}.arm_id is not canonical: {arm_id}")
        if problem_id != f"{case_id}/{arm_id}":
            raise WorkbenchError(
                f"{prefix}.problem_id must equal case_id/arm_id"
            )
        if model_id not in models:
            raise WorkbenchError(f"Unknown model id in {prefix}: {model_id}")
        if problem_id not in problems:
            raise WorkbenchError(f"Unknown problem id in {prefix}: {problem_id}")
        identity = (model_id, problem_id)
        if identity in seen:
            raise WorkbenchError(
                f"Duplicate prediction cell: {model_id}/{problem_id}"
            )
        seen.add(identity)

        problem = problems[problem_id]
        expected_hashes = {
            "source_sha256": sha256_file(problem.program),
            "input_sha256": sha256_file(problem.input),
            "oracle_sha256": sha256_file(
                problem.program.parent / "ground-output.txt"
            ),
        }
        for key, expected_hash in expected_hashes.items():
            actual_hash = require_sha256(prediction[key], f"{prefix}.{key}")
            if actual_hash != expected_hash:
                raise WorkbenchError(
                    f"Hash drift for {model_id}/{problem_id}: {key}"
                )
        selected.append(
            SelectedPrediction(models[model_id], problem, reason_code)
        )

    return tuple(selected), raw["max_transport_attempts"]


def render_problem_prompt(benchmark: Benchmark, problem: Problem) -> str:
    template = (
        read_utf8(problem.prompt)
        if problem.prompt is not None
        else benchmark.system_prompt
    )
    program = read_utf8(problem.program)
    if problem.context:
        context_root = problem.program.parent / "context"
        rendered_context = []
        for path in problem.context:
            relative = path.relative_to(context_root).as_posix()
            rendered_context.append(render_context_file(path, relative))
        program += "\n\n<context>\n" + "\n\n".join(rendered_context) + "\n</context>"
    return render_prompt_template(template, program, read_utf8(problem.input))


def session_path(
    benchmark: Benchmark, model: Model, problem: Problem, repetition: int
) -> Path:
    return (
        benchmark.root
        / "runs"
        / model.id
        / Path(problem.id)
        / f"r{repetition:03d}"
        / "session.jsonl"
    )


def attempt_session_paths(
    benchmark: Benchmark, model: Model, problem: Problem
) -> tuple[tuple[int, Path], ...]:
    root = benchmark.root / "runs" / model.id / Path(problem.id)
    attempts: list[tuple[int, Path]] = []
    if not root.is_dir():
        return ()
    for directory in root.iterdir():
        match = ATTEMPT_NAME.fullmatch(directory.name)
        if match and directory.is_dir():
            attempts.append((int(match.group(1)), directory / "session.jsonl"))
    return tuple(sorted(attempts))


def first_completed_session(
    benchmark: Benchmark, model: Model, problem: Problem
) -> Path | None:
    for _, path in attempt_session_paths(benchmark, model, problem):
        if path.is_file() and parse_session(path) is not None:
            return path
    return None


def parse_session(path: Path) -> str | None:
    final_message: dict[str, object] | None = None
    try:
        lines = read_utf8(path).splitlines()
    except WorkbenchError:
        return None

    for line in lines:
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            return None
        if not isinstance(entry, dict) or entry.get("type") != "message":
            continue
        message = entry.get("message")
        if isinstance(message, dict) and message.get("role") == "assistant":
            final_message = message

    if final_message is None:
        return None
    if final_message.get("stopReason") == "error" or final_message.get("errorMessage"):
        return None

    content = final_message.get("content", [])
    if not isinstance(content, list):
        return None
    text = "".join(
        block.get("text", "")
        for block in content
        if isinstance(block, dict)
        and block.get("type") == "text"
        and isinstance(block.get("text", ""), str)
    )
    if text:
        return text
    if final_message.get("stopReason") in {"stop", "length"}:
        return ""
    return None


def parse_prediction(path: Path) -> tuple[str | None, str]:
    response = parse_session(path)
    if response is None:
        return None, "no_response"
    try:
        parsed = json.loads(response)
    except json.JSONDecodeError:
        return None, "invalid_format"
    if (
        not isinstance(parsed, dict)
        or set(parsed) != {"output"}
        or not isinstance(parsed["output"], str)
    ):
        return None, "invalid_format"
    return parsed["output"], "parsed_output"


def run_attempt(
    benchmark: Benchmark, model: Model, problem: Problem, repetition: int
) -> tuple[str, Path]:
    destination = session_path(benchmark, model, problem, repetition)
    if destination.exists():
        return "skipped", destination

    environment = os.environ.copy()
    environment.update(
        {"PI_SKIP_VERSION_CHECK": "1", "PI_TELEMETRY": "0", "NO_COLOR": "1"}
    )
    if model.pi_config_dir is not None:
        environment["PI_CODING_AGENT_DIR"] = str(model.pi_config_dir)

    with tempfile.TemporaryDirectory(prefix="pi-workbench-") as directory:
        session_directory = Path(directory)
        system_prompt = render_problem_prompt(benchmark, problem)
        system_prompt_path = session_directory / "system-prompt.txt"
        system_prompt_path.write_text(system_prompt, encoding="utf-8")
        command = [
            "pi",
            "--provider",
            model.provider,
            "--model",
            model.model,
            "--thinking",
            model.reasoning,
            "--system-prompt",
            str(system_prompt_path),
            "--session-dir",
            str(session_directory),
            "--print",
            "--no-tools",
            "--no-extensions",
            "--no-skills",
            "--no-prompt-templates",
            "--no-context-files",
            "--no-themes",
            "--no-approve",
        ]
        try:
            process = subprocess.run(
                command,
                input="Return the requested prediction.\n",
                text=True,
                capture_output=True,
                cwd=benchmark.root,
                env=environment,
                timeout=model.timeout_seconds,
            )
        except subprocess.TimeoutExpired:
            process = None

        sessions = sorted(session_directory.rglob("*.jsonl"))
        if len(sessions) != 1:
            detail = (
                "timed out" if process is None else f"Pi exited {process.returncode}"
            )
            if process is not None and process.stderr.strip():
                detail += f": {process.stderr.strip()}"
            raise WorkbenchError(
                f"{model.id}/{problem.id}/r{repetition:03d}: {detail}; "
                f"found {len(sessions)} session files"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(sessions[0], destination)

    return ("timeout" if process is None else "recorded"), destination


def write_parsed_output(path: Path) -> str:
    prediction, status = parse_prediction(path)
    output_path = path.with_name("output.txt")
    if prediction is None:
        output_path.unlink(missing_ok=True)
    else:
        output_path.write_bytes(prediction.encode("utf-8"))
    return status


def run_selected_prediction(
    benchmark: Benchmark,
    selection: SelectedPrediction,
    max_transport_attempts: int,
) -> tuple[bool, str]:
    model = selection.model
    problem = selection.problem
    label = f"{model.id} {problem.id}"
    completed = first_completed_session(benchmark, model, problem)
    if completed is not None:
        status = write_parsed_output(completed)
        return False, f"SKIPPED  {status.upper():14} {label}"

    attempts = attempt_session_paths(benchmark, model, problem)
    used_attempts = len(attempts)
    next_repetition = max((number for number, _ in attempts), default=0) + 1
    failures: list[str] = []
    while used_attempts < max_transport_attempts:
        repetition = next_repetition
        next_repetition += 1
        used_attempts += 1
        print(
            f"RUNNING  {label} r{repetition:03d} "
            f"(timeout {model.timeout_seconds}s)",
            flush=True,
        )
        try:
            outcome, path = run_attempt(benchmark, model, problem, repetition)
        except WorkbenchError as error:
            failures.append(str(error))
            continue
        if parse_session(path) is None:
            failures.append(f"{path}: no completed assistant response")
            continue
        status = write_parsed_output(path)
        return (
            False,
            f"{outcome.upper():8} {status.upper():14} {label} r{repetition:03d}",
        )

    detail = failures[-1] if failures else "transport attempts already exhausted"
    return True, f"EXHAUSTED NO_RESPONSE    {label}: {detail}"


def report(
    benchmark: Benchmark,
    models: tuple[Model, ...],
    problems: tuple[Problem, ...],
    verbose: bool,
) -> None:
    per_model: dict[str, Counter[str]] = {model.id: Counter() for model in models}
    for model in models:
        for problem in problems:
            for repetition in range(1, benchmark.repetitions + 1):
                path = session_path(benchmark, model, problem, repetition)
                if path.exists():
                    _, status = parse_prediction(path)
                else:
                    status = "not_run"
                per_model[model.id][status] += 1
                if verbose:
                    print(
                        f"{status.upper():14} {model.id} {problem.id} "
                        f"r{repetition:03d}"
                    )

    statuses = ("parsed_output", "invalid_format", "no_response", "not_run")
    header = f"{'MODEL':24} " + " ".join(
        f"{status.upper():>14}" for status in statuses
    )
    print(header)
    for model in models:
        counts = per_model[model.id]
        print(
            f"{model.id:24} "
            + " ".join(f"{counts[status]:14d}" for status in statuses)
        )


def report_selection(
    benchmark: Benchmark,
    selections: tuple[SelectedPrediction, ...],
    verbose: bool,
) -> None:
    per_model: dict[str, Counter[str]] = {}
    for selection in selections:
        model = selection.model
        problem = selection.problem
        counts = per_model.setdefault(model.id, Counter())
        completed = first_completed_session(benchmark, model, problem)
        if completed is not None:
            _, status = parse_prediction(completed)
        elif attempt_session_paths(benchmark, model, problem):
            status = "no_response"
        else:
            status = "not_run"
        counts[status] += 1
        if verbose:
            print(f"{status.upper():14} {model.id} {problem.id}")

    statuses = ("parsed_output", "invalid_format", "no_response", "not_run")
    print(
        f"{'MODEL':24} "
        + " ".join(f"{status.upper():>14}" for status in statuses)
    )
    for model_id, counts in per_model.items():
        print(
            f"{model_id:24} "
            + " ".join(f"{counts[status]:14d}" for status in statuses)
        )


def add_selection_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--problem",
        action="append",
        help="Problem id or glob; may be repeated.",
    )
    parser.add_argument(
        "--model",
        action="append",
        help="Model id from workbench.toml; may be repeated.",
    )
    parser.add_argument("--limit", type=int, help="Use only the first N problems.")
    parser.add_argument(
        "--selection-file",
        type=Path,
        help="Run or report only exact model/problem cells from a validated plan.",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run exact-output prediction benchmarks through Pi."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a benchmark.")
    validate_parser.add_argument("benchmark", type=Path)

    run_parser = subparsers.add_parser("run", help="Run missing sessions.")
    run_parser.add_argument("benchmark", type=Path)
    add_selection_arguments(run_parser)
    run_parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of Pi sessions to run concurrently (default: 1).",
    )

    report_parser = subparsers.add_parser(
        "report", help="Summarize native Pi sessions."
    )
    report_parser.add_argument("benchmark", type=Path)
    add_selection_arguments(report_parser)
    report_parser.add_argument("--verbose", action="store_true")

    arguments = parser.parse_args(argv)
    try:
        load_env(Path(__file__).resolve().with_name(".env"))
        benchmark = load_benchmark(arguments.benchmark)
        if arguments.command == "validate":
            print(
                f"Valid: {len(benchmark.problems)} problems, "
                f"{len(benchmark.models)} models, {benchmark.repetitions} repetitions"
            )
            return 0

        if arguments.selection_file is not None and (
            arguments.model or arguments.problem or arguments.limit is not None
        ):
            raise WorkbenchError(
                "--selection-file cannot be combined with --model, --problem, or --limit"
            )
        selections: tuple[SelectedPrediction, ...] | None = None
        max_transport_attempts = 0
        if arguments.selection_file is not None:
            selections, max_transport_attempts = load_selection_file(
                benchmark, arguments.selection_file
            )
            models = tuple(
                dict.fromkeys(selection.model for selection in selections)
            )
            problems = tuple(
                dict.fromkeys(selection.problem for selection in selections)
            )
        else:
            models = select_models(benchmark, arguments.model)
            problems = select_problems(benchmark, arguments.problem, arguments.limit)
        if arguments.command == "run":
            if shutil.which("pi") is None:
                raise WorkbenchError("Pi executable not found")
            if arguments.workers < 1:
                raise WorkbenchError("--workers must be positive")

            def execute_attempt(
                model: Model, problem: Problem, repetition: int
            ) -> tuple[bool, str]:
                label = f"{model.id} {problem.id} r{repetition:03d}"
                print(
                    f"RUNNING  {label} (timeout {model.timeout_seconds}s)",
                    flush=True,
                )
                try:
                    outcome, path = run_attempt(
                        benchmark, model, problem, repetition
                    )
                    status = write_parsed_output(path)
                    return False, f"{outcome.upper():8} {status.upper():14} {label}"
                except WorkbenchError as error:
                    return True, f"FAILED   NO_OUTPUT      {label}: {error}"

            failures = 0
            with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
                if selections is not None:
                    futures = [
                        executor.submit(
                            run_selected_prediction,
                            benchmark,
                            selection,
                            max_transport_attempts,
                        )
                        for selection in selections
                    ]
                else:
                    futures = [
                        executor.submit(
                            execute_attempt, model, problem, repetition
                        )
                        for model in models
                        for problem in problems
                        for repetition in range(1, benchmark.repetitions + 1)
                    ]
                for future in as_completed(futures):
                    failed, message = future.result()
                    failures += failed
                    print(message, file=sys.stderr if failed else sys.stdout, flush=True)

            print()
            if selections is not None:
                report_selection(benchmark, selections, verbose=False)
            else:
                report(benchmark, models, problems, verbose=False)
            return 1 if failures else 0

        if selections is not None:
            report_selection(benchmark, selections, arguments.verbose)
        else:
            report(benchmark, models, problems, arguments.verbose)
        return 0
    except WorkbenchError as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
