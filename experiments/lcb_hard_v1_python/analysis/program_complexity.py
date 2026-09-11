#!/usr/bin/env python3
"""Measure workbench programs with the selected PLSemanticsBench profile."""

from __future__ import annotations

import argparse
import ast
import csv
import fnmatch
import hashlib
import importlib.util
import io
import json
import math
import os
import platform
import subprocess
import sys
import tempfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from importlib import metadata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PYTHON_COMPLEXITY_PATH = Path(__file__).with_name("legacy_python_complexity.py")
PYTHON_COMPLEXITY_SPEC = importlib.util.spec_from_file_location(
    "shared_python_complexity", PYTHON_COMPLEXITY_PATH
)
if PYTHON_COMPLEXITY_SPEC is None or PYTHON_COMPLEXITY_SPEC.loader is None:
    raise RuntimeError(f"Could not load {PYTHON_COMPLEXITY_PATH}")
PYTHON_COMPLEXITY = importlib.util.module_from_spec(PYTHON_COMPLEXITY_SPEC)
sys.modules[PYTHON_COMPLEXITY_SPEC.name] = PYTHON_COMPLEXITY
PYTHON_COMPLEXITY_SPEC.loader.exec_module(PYTHON_COMPLEXITY)
PythonDynamicTransformer = PYTHON_COMPLEXITY.PythonDynamicTransformer
measure_python_static_v2 = PYTHON_COMPLEXITY.measure_python_static

NOT_MEASURED = "NOT_MEASURED"
STATIC_METRICS = ("Omega_CC",)
DYNAMIC_METRICS: tuple[str, ...] = ()
RUNTIME_METRICS = (
    "Omega_hat_NativeTrace",
    "Omega_hat_StateSize",
    "Omega_hat_StateLoad",
)
PYTHON_RUNTIME_ADAPTER_VERSION = "python-cpython-monitoring-state-v7"
PYTHON_RUNTIME_OBSERVATION_CONVENTION = (
    "initial-next-opcode-mutation-boundary-return-v1"
)
ALL_DYNAMIC_METRICS = (*DYNAMIC_METRICS, *RUNTIME_METRICS)
METRICS = (*STATIC_METRICS, *ALL_DYNAMIC_METRICS)
GROUPING_PUNCTUATION = {"(", ")", "[", "]", "{", "}", ",", ":", ";", "."}
SCHEMA_VERSION = 6
PYTHON_DYNAMIC_INSTRUMENTATION = "python-ast-runtime-v3"
PYTHON_METRIC_METHODS = {
    "Omega_CC": "python-control-flow-v2",
    "Omega_hat_NativeTrace": "python-cpython-monitoring-instruction-v2",
    "Omega_hat_StateSize": "python-cpython-program-state-v5",
    "Omega_hat_StateLoad": "python-cpython-program-state-sum-v1",
}
CPP_METRIC_METHODS = {
    "Omega_CC": "cpp-preprocessed-control-flow-v1",
    "Omega_hat_NativeTrace": "cpp-dynamic-not-measured-v1",
    "Omega_hat_StateSize": "cpp-dynamic-not-measured-v1",
    "Omega_hat_StateLoad": "cpp-dynamic-not-measured-v1",
}
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
LANGUAGES = {
    "python": (".py", "Python 3.12"),
    "cpp": (".cpp", "C++20 benchmark source"),
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class DynamicTarget:
    source_path: Path | None
    source_bytes: bytes
    cwd: Path
    oracle_path: Path
    target_kind: str
    source_arm: str
    execution_id: str


class StateCheckpointTransformer(ast.NodeTransformer):
    def __init__(
        self,
        target_line: int,
        fields: list[str],
        placement: str,
        inside_threshold: int,
    ) -> None:
        self.target_line = target_line
        self.fields = fields
        self.placement = placement
        self.inside_threshold = inside_threshold
        self.matches = 0

    def checkpoint(self, node: ast.AST, threshold: int) -> ast.If:
        payload = ast.Dict(
            keys=[ast.Constant(field) for field in self.fields],
            values=[
                ast.parse(field, mode="eval").body for field in self.fields
            ],
        )
        serialized = ast.Call(
            func=ast.Attribute(
                value=ast.Name(id="_lcb_json", ctx=ast.Load()),
                attr="dumps",
                ctx=ast.Load(),
            ),
            args=[payload],
            keywords=[
                ast.keyword(arg="ensure_ascii", value=ast.Constant(False)),
                ast.keyword(arg="sort_keys", value=ast.Constant(True)),
                ast.keyword(
                    arg="separators",
                    value=ast.Tuple(
                        elts=[ast.Constant(","), ast.Constant(":")], ctx=ast.Load()
                    ),
                ),
                ast.keyword(arg="allow_nan", value=ast.Constant(False)),
            ],
        )
        write = ast.Expr(
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Attribute(
                        value=ast.Name(id="_lcb_sys", ctx=ast.Load()),
                        attr="stdout",
                        ctx=ast.Load(),
                    ),
                    attr="write",
                    ctx=ast.Load(),
                ),
                args=[ast.BinOp(left=serialized, op=ast.Add(), right=ast.Constant("\n"))],
                keywords=[],
            )
        )
        condition = ast.Compare(
            left=ast.Subscript(
                value=ast.Name(id="_lcb_count", ctx=ast.Load()),
                slice=ast.Constant(0),
                ctx=ast.Load(),
            ),
            ops=[ast.Gt()],
            comparators=[ast.Constant(threshold)],
        )
        return ast.copy_location(
            ast.If(
                test=condition,
                body=[write, ast.Raise(exc=ast.Name(id="SystemExit", ctx=ast.Load()))],
                orelse=[],
            ),
            node,
        )

    def _visit_loop(
        self, node: ast.For | ast.AsyncFor | ast.While
    ) -> ast.AST | list[ast.stmt]:
        node = self.generic_visit(node)
        body_line = node.body[0].lineno if node.body else None
        if body_line != self.target_line:
            return node
        self.matches += 1
        increment = ast.AugAssign(
            target=ast.Subscript(
                value=ast.Name(id="_lcb_count", ctx=ast.Load()),
                slice=ast.Constant(0),
                ctx=ast.Store(),
            ),
            op=ast.Add(),
            value=ast.Constant(1),
        )
        node.body.insert(0, ast.copy_location(increment, node))
        if self.placement == "inside":
            node.body.insert(1, self.checkpoint(node, self.inside_threshold - 1))
            return node
        if node.orelse:
            node.orelse.insert(0, self.checkpoint(node, 1000))
            return [node, self.checkpoint(node, 1000)]
        return [node, self.checkpoint(node, 1000)]

    visit_For = _visit_loop
    visit_AsyncFor = _visit_loop
    visit_While = _visit_loop


def build_state_checkpoint_source(
    source: bytes,
    target_line: int,
    fields: list[str],
    placement: str,
    inside_threshold: int = 502,
) -> bytes:
    if placement not in {"inside", "post"}:
        raise ValueError(f"unsupported checkpoint placement: {placement}")
    if not fields:
        raise ValueError("state checkpoint must contain at least one expression")
    try:
        for field in fields:
            ast.parse(field, mode="eval")
    except (SyntaxError, TypeError) as exc:
        raise ValueError(
            "state checkpoint fields must be valid Python expressions"
        ) from exc
    tree = ast.parse(source.decode("utf-8"))
    transformer = StateCheckpointTransformer(
        target_line, fields, placement, inside_threshold
    )
    tree = transformer.visit(tree)
    if transformer.matches != 1:
        raise ValueError(
            f"expected one target loop at line {target_line}, found {transformer.matches}"
        )
    prefix = ast.parse(
        "import json as _lcb_json\nimport sys as _lcb_sys\n_lcb_count = [0]\n"
    ).body
    insert_at = 0
    if (
        tree.body
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(tree.body[0].value, ast.Constant)
        and isinstance(tree.body[0].value.value, str)
    ):
        insert_at = 1
    while (
        insert_at < len(tree.body)
        and isinstance(tree.body[insert_at], ast.ImportFrom)
        and tree.body[insert_at].module == "__future__"
    ):
        insert_at += 1
    tree.body[insert_at:insert_at] = prefix
    ast.fix_missing_locations(tree)
    return (ast.unparse(tree) + "\n").encode("utf-8")


