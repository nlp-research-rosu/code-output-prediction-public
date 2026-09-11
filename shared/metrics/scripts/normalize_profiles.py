#!/usr/bin/env python3
"""Generate one canonical long-form complexity profile view.

Benchmark-local measurement files remain authoritative. This script only maps
their retained values and provenance into a shared analysis-facing schema.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = "program-complexity-normalized-v2"
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
METRICS = (
    "Omega_CC",
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
STATUSES = ("MEASURED", "LOWER_BOUND", "NOT_MEASURED", "NOT_REQUESTED")
NUMERIC_RECOVERY_POLICIES = ("preserve", "assume_equal")
COLUMNS = (
    "schema_version",
    "benchmark",
    "problem",
    "arm",
    "language",
    "source_sha256",
    "input_sha256",
    "execution_id",
    "metric",
    "value",
    "value_relation",
    "status",
    "not_measured_reason",
    "adapter",
    "adapter_version",
    "runtime",
    "observation_convention",
    "repetitions",
    "source_profile",
)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def repository_root(path: Path) -> Path:
    for parent in (path, *path.parents):
        if (parent / ".git").exists():
            return parent
    raise ValueError(f"could not find repository root above {path}")


def relative_path(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def canonical_language(value: str) -> str:
    lowered = value.lower()
    if "python" in lowered or "cpython" in lowered:
        return "python"
    if "c++" in lowered or "cpp" in lowered or "clang" in lowered:
        return "cpp"
    raise ValueError(f"unsupported normalized language: {value!r}")


def canonical_execution_id(value: str) -> str:
    if value.startswith("sha256:"):
        digest = value.removeprefix("sha256:")
    else:
        digest = value
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"invalid execution identity: {value!r}")
    return f"sha256:{digest}"


def derived_execution_id(
    source_sha256: str,
    input_sha256: str,
    runtime: str,
    adapter_version: str,
) -> str:
    identity = {
        "adapter_version": adapter_version,
        "input_sha256": input_sha256,
        "runtime": runtime,
        "source_sha256": source_sha256,
    }
    encoded = json.dumps(identity, sort_keys=True, separators=(",", ":")).encode()
    return f"sha256:{sha256_bytes(encoded)}"


def metric_value(value: Any) -> tuple[str, str]:
    if value == "NOT_MEASURED" or value is None:
        return "", "NOT_MEASURED"
    if value == "NOT_REQUESTED":
        return "", "NOT_REQUESTED"
    if isinstance(value, bool):
        raise ValueError("Boolean metric values are invalid")
    try:
        number = int(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"invalid metric value: {value!r}") from error
    if number < 0:
        raise ValueError(f"metric value cannot be negative: {number}")
    return str(number), "MEASURED"


def unavailable_reason(record: dict[str, Any], metric: str) -> str:
    if metric in {"Omega_hat_StateSize", "Omega_hat_StateLoad"}:
        runtime = record.get("runtime_measurement") or {}
        state_failure = runtime.get("state_failure") or {}
        if isinstance(state_failure, dict) and state_failure.get("reason"):
            return str(state_failure["reason"])
        for repetition in runtime.get("repetitions") or []:
            failure = repetition.get("state_failure") or {}
            if isinstance(failure, dict) and failure.get("reason"):
                return str(failure["reason"])
    runtime_failure = (record.get("runtime_measurement") or {}).get("failure")
    if isinstance(runtime_failure, dict):
        for key in ("reason", "message", "error"):
            if runtime_failure.get(key):
                return str(runtime_failure[key])
    elif runtime_failure:
        return str(runtime_failure)
    for failure in record.get("failures") or []:
        if isinstance(failure, dict):
            for key in ("reason", "message", "error"):
                if failure.get(key):
                    return str(failure[key])
        elif failure:
            return str(failure)
    for limitation in (record.get("method_notes") or {}).get("limitations") or []:
        if "NOT_MEASURED" in str(limitation):
            return str(limitation)
    execution = record.get("dynamic_execution") or {}
    for key in ("reason", "failure", "error"):
        if execution.get(key):
            return str(execution[key])
    return "authoritative profile records no exact measurement"


def repetition_count(
    record: dict[str, Any],
    metric: str,
    measurement: dict[str, Any] | None = None,
) -> int:
    if metric == "Omega_CC":
        return 1
    repetitions = (measurement or record.get("runtime_measurement") or {}).get(
        "repetitions"
    )
    if isinstance(repetitions, list) and repetitions:
        return len(repetitions)
    return 1


def normalized_row(
    *,
    benchmark: str,
    problem: str,
    arm: str,
    language: str,
    source_sha256: str,
    input_sha256: str,
    execution_id: str,
    metric: str,
    raw_value: Any,
    value_relation: str = "=",
    status_override: str | None = None,
    reason: str,
    adapter: str,
    adapter_version: str,
    runtime: str,
    observation_convention: str,
    repetitions: int,
    source_profile: str,
) -> dict[str, str]:
    if arm not in ARMS:
        raise ValueError(f"non-canonical arm: {arm!r}")
    if metric not in METRICS:
        raise ValueError(f"unknown metric: {metric!r}")
    value, status = metric_value(raw_value)
    if status_override is not None:
        if status_override != "LOWER_BOUND" or status != "MEASURED":
            raise ValueError(
                f"invalid normalized status override: {status_override!r}"
            )
        status = status_override
    if status in {"MEASURED", "LOWER_BOUND"}:
        reason = ""
    elif not reason:
        reason = "metric was not requested" if status == "NOT_REQUESTED" else (
            "authoritative profile records no exact measurement"
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "benchmark": benchmark,
        "problem": problem,
        "arm": arm,
        "language": canonical_language(language),
        "source_sha256": source_sha256,
        "input_sha256": input_sha256,
        "execution_id": canonical_execution_id(execution_id),
        "metric": metric,
        "value": value,
        "value_relation": value_relation if value else "",
        "status": status,
        "not_measured_reason": reason,
        "adapter": adapter,
        "adapter_version": adapter_version,
        "runtime": runtime,
        "observation_convention": observation_convention,
        "repetitions": str(repetitions),
        "source_profile": source_profile,
    }


def load_jsonl_profiles(
    config: dict[str, Any], config_path: Path, root: Path
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    measurement_root = config_path.parent
    recovery_policy = config.get("numeric_recovery_policy", "preserve")
    if recovery_policy not in NUMERIC_RECOVERY_POLICIES:
        raise ValueError(
            "numeric_recovery_policy must be one of "
            + ", ".join(NUMERIC_RECOVERY_POLICIES)
        )
    for name in config["sources"]:
        path = measurement_root / name
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            execution = record.get("dynamic_execution") or {}
            runtime_measurement = record.get("runtime_measurement") or {}
            recovery_measurement = (
                record.get("timeout_recovery_measurement") or {}
            )
            for metric in METRICS:
                raw_value = (record.get("metrics") or {}).get(
                    metric, "NOT_REQUESTED"
                )
                value_relation = "="
                status_override = None
                uses_recovery_measurement = False
                state_measurement = record.get("state_measurement") or {}
                state_value = state_measurement.get(metric) or {}
                if (
                    metric in {
                        "Omega_hat_NativeTrace",
                        "Omega_hat_StateSize",
                        "Omega_hat_StateLoad",
                    }
                    and raw_value == "NOT_MEASURED"
                    and state_measurement.get("status") == "LOWER_BOUND_TIMEOUT"
                    and state_value.get("relation") == ">="
                ):
                    raw_value = state_value.get("value")
                    uses_recovery_measurement = True
                    if recovery_policy == "preserve":
                        value_relation = ">="
                        status_override = "LOWER_BOUND"
                metric_measurement = (
                    recovery_measurement or runtime_measurement
                    if uses_recovery_measurement
                    else runtime_measurement
                )
                runtime = str(
                    execution.get("runtime")
                    or metric_measurement.get("runtime")
                    or record["language"]
                )
                dynamic_version = str(
                    metric_measurement.get("adapter_version")
                    or execution.get("adapter_version")
                    or execution.get("instrumentation")
                    or ""
                )
                method = str((record.get("metric_methods") or {}).get(metric, ""))
                convention = ""
                if metric in {"Omega_hat_StateSize", "Omega_hat_StateLoad"}:
                    convention = str(
                        metric_measurement.get("observation_convention") or method
                    )
                elif metric == "Omega_hat_NativeTrace":
                    convention = method
                rows.append(
                    normalized_row(
                        benchmark=config["benchmark"],
                        problem=str(record["problem"]),
                        arm=str(record["arm"]),
                        language=str(record["language"]),
                        source_sha256=str(record["source_sha256"]),
                        input_sha256=str(record["input_sha256"]),
                        execution_id=str(execution["execution_id"]),
                        metric=metric,
                        raw_value=raw_value,
                        value_relation=value_relation,
                        status_override=status_override,
                        reason=unavailable_reason(record, metric),
                        adapter=method,
                        adapter_version=(
                            method if metric == "Omega_CC" else dynamic_version
                        ),
                        runtime=runtime,
                        observation_convention=convention,
                        repetitions=repetition_count(
                            record, metric, metric_measurement
                        ),
                        source_profile=relative_path(path, root),
                    )
                )
    return rows


def load_codecontests_profiles(
    config: dict[str, Any], config_path: Path, root: Path
) -> list[dict[str, str]]:
    path = config_path.parent / config["sources"][0]
    document = json.loads(path.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    dynamic_version = str(document["dynamic_adapter_version"])
    runtime = str(document["tools"]["ast_and_lexer"])
    state_convention = str(document["state_adapter"]["observation"])
    value_keys = {
        "Omega_hat_NativeTrace": "native_trace_length",
        "Omega_hat_StateSize": "state_size",
        "Omega_hat_StateLoad": "state_load",
    }
    for program in document["programs"]:
        for arm in ARMS:
            mapping = program["arm_profiles"][arm]
            dynamic = program["dynamic"][mapping["source_input_execution_profile"]]
            static = program["static_profiles"][mapping["static_profile"]]
            execution_id = derived_execution_id(
                str(dynamic["source_sha256"]),
                str(dynamic["input_sha256"]),
                runtime,
                dynamic_version,
            )
            values = {"Omega_CC": static["cyclomatic_complexity"]}
            values.update({metric: dynamic[key] for metric, key in value_keys.items()})
            for metric in METRICS:
                is_static = metric == "Omega_CC"
                rows.append(
                    normalized_row(
                        benchmark=config["benchmark"],
                        problem=str(program["problem_id"]),
                        arm=arm,
                        language=str(program["language"]),
                        source_sha256=str(dynamic["source_sha256"]),
                        input_sha256=str(dynamic["input_sha256"]),
                        execution_id=execution_id,
                        metric=metric,
                        raw_value=values[metric],
                        reason="",
                        adapter=str(
                            config["static_adapter"] if is_static else dynamic_version
                        ),
                        adapter_version=str(
                            config["static_adapter"] if is_static else dynamic_version
                        ),
                        runtime=runtime,
                        observation_convention="" if is_static else (
                            dynamic_version
                            if metric == "Omega_hat_NativeTrace"
                            else state_convention
                        ),
                        repetitions=(
                            1 if is_static else int(dynamic["repeated_measurements"])
                        ),
                        source_profile=relative_path(path, root),
                    )
                )
    return rows


def load_networkx_profiles(
    config: dict[str, Any], config_path: Path, root: Path
) -> list[dict[str, str]]:
    measurement_root = config_path.parent
    csv_path = measurement_root / config["sources"][0]
    manifest_path = measurement_root / config["sources"][1]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    runtime = f"CPython {manifest['python']}; NetworkX {manifest['networkx']}"
    if "metric_methods" in manifest:
        metric_methods = manifest["metric_methods"]
        evidence = manifest.get("profile_evidence") or []
        runtime_measurement = (
            evidence[0].get("runtime_measurement", {}) if evidence else {}
        )
        dynamic_version = str(
            runtime_measurement.get(
                "adapter_version", manifest.get("instrumentation", "")
            )
        )
        state_convention = str(
            runtime_measurement.get("observation_convention", "")
        )
        adapters = {
            "Omega_CC": str(config["static_adapter"]),
            "Omega_hat_NativeTrace": str(metric_methods["Omega_hat_NativeTrace"]),
            "Omega_hat_StateSize": str(metric_methods["Omega_hat_StateSize"]),
            "Omega_hat_StateLoad": str(metric_methods["Omega_hat_StateLoad"]),
        }
        adapter_versions = {
            "Omega_CC": str(config["static_adapter"]),
            "Omega_hat_NativeTrace": dynamic_version,
            "Omega_hat_StateSize": dynamic_version,
            "Omega_hat_StateLoad": dynamic_version,
        }
        observations = {
            "Omega_CC": "",
            "Omega_hat_NativeTrace": str(metric_methods["Omega_hat_NativeTrace"]),
            "Omega_hat_StateSize": state_convention,
            "Omega_hat_StateLoad": state_convention,
        }
    else:
        conventions = manifest["conventions"]
        adapters = {
            "Omega_CC": str(config["static_adapter"]),
            "Omega_hat_NativeTrace": str(conventions["native_trace"]),
            "Omega_hat_StateSize": str(conventions["state_size"]),
            "Omega_hat_StateLoad": str(conventions["state_load"]),
        }
        adapter_versions = adapters
        observations = {
            metric: "" if metric == "Omega_CC" else adapters[metric]
            for metric in METRICS
        }
    rows: list[dict[str, str]] = []
    with csv_path.open(newline="", encoding="utf-8") as handle:
        for record in csv.DictReader(handle):
            for metric in METRICS:
                status = record.get("state_size_status", "OK")
                raw_value: Any = record.get(metric)
                reason = ""
                if (
                    metric in {"Omega_hat_StateSize", "Omega_hat_StateLoad"}
                    and status != "OK"
                ):
                    raw_value = "NOT_MEASURED"
                    reason = status
                if metric == "Omega_CC":
                    repetitions = 1
                elif metric == "Omega_hat_NativeTrace":
                    repetitions = int(record["native_trace_repetitions"])
                else:
                    repetitions = int(record["state_size_repetitions"])
                    if repetitions < 1 and "metric_methods" in manifest:
                        repetitions = int(manifest["repetitions"])
                rows.append(
                    normalized_row(
                        benchmark=config["benchmark"],
                        problem=str(record["case_id"]),
                        arm=str(record["arm_id"]),
                        language="python",
                        source_sha256=str(record["source_sha256"]),
                        input_sha256=str(record["input_sha256"]),
                        execution_id=str(record["execution_id"]),
                        metric=metric,
                        raw_value=raw_value,
                        reason=reason,
                        adapter=adapters[metric],
                        adapter_version=adapter_versions[metric],
                        runtime=runtime,
                        observation_convention=observations[metric],
                        repetitions=repetitions,
                        source_profile=relative_path(csv_path, root),
                    )
                )
    return rows


LOADERS = {
    "canonical-jsonl": load_jsonl_profiles,
    "codecontests-profiles-json": load_codecontests_profiles,
    "networkx-measurements-csv": load_networkx_profiles,
}


def sorted_rows(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    arm_order = {arm: index for index, arm in enumerate(ARMS)}
    metric_order = {metric: index for index, metric in enumerate(METRICS)}
    return sorted(
        rows,
        key=lambda row: (
            row["benchmark"],
            row["problem"],
            arm_order[row["arm"]],
            metric_order[row["metric"]],
        ),
    )


def csv_bytes(rows: list[dict[str, str]]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=COLUMNS, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def manifest_bytes(
    config: dict[str, Any],
    config_path: Path,
    root: Path,
    rows: list[dict[str, str]],
    output: bytes,
) -> bytes:
    script_path = Path(__file__).resolve()
    coverage = {
        metric: {status: 0 for status in STATUSES}
        for metric in METRICS
    }
    for row in rows:
        coverage[row["metric"]][row["status"]] += 1
    inputs = []
    for name in config["sources"]:
        path = config_path.parent / name
        inputs.append({
            "path": relative_path(path, root),
            "sha256": sha256_bytes(path.read_bytes()),
        })
    executions = {
        (row["benchmark"], row["problem"], row["arm"], row["execution_id"])
        for row in rows
    }
    document = {
        "schema_version": SCHEMA_VERSION,
        "benchmark": config["benchmark"],
        "columns": list(COLUMNS),
        "status_vocabulary": list(STATUSES),
        "row_count": len(rows),
        "execution_profile_count": len(executions),
        "coverage": coverage,
        "numeric_recovery_policy": config.get(
            "numeric_recovery_policy", "preserve"
        ),
        "config": {
            "path": relative_path(config_path, root),
            "sha256": sha256_bytes(config_path.read_bytes()),
        },
        "generator": {
            "path": relative_path(script_path, root),
            "sha256": sha256_bytes(script_path.read_bytes()),
        },
        "inputs": inputs,
        "output": {
            "path": relative_path(config_path.parent / "normalized-profiles.csv", root),
            "sha256": sha256_bytes(output),
        },
    }
    return (json.dumps(document, indent=2, sort_keys=True) + "\n").encode("utf-8")


def generate(config_path: Path) -> tuple[bytes, bytes]:
    config_path = config_path.resolve()
    root = repository_root(config_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    loader = LOADERS.get(config.get("source_format"))
    if loader is None:
        raise ValueError(f"unsupported source format: {config.get('source_format')!r}")
    rows = sorted_rows(loader(config, config_path, root))
    output = csv_bytes(rows)
    manifest = manifest_bytes(config, config_path, root, rows, output)
    return output, manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    output, manifest = generate(arguments.config)
    output_path = arguments.config.parent / "normalized-profiles.csv"
    manifest_path = arguments.config.parent / "normalized-profiles-manifest.json"
    if arguments.check:
        stale = []
        for path, expected in ((output_path, output), (manifest_path, manifest)):
            if not path.exists() or path.read_bytes() != expected:
                stale.append(str(path))
        if stale:
            raise SystemExit("stale normalized profiles: " + ", ".join(stale))
        print(f"CURRENT {arguments.config.parent} rows={output.count(b'\n') - 1}")
        return 0
    output_path.write_bytes(output)
    manifest_path.write_bytes(manifest)
    print(f"WROTE {output_path} rows={output.count(b'\n') - 1}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
