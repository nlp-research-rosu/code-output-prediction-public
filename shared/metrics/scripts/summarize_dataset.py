#!/usr/bin/env python3

import argparse
import csv
import hashlib
import io
import json
import math
import os
import statistics
import tempfile
from pathlib import Path
from typing import Any


SCHEMA = "program-complexity-dataset-summary-config-v1"
STATIC_METRICS = ("Omega_CC",)
DYNAMIC_METRICS = (
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
METRICS = (*STATIC_METRICS, *DYNAMIC_METRICS)
NUMERIC_RECOVERY_POLICIES = ("preserve", "assume_equal")
CSV_FIELDS = (
    "dataset_id",
    "label",
    "language",
    "programs",
    "static_profiles",
    "dynamic_profiles",
    "dynamic_executions",
    *METRICS,
)
README_START = "<!-- dataset-complexity-summary:start -->"
README_END = "<!-- dataset-complexity-summary:end -->"

class SummaryError(ValueError):
    pass


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        dir=path.parent, prefix=f".{path.name}.", text=True
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise SummaryError(f"profile file does not exist: {path}")
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise SummaryError(f"invalid JSON at {path}:{line_number}: {error}") from error
        if not isinstance(record, dict):
            raise SummaryError(f"profile at {path}:{line_number} must be an object")
        records.append(record)
    return records


def numeric(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def metric_value(
    record: dict[str, Any], metric: str, recovery_policy: str = "preserve"
) -> tuple[Any, str]:
    value = (record.get("metrics") or {}).get(metric)
    if numeric(value):
        return value, "="
    retained = (record.get("state_measurement") or {}).get(metric)
    if isinstance(retained, dict):
        bound = retained.get("value")
        if retained.get("relation") == ">=" and numeric(bound):
            return bound, "=" if recovery_policy == "assume_equal" else ">="
    return None, ""


def static_identity(record: dict[str, Any]) -> tuple[Any, ...]:
    methods = record.get("metric_methods") or {}
    return (
        record.get("problem"),
        record.get("source_sha256"),
        record.get("language"),
        tuple((metric, methods.get(metric)) for metric in STATIC_METRICS),
    )


def static_signature(record: dict[str, Any]) -> tuple[Any, ...]:
    metrics = record.get("metrics") or {}
    return (*static_identity(record), tuple((metric, metrics.get(metric)) for metric in STATIC_METRICS))


def dynamic_signature(
    record: dict[str, Any], recovery_policy: str
) -> tuple[Any, ...]:
    execution = record.get("dynamic_execution") or {}
    return (
        execution.get("execution_id"),
        record.get("problem"),
        record.get("language"),
        tuple(
            (metric, *metric_value(record, metric, recovery_policy))
            for metric in DYNAMIC_METRICS
        ),
    )


def resolve_paths(config_path: Path, values: Any, field: str) -> list[Path]:
    if not isinstance(values, list) or not values or not all(isinstance(value, str) for value in values):
        raise SummaryError(f"{field} must be a non-empty list of paths")
    return [(config_path.parent / value).resolve() for value in values]


def portable_path(config_path: Path, path: Path) -> str:
    return Path(os.path.relpath(path, config_path.parent)).as_posix()


def summarize_row(config_path: Path, row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    dataset_id = row.get("dataset_id")
    label = row.get("label")
    if not isinstance(dataset_id, str) or not dataset_id:
        raise SummaryError("dataset_id must be a non-empty string")
    if not isinstance(label, str) or not label:
        raise SummaryError(f"label for {dataset_id} must be a non-empty string")
    recovery_policy = row.get("numeric_recovery_policy", "preserve")
    if recovery_policy not in NUMERIC_RECOVERY_POLICIES:
        raise SummaryError(
            "numeric_recovery_policy must be one of "
            + ", ".join(NUMERIC_RECOVERY_POLICIES)
        )

    static_paths = resolve_paths(config_path, row.get("static_profiles"), "static_profiles")
    dynamic_values = row.get("dynamic_profiles", [])
    if not isinstance(dynamic_values, list) or not all(isinstance(value, str) for value in dynamic_values):
        raise SummaryError("dynamic_profiles must be a list of paths")
    dynamic_paths = [(config_path.parent / value).resolve() for value in dynamic_values]
    static_records = [record for path in static_paths for record in load_jsonl(path)]
    dynamic_records = [record for path in dynamic_paths for record in load_jsonl(path)]

    languages = {record.get("language") for record in [*static_records, *dynamic_records]}
    if None in languages or len(languages) != 1:
        raise SummaryError(f"{dataset_id} must contain exactly one language")
    language = next(iter(languages))

    static_by_identity: dict[tuple[Any, ...], dict[str, Any]] = {}
    identities_by_problem: dict[str, set[tuple[Any, ...]]] = {}
    for record in static_records:
        problem = record.get("problem")
        if not isinstance(problem, str) or not problem:
            raise SummaryError(f"{dataset_id} contains a static profile without problem")
        identity = static_identity(record)
        existing = static_by_identity.get(identity)
        if existing is not None and static_signature(existing) != static_signature(record):
            raise SummaryError(f"conflicting static values for {dataset_id}/{problem}")
        static_by_identity[identity] = record
        identities_by_problem.setdefault(problem, set()).add(identity)
    ambiguous = sorted(problem for problem, identities in identities_by_problem.items() if len(identities) > 1)
    if ambiguous:
        raise SummaryError(
            f"{dataset_id} has multiple static identities for problem(s): {', '.join(ambiguous[:5])}"
        )

    dynamic_by_execution: dict[str, dict[str, Any]] = {}
    dynamic_unavailable = []
    for record in dynamic_records:
        execution = record.get("dynamic_execution") or {}
        execution_id = execution.get("execution_id")
        if execution.get("status") != "OK" or not isinstance(execution_id, str) or not execution_id:
            dynamic_unavailable.append(record)
            continue
        existing = dynamic_by_execution.get(execution_id)
        if existing is not None and dynamic_signature(
            existing, recovery_policy
        ) != dynamic_signature(record, recovery_policy):
            raise SummaryError(f"conflicting dynamic values for execution {execution_id}")
        dynamic_by_execution[execution_id] = record

    static_problems = set(identities_by_problem)
    if dynamic_paths:
        dynamic_problems = {record.get("problem") for record in dynamic_records}
        if dynamic_problems != static_problems:
            missing = sorted(static_problems - dynamic_problems)
            extra = sorted(dynamic_problems - static_problems)
            raise SummaryError(
                f"{dataset_id} dynamic problem set differs from static set; missing={missing[:5]}, extra={extra[:5]}"
            )

    metric_records = {
        **{metric: list(static_by_identity.values()) for metric in STATIC_METRICS},
        **{metric: list(dynamic_by_execution.values()) for metric in DYNAMIC_METRICS},
    }
    medians: dict[str, Any] = {}
    coverage: dict[str, dict[str, int]] = {}
    for metric, records in metric_records.items():
        values = [
            metric_value(record, metric, recovery_policy) for record in records
        ]
        measured = [value for value, relation in values if relation in {"=", ">="}]
        exact = sum(relation == "=" for _, relation in values)
        lower_bound = sum(relation == ">=" for _, relation in values)
        medians[metric] = statistics.median(measured) if measured else "NOT_MEASURED"
        unavailable = len(values) - len(measured)
        if metric in DYNAMIC_METRICS:
            unavailable += len(dynamic_unavailable)
        coverage[metric] = {
            "measured": len(measured),
            "exact": exact,
            "lower_bound": lower_bound,
            "unavailable": unavailable,
        }

    result = {
        "dataset_id": dataset_id,
        "label": label,
        "language": language,
        "programs": len(static_problems),
        "static_profiles": len(static_by_identity),
        "dynamic_profiles": len(dynamic_records),
        "dynamic_executions": len(dynamic_by_execution),
        **medians,
    }
    manifest = {
        "dataset_id": dataset_id,
        "label": label,
        "language": language,
        "note": row.get("note", ""),
        "numeric_recovery_policy": recovery_policy,
        "programs": len(static_problems),
        "static_profiles": {
            "selected": len(static_records),
            "unique": len(static_by_identity),
            "files": [
                {"path": portable_path(config_path, path), "sha256": sha256(path)}
                for path in static_paths
            ],
        },
        "dynamic_profiles": {
            "selected": len(dynamic_records),
            "unavailable": len(dynamic_unavailable),
            "unique_executions": len(dynamic_by_execution),
            "files": [
                {"path": portable_path(config_path, path), "sha256": sha256(path)}
                for path in dynamic_paths
            ],
        },
        "metric_coverage": coverage,
    }
    return result, manifest


def csv_value(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def compact(value: Any) -> str:
    if value == "NOT_MEASURED":
        return value
    number = float(value)
    for divisor, suffix in ((1_000_000, "M"), (1_000, "K")):
        if abs(number) >= divisor:
            return f"{number / divisor:.3g}{suffix}"
    if number.is_integer():
        return str(int(number))
    return f"{number:.6g}"


def render_csv(rows: list[dict[str, Any]]) -> str:
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: csv_value(row[field]) for field in CSV_FIELDS})
    return output.getvalue()


def render_markdown(rows: list[dict[str, Any]], manifests: list[dict[str, Any]]) -> str:
    columns = ["Dataset", "#Programs", *METRICS]
    has_lower_bounds = any(
        metric["lower_bound"]
        for manifest in manifests
        for metric in manifest["metric_coverage"].values()
    )
    lines = [
        README_START,
        "## Dataset median summary",
        "",
        "All metric cells are medians. Dynamic metrics are marked with a hat.",
    ]
    if has_lower_bounds:
        lines.extend(
            [
                "Exact values and observed `>=` bounds both enter the median.",
                "",
            ]
        )
    else:
        lines.extend(["Every numeric value enters as an ordinary measurement.", ""])
    lines.extend([
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ])
    for row in rows:
        values = [row["label"], str(row["programs"]), *(compact(row[metric]) for metric in METRICS)]
        lines.append("| " + " | ".join(values) + " |")
    lines.extend(["", "### Cohort", ""])
    for row, manifest in zip(rows, manifests, strict=True):
        note = manifest["note"] or "No additional cohort note."
        lines.append(
            f"- **{row['label']}**: {row['programs']} unique programs; "
            f"{row['dynamic_executions']} unique dynamic executions. {note}"
        )
    lines.extend(
        [
            "",
            "Metric names, units, and calculation follow the shared definitions linked",
            "by this measurement package. `NOT_MEASURED` means unavailable, not zero.",
        ]
    )
    lines.extend(
        [
            "",
            "Raw, unrounded medians are in `dataset-summary.csv`. Input hashes,",
            "deduplication counts, and per-metric availability are in",
            "`dataset-summary-manifest.json`.",
            README_END,
        ]
    )
    return "\n".join(lines)


def updated_readme(path: Path, section: str) -> str:
    content = path.read_text(encoding="utf-8")
    if content.count(README_START) != 1 or content.count(README_END) != 1:
        raise SummaryError(
            f"README must contain exactly one {README_START} and {README_END}: {path}"
        )
    start = content.index(README_START)
    end = content.index(README_END, start) + len(README_END)
    return content[:start] + section + content[end:]


def generate(
    config_path: Path, output: Path, readme: Path | None = None
) -> dict[str, int]:
    config_path = config_path.resolve()
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise SummaryError(f"cannot read config {config_path}: {error}") from error
    if config.get("schema") != SCHEMA:
        raise SummaryError(f"config schema must be {SCHEMA}")
    configured_rows = config.get("rows")
    if not isinstance(configured_rows, list) or not configured_rows:
        raise SummaryError("config rows must be a non-empty list")
    identifiers = [row.get("dataset_id") for row in configured_rows if isinstance(row, dict)]
    if len(identifiers) != len(configured_rows) or len(set(identifiers)) != len(identifiers):
        raise SummaryError("config rows must be objects with unique dataset_id values")

    rows = []
    manifests = []
    for configured_row in configured_rows:
        result, manifest = summarize_row(config_path, configured_row)
        rows.append(result)
        manifests.append(manifest)
    readme_path = readme.resolve() if readme is not None else None
    readme_content = (
        updated_readme(readme_path, render_markdown(rows, manifests))
        if readme_path is not None
        else None
    )
    output = output.resolve()
    atomic_write(output / "dataset-summary.csv", render_csv(rows))
    manifest = {
        "schema": "program-complexity-dataset-summary-v1",
        "config": {"path": config_path.name, "sha256": sha256(config_path)},
        "metrics": {"static": list(STATIC_METRICS), "dynamic": list(DYNAMIC_METRICS)},
        "rows": manifests,
    }
    atomic_write(
        output / "dataset-summary-manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
    )
    if readme_path is not None and readme_content is not None:
        atomic_write(readme_path, readme_content)
    return {"rows": len(rows), "programs": sum(row["programs"] for row in rows)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize per-program complexity profiles by dataset")
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--readme", type=Path)
    arguments = parser.parse_args()
    try:
        summary = generate(arguments.config, arguments.output, arguments.readme)
    except SummaryError as error:
        parser.error(str(error))
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