def build_post_loop_checkpoint_source(
    source: bytes, target_line: int, fields: list[str]
) -> bytes:
    return build_state_checkpoint_source(source, target_line, fields, "post")


def dynamic_execution_id(source_hash: str, input_hash: str) -> str:
    identity = {
        "source_sha256": source_hash,
        "input_sha256": input_hash,
        "runtime": f"CPython {platform.python_version()}",
        "instrumentation": PYTHON_DYNAMIC_INSTRUMENTATION,
    }
    return "sha256:" + sha256(
        json.dumps(identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    )


def resolve_dynamic_target(
    root: Path, benchmark: Path, case: dict[str, Any]
) -> DynamicTarget:
    arm = root.name
    program = root / "program.py"
    oracle = root / "ground-output.txt"
    target_kind = "arm-program-output"
    source_arm = arm
    source_path: Path | None = program
    source_bytes = program.read_bytes()
    if arm == "inside-loop-state":
        target_kind = "inside-selected-loop"
    elif arm == "post-loop-state":
        target_kind = "immediately-after-selected-loop"
    source_hash = sha256(source_bytes)
    input_hash = sha256((root / "input.txt").read_bytes())
    return DynamicTarget(
        source_path=source_path,
        source_bytes=source_bytes,
        cwd=root,
        oracle_path=oracle,
        target_kind=target_kind,
        source_arm=source_arm,
        execution_id=dynamic_execution_id(source_hash, input_hash),
    )


def halstead(operators: list[str], operands: list[str]) -> tuple[float, int]:
    vocabulary = len(set(operators)) + len(set(operands))
    length = len(operators) + len(operands)
    volume = 0.0 if vocabulary <= 1 else length * math.log2(vocabulary)
    return round(volume, 6), vocabulary


def measure_python_static(source: str) -> dict[str, int | float]:
    return measure_python_static_v2(source)


def run_instrumented_python(source_path: Path, metrics_path: Path) -> int:
    source = source_path.read_text(encoding="utf-8")
    tree = PythonDynamicTransformer().visit(
        ast.parse(source, filename=str(source_path))
    )
    ast.fix_missing_locations(tree)
    state = {
        "max_if_depth": 0,
        "max_loop_depth": 0,
        "assignments": 0,
    }

    def assign(count: int) -> None:
        state["assignments"] += count

    def assign_value(count: int, value: Any) -> Any:
        assign(count)
        return value

    def mark_if(depth: int) -> None:
        state["max_if_depth"] = max(state["max_if_depth"], depth)

    def mark_loop(depth: int) -> None:
        state["max_loop_depth"] = max(state["max_loop_depth"], depth)

    def if_expression(depth: int, value: Any) -> bool:
        mark_if(depth)
        return bool(value)

    def if_filter(depth: int, value: Any) -> bool:
        taken = bool(value)
        if taken:
            mark_if(depth)
        return taken

    def counted_iter(depth: int, count: int, iterable: Any) -> Any:
        for value in iterable:
            mark_loop(depth)
            assign(count)
            yield value

    globals_dict: dict[str, Any] = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
        "_plsb_measure_assign": assign,
        "_plsb_measure_assign_value": assign_value,
        "_plsb_measure_if": mark_if,
        "_plsb_measure_if_expr": if_expression,
        "_plsb_measure_if_filter": if_filter,
        "_plsb_measure_loop": mark_loop,
        "_plsb_measure_iter": counted_iter,
    }
    status = "ok"
    error = None
    try:
        exec(compile(tree, str(source_path), "exec"), globals_dict)
    except SystemExit:
        pass
    except BaseException as exc:  # The benchmark program is the isolation boundary.
        status = "error"
        error = f"{type(exc).__name__}: {exc}"
    metrics_path.write_text(
        json.dumps(
            {
                "status": status,
                "error": error,
                "Omega_hat_If": state["max_if_depth"],
                "Omega_hat_Loop": state["max_loop_depth"],
                "Omega_hat_Assign": state["assignments"],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return 0 if status == "ok" else 1


def measure_python_dynamic(
    source_path: Path | None,
    input_path: Path,
    oracle_path: Path,
    timeout: int,
    *,
    source_bytes: bytes | None = None,
    execution_cwd: Path | None = None,
    oracle_mode: str = "exact",
) -> tuple[dict[str, int] | None, str | None]:
    if source_path is None:
        if source_bytes is None:
            raise ValueError("generated dynamic source bytes are required")
        with tempfile.TemporaryDirectory(prefix="program-complexity-target-") as directory:
            generated = Path(directory) / "program.py"
            generated.write_bytes(source_bytes)
            return _measure_python_dynamic_path(
                generated,
                input_path,
                oracle_path,
                timeout,
                execution_cwd or input_path.parent,
                oracle_mode,
            )
    return _measure_python_dynamic_path(
        source_path,
        input_path,
        oracle_path,
        timeout,
        execution_cwd or source_path.parent,
        oracle_mode,
    )


def _measure_python_dynamic_path(
    source_path: Path,
    input_path: Path,
    oracle_path: Path,
    timeout: int,
    execution_cwd: Path,
    oracle_mode: str,
) -> tuple[dict[str, int] | None, str | None]:
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir()),
    }
    if "PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT" in os.environ:
        environment["PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT"] = os.environ[
            "PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT"
        ]
    if "PROGRAM_COMPLEXITY_STATE_COUNTER" in os.environ:
        environment["PROGRAM_COMPLEXITY_STATE_COUNTER"] = os.environ[
            "PROGRAM_COMPLEXITY_STATE_COUNTER"
        ]
    try:
        natural = subprocess.run(
            [sys.executable, str(source_path)],
            input=input_path.read_bytes(),
            capture_output=True,
            timeout=timeout,
            cwd=execution_cwd,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return None, f"natural execution timed out after {timeout}s"
    if natural.returncode != 0:
        error = natural.stderr.decode("utf-8", errors="replace").strip()[:300]
        return None, f"natural runtime exited {natural.returncode}: {error}"
    expected_stdout = oracle_path.read_bytes()
    if not stdout_matches_oracle(natural.stdout, expected_stdout, oracle_mode):
        return None, "natural stdout did not match ground-output.txt"
    with tempfile.TemporaryDirectory(prefix="program-complexity-") as directory:
        metrics_path = Path(directory) / "metrics.json"
        try:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    "_run-python",
                    str(source_path),
                    str(metrics_path),
                ],
                input=input_path.read_bytes(),
                capture_output=True,
                timeout=timeout,
                cwd=execution_cwd,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            return None, f"dynamic execution timed out after {timeout}s"
        if not metrics_path.exists():
            return (
                None,
                f"instrumented runtime exited {completed.returncode} without metrics",
            )
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        if payload["status"] != "ok":
            return None, payload.get("error") or "instrumented runtime failed"
        if not stdout_matches_oracle(
            completed.stdout, expected_stdout, oracle_mode
        ):
            return None, "instrumented stdout did not match ground-output.txt"
        return {
            key: int(payload[key])
            for key in ("Omega_hat_If", "Omega_hat_Loop", "Omega_hat_Assign")
        }, None


def stdout_matches_oracle(actual: bytes, expected: bytes, mode: str) -> bool:
    if mode == "exact":
        return actual == expected
    if mode != "last-json-line":
        raise ValueError(f"unsupported oracle mode: {mode}")
    lines = actual.splitlines()
    candidate = lines[-1] if lines else b""
    try:
        options = {
            "ensure_ascii": False,
            "sort_keys": True,
            "separators": (",", ":"),
            "allow_nan": False,
        }
        return json.dumps(json.loads(candidate), **options) == json.dumps(
            json.loads(expected), **options
        )
    except (ValueError, TypeError, UnicodeDecodeError):
        return False


def measure_python_runtime_metrics(
    source_path: Path | None,
    input_path: Path,
    oracle_path: Path,
    timeout: int,
    artifact_root: Path,
    source_label: str,
    *,
    source_bytes: bytes | None = None,
    execution_cwd: Path | None = None,
    oracle_mode: str = "exact",
    repetitions: int = 1,
) -> tuple[dict[str, int | str], dict[str, Any], str | None]:
    if source_path is None:
        if source_bytes is None:
            raise ValueError("generated runtime source bytes are required")
        with tempfile.TemporaryDirectory(prefix="program-runtime-target-") as directory:
            generated = Path(directory) / "program.py"
            generated.write_bytes(source_bytes)
            return _measure_python_runtime_metrics_path(
                generated,
                input_path,
                oracle_path,
                timeout,
                artifact_root,
                source_label,
                execution_cwd or input_path.parent,
                oracle_mode,
                repetitions,
            )
    return _measure_python_runtime_metrics_path(
        source_path,
        input_path,
        oracle_path,
        timeout,
        artifact_root,
        source_label,
        execution_cwd or source_path.parent,
        oracle_mode,
        repetitions,
    )


def _measure_python_runtime_metrics_path(
    source_path: Path,
    input_path: Path,
    oracle_path: Path,
    timeout: int,
    artifact_root: Path,
    source_label: str,
    execution_cwd: Path,
    oracle_mode: str,
    repetition_count: int,
) -> tuple[dict[str, int | str], dict[str, Any], str | None]:
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "PYTHONHASHSEED": "0",
        "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
        "TMPDIR": os.environ.get("TMPDIR", tempfile.gettempdir()),
    }
    if "PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT" in os.environ:
        environment["PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT"] = os.environ[
            "PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT"
        ]
    if "PROGRAM_COMPLEXITY_STATE_COUNTER" in os.environ:
        environment["PROGRAM_COMPLEXITY_STATE_COUNTER"] = os.environ[
            "PROGRAM_COMPLEXITY_STATE_COUNTER"
        ]
    expected_stdout = oracle_path.read_bytes()
    try:
        natural = subprocess.run(
            [sys.executable, str(source_path)],
            input=input_path.read_bytes(),
            capture_output=True,
            timeout=timeout,
            cwd=execution_cwd,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return _unavailable_runtime_metrics(
            "natural execution timed out", source_label, artifact_root
        )
    if natural.returncode != 0 or not stdout_matches_oracle(
        natural.stdout, expected_stdout, oracle_mode
    ):
        reason = (
            f"natural runtime exited {natural.returncode}"
            if natural.returncode != 0
            else "natural stdout did not match ground-output.txt"
        )
        return _unavailable_runtime_metrics(reason, source_label, artifact_root)
    repetitions: list[dict[str, Any]] = []
    for repetition in range(1, repetition_count + 1):
        artifact = artifact_root / f"repetition-{repetition}.csv.gz"
        result_path = artifact_root / f"repetition-{repetition}.json"
        command = [
            sys.executable,
            str(Path(__file__).with_name("python_runtime_metrics.py")),
            str(source_path),
            source_label,
            str(artifact),
            str(result_path),
        ]
        try:
            completed = subprocess.run(
                command,
                input=input_path.read_bytes(),
                capture_output=True,
                timeout=timeout,
                cwd=execution_cwd,
                env=environment,
            )
        except subprocess.TimeoutExpired:
            partial_progress = None
            if result_path.exists():
                try:
                    partial_progress = json.loads(
                        result_path.read_text(encoding="utf-8")
                    )
                except (OSError, ValueError):
                    partial_progress = None
                result_path.unlink(missing_ok=True)
            partial_repetitions = list(repetitions)
            if isinstance(partial_progress, dict):
                partial_repetitions.append(
                    {
                        **partial_progress,
                        "repetition": repetition,
                        "partial": True,
                    }
                )
            return _unavailable_runtime_metrics(
                f"traced repetition {repetition} timed out",
                source_label,
                artifact_root,
                partial_repetitions,
            )
        if not result_path.exists():
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            detail = f": {stderr[:500]}" if stderr else ""
            return _unavailable_runtime_metrics(
                f"traced repetition {repetition} exited {completed.returncode} without result{detail}",
                source_label,
                artifact_root,
                repetitions,
            )
        payload = json.loads(result_path.read_text(encoding="utf-8"))
        result_path.unlink()
        if payload["status"] != "ok" or completed.returncode != 0:
            return _unavailable_runtime_metrics(
                payload.get("error")
                or f"traced repetition {repetition} exited {completed.returncode}",
                source_label,
                artifact_root,
                repetitions,
            )
        if not stdout_matches_oracle(completed.stdout, expected_stdout, oracle_mode):
            return _unavailable_runtime_metrics(
                f"traced repetition {repetition} stdout did not match oracle",
                source_label,
                artifact_root,
                repetitions,
            )
        repetitions.append(
            {
                **payload,
                "repetition": repetition,
                "raw_artifact": str(artifact),
            }
        )
    trace_values = {
        int(repetition["Omega_hat_NativeTrace"]) for repetition in repetitions
    }
    if len(trace_values) != 1:
        return _unavailable_runtime_metrics(
            "NativeTrace counts differed across repetitions",
            source_label,
            artifact_root,
            repetitions,
        )
    raw_series = {
        (
            repetition["raw_artifact_sha256"],
            int(repetition["raw_observation_rows"]),
        )
        for repetition in repetitions
    }
    if len(raw_series) != 1:
        return _unavailable_runtime_metrics(
            "raw state observations differed across repetitions",
            source_label,
            artifact_root,
            repetitions,
        )
    state_failures = [repetition["state_failure"] for repetition in repetitions]
    state_available = all(failure is None for failure in state_failures)
    if state_available:
        state_values = {
            (
                int(repetition["Omega_hat_StateSize"]),
                int(repetition["Omega_hat_StateLoad"]),
                int(repetition["state_size_peak_event"]),
                repetition["raw_artifact_sha256"],
            )
            for repetition in repetitions
        }
        if len(state_values) != 1:
            return _unavailable_runtime_metrics(
                "state observations differed across repetitions",
                source_label,
                artifact_root,
                repetitions,
            )
    elif not all(failure == state_failures[0] for failure in state_failures):
        return _unavailable_runtime_metrics(
            "state traversal failure differed across repetitions",
            source_label,
            artifact_root,
            repetitions,
        )
    first = repetitions[0]
    for repetition in repetitions:
        repetition.pop("Omega_hat_StateCount", None)
        repetition.pop("state_count_peak_event", None)
    metrics: dict[str, int | str] = {
        "Omega_hat_NativeTrace": trace_values.pop(),
        "Omega_hat_StateSize": (
            int(first["Omega_hat_StateSize"]) if state_available else NOT_MEASURED
        ),
        "Omega_hat_StateLoad": (
            int(first["Omega_hat_StateLoad"]) if state_available else NOT_MEASURED
        ),
    }
    metadata = {
        "status": "OK" if state_available else "PARTIAL",
        "source": source_label,
        "adapter_version": first["adapter_version"],
        "state_counter": first["state_counter"],
        "observation_convention": first["observation_convention"],
        "runtime": f"{platform.python_implementation()} {platform.python_version()}",
        "interpreter_flags": list(sys.flags),
        "cwd": str(execution_cwd),
        "timeout_seconds": timeout,
        "state_cell_visit_limit": first["state_cell_visit_limit"],
        "frame_selection": "normalized target source path including nested target frames",
        "root_selection": "AST-declared initialized globals, parameters, and active locals",
        "supported_values": [
            "None",
            "bool",
            "int",
            "float",
            "complex",
            "str",
            "bytes",
            "bytearray",
            "list",
            "tuple",
            "set",
            "frozenset",
            "dict",
            "range",
            "collections.deque",
            "opaque imported-library values with internal fields excluded",
            "objects with safely enumerable __dict__ fields",
        ],
        "excluded_values": ["modules", "functions", "methods", "classes"],
        "oracle_result": "MATCH",
        "state_failure": state_failures[0],
        "state_size_peak_event": (
            int(first["state_size_peak_event"]) if state_available else None
        ),
        "repetitions": repetitions,
    }
    return metrics, metadata, None


def _unavailable_runtime_metrics(
    reason: str,
    source_label: str,
    artifact_root: Path,
    repetitions: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, int | str], dict[str, Any], str]:
    return (
        {metric: NOT_MEASURED for metric in RUNTIME_METRICS},
        {
            "status": NOT_MEASURED,
            "source": source_label,
            "artifact_root": str(artifact_root),
            "failure": reason,
            "repetitions": repetitions or [],
        },
        reason,
    )


def pygments_tokens(
    source: str, language: str
) -> tuple[list[str], list[str], set[int]]:
    from pygments import lex
    from pygments.lexers.compiled import CppLexer
    from pygments.token import (
        Comment,
        Keyword,
        Name,
        Number,
        Operator,
        Punctuation,
        String,
        Text,
    )

    lexer = CppLexer()
    operators: list[str] = []
    operands: list[str] = []
    code_lines: set[int] = set()
    line = 1
    for token_type, value in lex(source, lexer):
        start = line
        line += value.count("\n")
        if token_type in Comment or token_type in Text or not value.strip():
            continue
        for offset, part in enumerate(value.splitlines() or [value]):
            if part.strip():
                code_lines.add(start + offset)
        if token_type in Keyword or token_type in Operator:
            operators.append(value)
        elif token_type in Name or token_type in Number or token_type in String:
            operands.append(value)
        elif token_type in Punctuation and value not in GROUPING_PUNCTUATION:
            operators.append(value)
    return operators, operands, code_lines


def cpp_parser() -> Any:
    import tree_sitter_cpp
    from tree_sitter import Language, Parser

    return Parser(Language(tree_sitter_cpp.language()))


def preprocess_cpp_for_control(source_text: str) -> str:
    """Expand source-defined macros without importing external header bodies."""
    without_includes = "".join(
        "\n" if line.lstrip().startswith("#include") else line
        for line in source_text.splitlines(keepends=True)
    )
    completed = subprocess.run(
        ["g++", "-E", "-P", "-x", "c++", "-std=gnu++23", "-"],
        input=without_includes,
        text=True,
        capture_output=True,
        timeout=15,
    )
    if completed.returncode != 0:
        raise ValueError("C++ preprocessing failed: " + completed.stderr.strip()[:300])
    return completed.stdout


def cpp_parse_errors(root: Any) -> list[Any]:
    errors: list[Any] = []

    def collect(node: Any) -> None:
        if node.type == "ERROR" or node.is_missing:
            errors.append(node)
        for child in node.children:
            collect(child)

    collect(root)
    return errors


def cpp_errors_do_not_affect_control(errors: list[Any], source: bytes) -> bool:
    """Accept Tree-sitter's known assignment-in-comma-expression recovery."""
    for error in errors:
        if error.is_missing or error.type != "ERROR":
            return False
        parent = error.parent
        if parent is None or parent.type != "comma_expression":
            return False
        fragment = node_text(error, source).strip()
        if not fragment.startswith("=") or any(
            token in fragment for token in ("&&", "||", "?")
        ):
            return False
    return bool(errors)


def node_text(node: Any, source: bytes) -> str:
    return source[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def measure_cpp_static(
    source_text: str,
) -> tuple[dict[str, int | float | str], list[str], list[str]]:
    control_text = preprocess_cpp_for_control(source_text)
    source = control_text.encode("utf-8")
    tree = cpp_parser().parse(source)
    limitations: list[str] = []
    failures: list[str] = []
    decisions = 0
    max_if = 0
    max_loop = 0
    decision_types = {
        "if_statement",
        "for_statement",
        "for_range_loop",
        "while_statement",
        "do_statement",
        "conditional_expression",
        "catch_clause",
    }
    loop_types = {"for_statement", "for_range_loop", "while_statement", "do_statement"}

    def walk(
        node: Any, if_depth: int, loop_depth: int, elif_node: bool = False
    ) -> None:
        nonlocal decisions, max_if, max_loop
        if node.type in decision_types:
            decisions += 1
        if node.type == "case_statement" and not node_text(
            node.child(0), source
        ).startswith("default"):
            decisions += 1
        if node.type == "binary_expression":
            operator = node.child_by_field_name("operator")
            if operator is not None and node_text(operator, source) in {"&&", "||"}:
                decisions += 1
        next_if = if_depth
        next_loop = loop_depth
        if node.type == "if_statement" and not elif_node:
            next_if += 1
            max_if = max(max_if, next_if)
        if node.type in loop_types:
            next_loop += 1
            max_loop = max(max_loop, next_loop)
        alternative = (
            node.child_by_field_name("alternative")
            if node.type == "if_statement"
            else None
        )
        for child in node.named_children:
            child_elif = alternative is child and child.type == "if_statement"
            walk(child, next_if, next_loop, child_elif)

    operators, operands, code_lines = pygments_tokens(source_text, "cpp")
    volume, vocabulary = halstead(operators, operands)
    parse_errors = cpp_parse_errors(tree.root_node)
    tolerable_recovery = cpp_errors_do_not_affect_control(parse_errors, source)
    if parse_errors and not tolerable_recovery:
        control_metrics: dict[str, int | str] = {"Omega_CC": NOT_MEASURED}
        failures.append("Tree-sitter C++ parse contains ERROR or missing nodes")
        limitations.append(
            "C++ control-flow axes NOT_MEASURED: the exact source did not parse cleanly"
        )
    else:
        walk(tree.root_node, 0, 0)
        control_metrics = {"Omega_CC": 1 + decisions}
        if tolerable_recovery:
            limitations.append(
                "Tree-sitter recovered only assignment tokens inside comma expressions; these do not contain control decisions"
            )
    limitations.append(
        "C++ control flow is parsed after g++ 13.3 macro expansion with external #include bodies excluded"
    )
    return control_metrics, limitations, failures


def explanation(metrics: dict[str, Any]) -> str:
    return (
        "The retained profile keeps source cyclomatic complexity separately "
        f"(Omega_CC={metrics['Omega_CC']}) from native execution length, peak "
        "reachable state size, and cumulative state load."
    )


def measure_task(
    root: Path,
    benchmark: Path,
    timeout: int,
    static_only: bool,
    repetitions: int,
    case: dict[str, Any] | None = None,
    shared_dynamic_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    identifier = root.relative_to(benchmark / "problems").as_posix()
    program_paths = list(root.glob("program.*"))
    if len(program_paths) != 1:
        raise ValueError(f"{identifier}: expected one program file")
    program = program_paths[0]
    source_bytes = program.read_bytes()
    source = source_bytes.decode("utf-8")
    input_path = root / "input.txt"
    oracle_path = root / "ground-output.txt"
    language_key = "python" if program.suffix == ".py" else "cpp"
    language = LANGUAGES[language_key][1]
    metric_methods = (
        PYTHON_METRIC_METHODS if language_key == "python" else CPP_METRIC_METHODS
    )
    limitations: list[str] = [
        "Language-native measurements are not directly comparable with IMP PLSemanticsBench values",
    ]
    failures: list[str] = []
    if program.suffix == ".py":
        static = measure_python_static(source)
    elif program.suffix == ".cpp":
        static, cpp_limits, cpp_failures = measure_cpp_static(source)
        limitations.extend(cpp_limits)
        failures.extend(cpp_failures)
    else:
        raise ValueError(f"unsupported language: {program.suffix}")
    metrics: dict[str, Any] = {
        "Omega_CC": static["Omega_CC"],
        "Omega_hat_NativeTrace": NOT_MEASURED,
        "Omega_hat_StateSize": NOT_MEASURED,
        "Omega_hat_StateLoad": NOT_MEASURED,
    }
    dynamic_execution: dict[str, Any] | None = None
    runtime_measurement: dict[str, Any] | None = None
    if not static_only and program.suffix == ".py":
        if case is None:
            raise ValueError(f"{identifier}: case metadata is required for dynamic measurement")
        target = resolve_dynamic_target(root, benchmark, case)
        if shared_dynamic_record is not None:
            shared_execution = shared_dynamic_record.get("dynamic_execution") or {}
            if shared_execution.get("execution_id") != target.execution_id:
                raise ValueError(f"{identifier}: shared dynamic execution identity mismatch")
            dynamic = {
                metric: int(shared_dynamic_record["metrics"][metric])
                for metric in DYNAMIC_METRICS
            }
            for metric in RUNTIME_METRICS:
                metrics[metric] = shared_dynamic_record["metrics"].get(
                    metric, NOT_MEASURED
                )
            runtime_measurement = shared_dynamic_record.get("runtime_measurement")
            error = None
        else:
            # The retained dynamic metric set is measured by the CPython
            # monitoring adapter below.  The old AST profiler produced only
            # removed metrics, so rerunning it here added a full execution
            # (and sometimes a timeout) whose result was discarded.
            dynamic = {}
            error = None
        dynamic_execution = {
            "execution_id": target.execution_id,
            "source_arm": target.source_arm,
            "source": (
                str(target.source_path.relative_to(benchmark))
                if target.source_path is not None
                else "GENERATED_POST_LOOP_CHECKPOINT"
            ),
            "source_sha256": sha256(target.source_bytes),
            "input_sha256": sha256(input_path.read_bytes()),
            "oracle": str(target.oracle_path.relative_to(benchmark)),
            "target_kind": target.target_kind,
            "runtime": f"CPython {platform.python_version()}",
            "instrumentation": PYTHON_DYNAMIC_INSTRUMENTATION,
            "status": "OK" if dynamic is not None else "NOT_MEASURED",
        }
        if dynamic is None:
            failures.append(error or "dynamic measurement failed")
        else:
            metrics.update(dynamic)
        if (
            shared_dynamic_record is None
            and target.source_arm
            in {
                "short-trace-final",
                "long-trace-final",
                "inside-loop-state",
                "post-loop-state",
            }
        ):
            artifact_root = (
                benchmark
                / "measurements"
                / "program-complexity"
                / "raw-state-observations"
                / target.source_arm
                / target.execution_id.removeprefix("sha256:")
            )
            source_label = (
                target.source_path.relative_to(benchmark).as_posix()
                if target.source_path is not None
                else "GENERATED_POST_LOOP_CHECKPOINT"
            )
            runtime_metrics, runtime_measurement, runtime_error = (
                measure_python_runtime_metrics(
                    target.source_path,
                    input_path,
                    target.oracle_path,
                    timeout,
                    artifact_root,
                    source_label,
                    source_bytes=(
                        target.source_bytes if target.source_path is None else None
                    ),
                    execution_cwd=target.cwd,
                    oracle_mode=(
                        "last-json-line"
                        if target.target_kind == "generated-post-loop-checkpoint"
                        else "exact"
                    ),
                    repetitions=repetitions,
                )
            )
            metrics.update(runtime_metrics)
            if runtime_error is not None:
                limitations.append(
                    "New CPython runtime metrics NOT_MEASURED: " + runtime_error
                )
                if runtime_error.startswith(
                    ("natural execution", "natural stdout")
                ):
                    dynamic_execution["status"] = NOT_MEASURED
            if runtime_measurement is not None:
                cwd_value = runtime_measurement.get("cwd")
                if isinstance(cwd_value, str):
                    runtime_measurement["cwd"] = Path(cwd_value).relative_to(
                        benchmark
                    ).as_posix()
                artifact_root_value = runtime_measurement.get("artifact_root")
                if isinstance(artifact_root_value, str):
                    runtime_measurement["artifact_root"] = Path(
                        artifact_root_value
                    ).relative_to(benchmark).as_posix()
                for repetition in runtime_measurement.get("repetitions", []):
                    raw_value = repetition.get("raw_artifact")
                    if isinstance(raw_value, str):
                        raw_path = Path(raw_value)
                        repetition["raw_artifact"] = raw_path.relative_to(
                            benchmark
                        ).as_posix()
    elif program.suffix == ".cpp":
        limitations.append(
            "C++ dynamic axes NOT_MEASURED: no semantics-preserving instrumenter configured"
        )
    record = {
        "schema_version": SCHEMA_VERSION,
        "program": identifier,
        "problem": "/".join(identifier.split("/")[:-1]),
        "arm": identifier.split("/")[-1],
        "language": language,
        "input": str(input_path.relative_to(benchmark)),
        "scope": "complete visible program, excluding natural-language prompt",
        "source_sha256": sha256(source_bytes),
        "input_sha256": sha256(input_path.read_bytes()),
        "metric_methods": metric_methods,
        "metrics": {name: metrics[name] for name in METRICS},
        "plain_english_profile": explanation(metrics),
        "method_notes": {
            "parser_cfg": "CPython 3.12 AST-derived extended cyclomatic complexity"
            if program.suffix == ".py"
            else "g++ 13.3 macro expansion (external includes excluded) plus Tree-sitter C++ 0.23.4 extended-decision CST convention",
            "execution": "Natural and CPython-monitoring execution under CPython 3.12 with exact input and target-specific oracle validation"
            if program.suffix == ".py" and not static_only
            else NOT_MEASURED,
            "limitations": limitations,
        },
        "dynamic_execution": dynamic_execution,
        "runtime_measurement": runtime_measurement,
        "failures": failures,
    }
    return record


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", dir=path.parent
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(content, encoding="utf-8")
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_jsonl(path: Path) -> dict[str, dict[str, Any]]:
    if not path.exists():
        return {}
    return {
        record["program"]: record
        for record in (
            json.loads(line)
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def select_programs(
    benchmark: Path,
    arm: str,
    language: str,
    case_limit: int | None,
    patterns: list[str],
) -> list[Path]:
    payload = json.loads((benchmark / "cases.json").read_text(encoding="utf-8"))
    cases = (
        payload["cases"][:case_limit] if case_limit is not None else payload["cases"]
    )
    roots = []
    case_language = "python" if language == "python" else "cpp20"
    suffix = LANGUAGES[language][0]
    for case in cases:
        if case["language"] != case_language:
            continue
        root = (
            benchmark
            / "problems"
            / case["platform"]
            / str(case["question_id"])
            / arm
        )
        identifier = root.relative_to(benchmark / "problems").as_posix()
        if patterns and not any(
            fnmatch.fnmatchcase(identifier, pattern) for pattern in patterns
        ):
            continue
        if not (root / f"program{suffix}").is_file():
            raise ValueError(f"{identifier}: expected program{suffix}")
        roots.append(root)
    return roots


def metric_can_reuse(
    record: dict[str, Any] | None,
    metric: str,
    source_hash: str,
    input_hash: str,
    metric_methods: dict[str, str],
    expected_execution_id: str | None = None,
    benchmark: Path | None = None,
) -> bool:
    if record is None:
        return False
    if record.get("source_sha256") != source_hash:
        return False
    if metric.startswith("Omega_hat_"):
        if record.get("input_sha256") != input_hash:
            return False
        if expected_execution_id is not None and record.get(
            "dynamic_execution", {}
        ).get("execution_id") != expected_execution_id:
            return False
    methods = record.get("metric_methods", {})
    if methods.get(metric) == metric_methods[metric]:
        value = record.get("metrics", {}).get(metric)
        if metric in RUNTIME_METRICS:
            return runtime_metric_can_reuse(record, metric, value, benchmark)
        if value != NOT_MEASURED:
            return metric in record.get("metrics", {})
        return metric_methods[metric].endswith("not-measured-v1")
    return False


def runtime_metric_can_reuse(
    record: dict[str, Any],
    metric: str,
    value: Any,
    benchmark: Path | None,
) -> bool:
    if benchmark is None:
        return False
    measurement = record.get("runtime_measurement") or {}
    repetitions = measurement.get("repetitions") or []
    if value == NOT_MEASURED and measurement.get("status") == NOT_MEASURED:
        if metric == "Omega_hat_NativeTrace":
            return False
        return bool(measurement.get("failure")) and not repetitions
    if measurement.get("runtime") != (
        f"{platform.python_implementation()} {platform.python_version()}"
    ):
        return False
    if len(repetitions) not in {1, 3}:
        return False
    raw_signatures = set()
    for repetition in repetitions:
        artifact_value = repetition.get("raw_artifact")
        if not isinstance(artifact_value, str):
            return False
        artifact = benchmark / artifact_value
        if not artifact.is_file() or sha256(artifact.read_bytes()) != repetition.get(
            "raw_artifact_sha256"
        ):
            return False
        raw_signatures.add(
            (
                repetition.get("raw_artifact_sha256"),
                repetition.get("raw_observation_rows"),
            )
        )
    if len(raw_signatures) != 1:
        return False
    repetition_values = [repetition.get(metric) for repetition in repetitions]
    if metric == "Omega_hat_NativeTrace":
        return value != NOT_MEASURED and repetition_values == [value] * len(repetitions)
    if value != NOT_MEASURED:
        return (
            repetition_values == [value] * len(repetitions)
            and all(repetition.get("state_failure") is None for repetition in repetitions)
        )
    failures = [repetition.get("state_failure") for repetition in repetitions]
    failure_type = (failures[0] or {}).get("type") if failures else None
    if isinstance(failure_type, str) and (
        failure_type.startswith("__main__.")
    ):
        return False
    return (
        measurement.get("status") == "PARTIAL"
        and failures[0] is not None
        and failures == [failures[0]] * len(repetitions)
    )


def shared_dynamic_metric_can_reuse(
    record: dict[str, Any] | None,
    metric: str,
    expected_execution_id: str | None,
    metric_methods: dict[str, str],
    benchmark: Path | None = None,
) -> bool:
    if record is None or expected_execution_id is None:
        return False
    if record.get("dynamic_execution", {}).get("execution_id") != expected_execution_id:
        return False
    if record.get("metric_methods", {}).get(metric) != metric_methods[metric]:
        return False
    value = record.get("metrics", {}).get(metric, NOT_MEASURED)
    if metric in RUNTIME_METRICS:
        return runtime_metric_can_reuse(record, metric, value, benchmark)
    return value != NOT_MEASURED


def failed_record(
    root: Path, benchmark: Path, language: str, exc: BaseException
) -> dict[str, Any]:
    identifier = root.relative_to(benchmark / "problems").as_posix()
    suffix, language_name = LANGUAGES[language]
    metric_methods = (
        PYTHON_METRIC_METHODS if language == "python" else CPP_METRIC_METHODS
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "program": identifier,
        "problem": "/".join(identifier.split("/")[:-1]),
        "arm": identifier.split("/")[-1],
        "language": language_name,
        "input": str((root / "input.txt").relative_to(benchmark)),
        "scope": "complete visible program, excluding natural-language prompt",
        "source_sha256": sha256((root / f"program{suffix}").read_bytes()),
        "input_sha256": sha256((root / "input.txt").read_bytes()),
        "metric_methods": metric_methods,
        "metric_provenance": {name: "failed" for name in METRICS},
        "metrics": {name: NOT_MEASURED for name in METRICS},
        "plain_english_profile": "Measurement failed; see failures.",
        "method_notes": {"limitations": ["Measurement failed"]},
        "failures": [f"{type(exc).__name__}: {exc}"],
    }


def package_versions() -> dict[str, str]:
    result = {"python": platform.python_version()}
    for distribution in (
        "numpy",
        "matplotlib",
        "Pygments",
        "tree-sitter",
        "tree-sitter-cpp",
    ):
        try:
            result[distribution] = metadata.version(distribution)
        except metadata.PackageNotFoundError:
            result[distribution] = NOT_MEASURED
    return result


def write_profiles_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fields = [
        "program",
        "problem",
        "arm",
        "language",
        "source_sha256",
        "input_sha256",
        "execution_id",
        *METRICS,
        "state_measurement_status",
        "Omega_hat_NativeTrace_relation",
        "Omega_hat_NativeTrace_reported",
        "Omega_hat_StateSize_relation",
        "Omega_hat_StateSize_reported",
        "Omega_hat_StateLoad_relation",
        "Omega_hat_StateLoad_reported",
    ]
    handle = io.StringIO(newline="")
    writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        state = record.get("state_measurement") or state_measurement_summary(record)
        writer.writerow(
            {
                **{key: record[key] for key in fields[:6]},
                "execution_id": (
                    record.get("dynamic_execution") or {}
                ).get("execution_id", ""),
                **record["metrics"],
                "state_measurement_status": state["status"],
                "Omega_hat_NativeTrace_relation": state[
                    "Omega_hat_NativeTrace"
                ]["relation"],
                "Omega_hat_NativeTrace_reported": state[
                    "Omega_hat_NativeTrace"
                ]["value"],
                "Omega_hat_StateSize_relation": state["Omega_hat_StateSize"][
                    "relation"
                ],
                "Omega_hat_StateSize_reported": state["Omega_hat_StateSize"][
                    "value"
                ],
                "Omega_hat_StateLoad_relation": state["Omega_hat_StateLoad"][
                    "relation"
                ],
                "Omega_hat_StateLoad_reported": state["Omega_hat_StateLoad"][
                    "value"
                ],
            }
        )
    atomic_write_text(path, handle.getvalue())


def state_measurement_summary(record: dict[str, Any]) -> dict[str, Any]:
    """Return the final exact-or-censored state values for one execution."""
    metrics = record.get("metrics") or {}
    exact = all(isinstance(metrics.get(metric), int) for metric in RUNTIME_METRICS)
    if exact:
        return {
            "status": "EXACT",
            **{
                metric: {"relation": "=", "value": int(metrics[metric])}
                for metric in RUNTIME_METRICS
            },
        }

    measurement_field = (
        "timeout_recovery_measurement"
        if record.get("timeout_recovery_measurement")
        else "runtime_measurement"
    )
    measurement = record.get(measurement_field) or {}
    partials = [
        repetition
        for repetition in measurement.get("repetitions") or []
        if repetition.get("partial") is True
        and isinstance(repetition.get("Omega_hat_NativeTraceLowerBound"), int)
        and isinstance(repetition.get("Omega_hat_StateSizeLowerBound"), int)
        and isinstance(repetition.get("Omega_hat_StateLoadLowerBound"), int)
    ]
    if partials:
        strongest = max(
            partials,
            key=lambda repetition: repetition["Omega_hat_StateLoadLowerBound"],
        )
        return {
            "status": "LOWER_BOUND_TIMEOUT",
            "basis": measurement.get("failure", "timed measurement stopped"),
            "completed_state_observations": strongest.get(
                "raw_observation_rows", 0
            ),
            "Omega_hat_NativeTrace": {
                "relation": ">=",
                "value": int(strongest["Omega_hat_NativeTraceLowerBound"]),
            },
            "Omega_hat_StateSize": {
                "relation": ">=",
                "value": int(strongest["Omega_hat_StateSizeLowerBound"]),
            },
            "Omega_hat_StateLoad": {
                "relation": ">=",
                "value": int(strongest["Omega_hat_StateLoadLowerBound"]),
            },
        }

    failure = str(measurement.get("failure") or "")
    status = (
        "INVALID_ORACLE_MISMATCH"
        if "stdout did not match ground-output.txt" in failure
        else "NOT_MEASURED"
    )
    return {
        "status": status,
        "basis": failure or "no complete or bounded state observation is available",
        **{
            metric: {"relation": "", "value": ""}
            for metric in RUNTIME_METRICS
        },
    }


def apply_state_measurement_summary(record: dict[str, Any]) -> None:
    summary = state_measurement_summary(record)
    record["state_measurement"] = summary
    if summary["status"] != "LOWER_BOUND_TIMEOUT":
        return
    measurement_field = (
        "timeout_recovery_measurement"
        if record.get("timeout_recovery_measurement")
        else "runtime_measurement"
    )
    measurement = record.get(measurement_field) or {}
    measurement.setdefault("adapter_version", PYTHON_RUNTIME_ADAPTER_VERSION)
    measurement.setdefault(
        "observation_convention", PYTHON_RUNTIME_OBSERVATION_CONVENTION
    )
    measurement.setdefault("state_counter", "c-iterative-flat-cache-v2")
    for repetition in measurement.get("repetitions") or []:
        repetition.setdefault("adapter_version", PYTHON_RUNTIME_ADAPTER_VERSION)
        repetition.setdefault(
            "observation_convention", PYTHON_RUNTIME_OBSERVATION_CONVENTION
        )
        repetition.setdefault("state_counter", "c-iterative-flat-cache-v2")
    record[measurement_field] = measurement


def normalize_runtime_paths(record: dict[str, Any], benchmark: Path) -> None:
    for measurement_field in (
        "runtime_measurement",
        "timeout_recovery_measurement",
    ):
        measurement = record.get(measurement_field) or {}
        for field in ("cwd", "artifact_root"):
            value = measurement.get(field)
            if isinstance(value, str) and Path(value).is_absolute():
                measurement[field] = Path(value).relative_to(benchmark).as_posix()
        for repetition in measurement.get("repetitions", []):
            value = repetition.get("raw_artifact")
            if isinstance(value, str) and Path(value).is_absolute():
                repetition["raw_artifact"] = Path(value).relative_to(
                    benchmark
                ).as_posix()


def checkpoint_profiles(
    profiles_path: Path,
    csv_path: Path,
    existing: dict[str, dict[str, Any]],
    benchmark: Path,
) -> None:
    """Persist every completed profile so an interrupted batch can resume."""
    records = [existing[key] for key in sorted(existing)]
    for record in records:
        apply_state_measurement_summary(record)
        normalize_runtime_paths(record, benchmark)
    atomic_write_text(
        profiles_path,
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
    )
    write_profiles_csv(csv_path, records)


def write_program_complexity_readme(path: Path, timeout: int) -> None:
    python_by_arm = {
        arm: list(
            load_jsonl(path.parent / arm / "python" / "profiles.jsonl").values()
        )
        for arm in ARMS
    }
    python_records = [
        record for records in python_by_arm.values() for record in records
    ]
    state_statuses = Counter(
        (record.get("state_measurement") or state_measurement_summary(record))[
            "status"
        ]
        for record in python_records
    )
    cpp_by_arm = {
        arm: list(load_jsonl(path.parent / arm / "cpp" / "profiles.jsonl").values())
        for arm in ARMS
    }
    cpp_records = [record for records in cpp_by_arm.values() for record in records]
    failures = sum(
        bool(record["failures"])
        for record in [*python_records, *cpp_records]
    )
    distribution_sections = []
    for metric in STATIC_METRICS:
        slug = metric.removeprefix("Omega_").lower().replace("_", "-")
        image = path.parent / "distributions" / f"omega-{slug}-distribution.png"
        if image.is_file():
            distribution_sections.append(
                f"### `{metric}`\n\n"
                f"![{metric} distribution](distributions/omega-{slug}-distribution.png)"
            )
    distributions = (
        "\n\n".join(distribution_sections)
        if distribution_sections
        else "Distribution figures have not been generated yet."
    )
    content = f"""# Program complexity measurements

This directory contains language-native PLSemanticsBench-style profiles for
`lcb_hard_v1_python`. Static profiles cover the actual source in all four arms for
both languages. Python and C++ remain separate because
their raw values use language-specific constructs and token conventions.

- Python profiles: {len(python_records)} ({len(ARMS)} arms × {len(python_by_arm['short-trace-final'])} programs)
- C++ profiles: {len(cpp_records)} ({len(ARMS)} arms × {len(cpp_by_arm['short-trace-final'])} programs)
- Profiles with measurement failures: {failures}
- Dynamic timeout when requested: {timeout} seconds
- Exact Python state profiles: {state_statuses['EXACT']}
- Python state lower bounds after timeout: {state_statuses['LOWER_BOUND_TIMEOUT']}
- Invalid Python oracle identities: {state_statuses['INVALID_ORACLE_MISMATCH']}
- Scope: complete visible program, excluding the natural-language prompt

Metric names, formulas, units, calculation, and interpretation are defined in
the [shared metric definitions](../../../../shared/metrics/README.md).

## Static metrics and coverage

The retained source metric remains separate from the three execution metrics;
no aggregate score or qualitative difficulty label is produced.

| Metric | Python | C++ |
| --- | --- | --- |
| `Omega_CC` | CPython AST-derived control flow | preprocessed Tree-sitter control flow |

No Python and C++ values are pooled because their control-flow adapters use
language-specific conventions.

Python profiles contain `Omega_hat_NativeTrace`, `Omega_hat_StateSize`, and
`Omega_hat_StateLoad`. Each profile records its dynamic execution identity and
oracle. StateSize is the peak of the complete state-observation series, while
StateLoad is its sum. When an execution reaches the declared timeout, the
authoritative profile keeps the exact metric as `NOT_MEASURED` and separately
records the completed prefix as `>=` lower bounds with status
`LOWER_BOUND_TIMEOUT`; these values must not be interpreted as exact totals.

<!-- dataset-complexity-summary:start -->
## Dataset median summary

Run the dataset summary command below to populate this section.
<!-- dataset-complexity-summary:end -->

## Static distributions

Each histogram covers all numeric profiles for one language. The vertical lines
show the median and quartiles; the rug shows individual programs. Panels use
independent x-axes and must not be read as cross-language equivalence.

Machine-readable statistics are in `distributions/summary.csv`; plotting and
transformation conventions are in `distributions/analysis-config.json`.

{distributions}

## Schema and updates

Authoritative profiles live in `<arm>/<language>/profiles.jsonl` for each of
the four arms; adjacent CSV files are flat analysis views.
Each manifest records hashes, method versions, exact problem IDs and per-metric
reuse/recomputation counts. Problem ID is the primary key, and writes are atomic
and deterministically sorted.

Each adjacent `failures.jsonl` contains only parsing or measurement failures. Expected
`NOT_MEASURED` values are not failures. Language-native values are not directly
comparable with the paper's IMP values unless constructs and counting conventions
are compatible.

## Reproduce

```bash
for arm in short-trace-final long-trace-final inside-loop-state post-loop-state; do
  uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_python/analysis/requirements.txt python -m experiments.lcb_hard_v1_python.analysis.program_complexity run --benchmark experiments/lcb_hard_v1_python --arm "$arm" --language python --workers 8 --execution-timeout 120
done
for arm in short-trace-final long-trace-final inside-loop-state post-loop-state; do
  uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_python/analysis/requirements.txt python -m experiments.lcb_hard_v1_python.analysis.program_complexity run --benchmark experiments/lcb_hard_v1_python --arm "$arm" --language cpp --static-only --workers 8
done
uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_python/analysis/requirements.txt python -m experiments.lcb_hard_v1_python.analysis.complexity_distributions --program-root experiments/lcb_hard_v1_python/measurements/program-complexity --benchmark-name lcb_hard_v1_python --arm short-trace-final
uv run --python 3.12.11 python -m experiments.lcb_hard_v1_python.analysis.normalize_complexity_profiles --benchmark experiments/lcb_hard_v1_python
python3 shared/metrics/scripts/summarize_dataset.py --config experiments/lcb_hard_v1_python/measurements/program-complexity/dataset-summary-config.json --output experiments/lcb_hard_v1_python/measurements/program-complexity --readme experiments/lcb_hard_v1_python/measurements/program-complexity/README.md
```
"""
    atomic_write_text(path, content)


def batch(arguments: argparse.Namespace) -> int:
    benchmark = arguments.benchmark.resolve()
    output = (
        arguments.output.resolve()
        if arguments.output is not None
        else benchmark
        / "measurements"
        / "program-complexity"
        / arguments.arm
        / arguments.language
    )
    roots = select_programs(
        benchmark,
        arguments.arm,
        arguments.language,
        arguments.case_limit,
        arguments.problem,
    )
    suffix = LANGUAGES[arguments.language][0]
    metric_methods = (
        PYTHON_METRIC_METHODS if arguments.language == "python" else CPP_METRIC_METHODS
    )
    case_payload = json.loads((benchmark / "cases.json").read_text(encoding="utf-8"))
    cases = {
        f"{case['platform']}/{case['question_id']}": case
        for case in case_payload["cases"]
    }
    profiles_path = output / "profiles.jsonl"
    existing = {} if arguments.overwrite else load_jsonl(profiles_path)
    legacy = (
        {} if arguments.overwrite else load_jsonl(arguments.legacy_profiles.resolve())
    )
    shared_dynamic_profiles: dict[str, dict[str, Any]] = {}
    selected: dict[
        str,
        tuple[
            Path,
            dict[str, Any] | None,
            dict[str, str],
            dict[str, Any],
            dict[str, Any] | None,
        ],
    ] = {}
    for root in roots:
        identifier = root.relative_to(benchmark / "problems").as_posix()
        problem_id = "/".join(identifier.split("/")[:-1])
        case = cases[problem_id]
        source_hash = sha256((root / f"program{suffix}").read_bytes())
        input_hash = sha256((root / "input.txt").read_bytes())
        expected_execution_id = None
        if not arguments.static_only and arguments.language == "python":
            expected_execution_id = resolve_dynamic_target(
                root, benchmark, case
            ).execution_id
        candidate = existing.get(identifier) or legacy.get(identifier)
        shared_dynamic_record = shared_dynamic_profiles.get(problem_id)
        reusable = {}
        for metric in METRICS:
            can_reuse = metric_can_reuse(
                candidate,
                metric,
                source_hash,
                input_hash,
                metric_methods,
                expected_execution_id,
                benchmark,
            )
            if (
                arguments.recover_missing_runtime
                and metric in {"Omega_hat_StateSize", "Omega_hat_StateLoad"}
                and candidate is not None
                and candidate.get("metrics", {}).get(metric) == NOT_MEASURED
            ):
                can_reuse = False
            can_reuse_shared = metric in ALL_DYNAMIC_METRICS and shared_dynamic_metric_can_reuse(
                shared_dynamic_record,
                metric,
                expected_execution_id,
                metric_methods,
                benchmark,
            )
            if can_reuse:
                reusable[metric] = "reused"
            elif can_reuse_shared:
                reusable[metric] = "reused_execution"
            elif metric_methods[metric].endswith("not-measured-v1"):
                reusable[metric] = "not_measured"
            elif arguments.static_only and metric in ALL_DYNAMIC_METRICS:
                reusable[metric] = "not_requested"
            else:
                reusable[metric] = "recomputed"
        if (
            all(
                value in {"reused", "not_measured", "not_requested"}
                for value in reusable.values()
            )
            and candidate
        ):
            record = dict(candidate)
            record["metric_provenance"] = reusable
            existing[identifier] = record
        else:
            selected[identifier] = (
                root,
                candidate,
                reusable,
                case,
                shared_dynamic_record
                if any(value == "reused_execution" for value in reusable.values())
                else None,
            )

    with ThreadPoolExecutor(max_workers=arguments.workers) as executor:
        futures = {
            executor.submit(
                measure_task,
                root,
                benchmark,
                arguments.execution_timeout,
                arguments.static_only,
                arguments.repetitions,
                case,
                shared_dynamic_record,
            ): (identifier, root, candidate, reusable)
            for identifier, (
                root,
                candidate,
                reusable,
                case,
                shared_dynamic_record,
            ) in selected.items()
        }
        for index, future in enumerate(as_completed(futures), 1):
            identifier, root, candidate, reusable = futures[future]
            try:
                record = future.result()
                for metric, provenance in reusable.items():
                    if provenance == "reused" and candidate is not None:
                        record["metrics"][metric] = candidate["metrics"][metric]
                record["metric_provenance"] = {
                    metric: (
                        candidate.get("metric_provenance", {}).get(metric, "reused")
                        if provenance == "reused" and candidate is not None
                        else "failed"
                        if provenance == "recomputed"
                        and record["metrics"][metric] == NOT_MEASURED
                        else provenance
                    )
                    for metric, provenance in reusable.items()
                }
            except BaseException as exc:
                record = failed_record(root, benchmark, arguments.language, exc)
            existing[identifier] = record
            checkpoint_profiles(
                profiles_path,
                output / "profiles.csv",
                existing,
                benchmark,
            )
            print(
                f"MEASURED {index}/{len(selected)} {identifier}",
                flush=True,
            )

    selected_ids = {
        root.relative_to(benchmark / "problems").as_posix() for root in roots
    }
    authoritative_ids = set(existing) if arguments.problem else selected_ids
    records = [existing[key] for key in sorted(authoritative_ids)]
    for record in records:
        normalize_runtime_paths(record, benchmark)
    selected_records = [existing[key] for key in sorted(selected_ids)]
    provenance_counts = {
        metric: {
            "reused": sum(
                record.get("metric_provenance", {}).get(metric) == "reused"
                for record in selected_records
            ),
            "reused_execution": sum(
                record.get("metric_provenance", {}).get(metric)
                == "reused_execution"
                for record in selected_records
            ),
            "recomputed": sum(
                record.get("metric_provenance", {}).get(metric) == "recomputed"
                for record in selected_records
            ),
            "failed": sum(
                record.get("metric_provenance", {}).get(metric) == "failed"
                for record in selected_records
            ),
            "not_requested": sum(
                record.get("metric_provenance", {}).get(metric) == "not_requested"
                for record in selected_records
            ),
            "not_measured": sum(
                record.get("metric_provenance", {}).get(metric) == "not_measured"
                for record in selected_records
            ),
        }
        for metric in METRICS
    }
    profile_payload = "".join(
        json.dumps(record, sort_keys=True) + "\n" for record in records
    )
    atomic_write_text(profiles_path, profile_payload)
    write_profiles_csv(output / "profiles.csv", records)
    failures = [record for record in records if record["failures"]]
    atomic_write_text(
        output / "failures.jsonl",
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in failures),
    )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "benchmark": benchmark.name,
        "arm": arguments.arm,
        "language": arguments.language,
        "measurement_mode": "static_only" if arguments.static_only else "full",
        "profile_count": len(records),
        "selected_case_limit": arguments.case_limit,
        "selected_profile_count": len(selected_records),
        "selected_problem_ids": [record["problem"] for record in selected_records],
        "metric_methods": metric_methods,
        "metric_provenance": provenance_counts,
        "execution_timeout_seconds": arguments.execution_timeout,
        "runtime_repetitions": arguments.repetitions,
        "runtime_versions": package_versions(),
        "profiles": [
            {
                "problem": record["problem"],
                "program": record["program"],
                "source_sha256": record["source_sha256"],
                "input_sha256": record["input_sha256"],
                "dynamic_execution_id": (
                    record.get("dynamic_execution") or {}
                ).get("execution_id"),
            }
            for record in records
        ],
    }
    atomic_write_text(
        output / "manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
    )
    print(
        f"COMPLETE profiles={len(records)} selected={len(selected_records)} "
        f"failures={len(failures)} output={output}"
    )
    return 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    subparsers = result.add_subparsers(dest="command", required=True)
    runner = subparsers.add_parser("run")
    runner.add_argument(
        "--benchmark", type=Path, default=ROOT / "experiments/lcb_hard_v1_python"
    )
    runner.add_argument("--output", type=Path)
    runner.add_argument(
        "--legacy-profiles",
        type=Path,
        default=ROOT
        / "experiments"
        / "lcb_hard_v1_python"
        / "measurements"
        / "program-complexity"
        / "profiles.jsonl",
    )
    runner.add_argument("--problem", action="append", default=[])
    runner.add_argument("--case-limit", type=int)
    runner.add_argument("--arm", choices=ARMS, default="short-trace-final")
    runner.add_argument("--language", choices=list(LANGUAGES), default="python")
    runner.add_argument("--static-only", action="store_true")
    runner.add_argument("--workers", type=int, default=1)
    runner.add_argument("--execution-timeout", type=int, default=30)
    runner.add_argument("--repetitions", type=int, default=1)
    runner.add_argument("--overwrite", action="store_true")
    runner.add_argument(
        "--recover-missing-runtime",
        action="store_true",
        help="rerun only profiles whose StateSize or StateLoad is NOT_MEASURED",
    )
    internal = subparsers.add_parser("_run-python")
    internal.add_argument("source", type=Path)
    internal.add_argument("metrics", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    if arguments.command == "_run-python":
        return run_instrumented_python(arguments.source, arguments.metrics)
    if (
        arguments.workers < 1
        or arguments.execution_timeout < 1
        or arguments.repetitions < 1
    ):
        raise SystemExit("workers, execution-timeout, and repetitions must be positive")
    if arguments.case_limit is not None and arguments.case_limit < 1:
        raise SystemExit("case-limit must be positive")
    return batch(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
