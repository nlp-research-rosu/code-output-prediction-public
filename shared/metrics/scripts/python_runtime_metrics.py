#!/usr/bin/env python3
"""Measure CPython-native trace length and peak program state."""

from __future__ import annotations

import argparse
import ast
import collections
import csv
import dis
import gzip
import hashlib
import importlib.util
import io
import json
import os
import shlex
import subprocess
import sys
import sysconfig
import tempfile
import time
import types
from dataclasses import dataclass
from collections.abc import Iterator
from pathlib import Path
from typing import Any

ADAPTER_VERSION = "python-cpython-monitoring-state-v7"
OBSERVATION_CONVENTION = "initial-next-opcode-mutation-boundary-return-v1"
MAX_STATE_CELL_VISITS = int(
    os.environ.get("PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT", "2000000")
)
FIELDS = (
    "event_index",
    "event_kind",
    "source_location",
    "state_count",
    "state_size",
)
MUTATION_OPCODES = {
    "CALL",
    "CALL_FUNCTION_EX",
    "DELETE_ATTR",
    "DELETE_DEREF",
    "DELETE_FAST",
    "DELETE_GLOBAL",
    "DELETE_NAME",
    "DELETE_SUBSCR",
    "IMPORT_FROM",
    "IMPORT_NAME",
    "LIST_APPEND",
    "LIST_EXTEND",
    "MAP_ADD",
    "SET_ADD",
    "SET_UPDATE",
    "STORE_ATTR",
    "STORE_DEREF",
    "STORE_FAST",
    "STORE_GLOBAL",
    "STORE_NAME",
    "STORE_SLICE",
    "STORE_SUBSCR",
}
SCALAR_BINDING_MUTATIONS = {
    "STORE_DEREF",
    "STORE_FAST",
    "STORE_GLOBAL",
    "STORE_NAME",
}
DIRECT_DICT_MUTATIONS = {"DELETE_SUBSCR", "MAP_ADD", "STORE_SUBSCR"}
EXCLUDED_VALUE_TYPES = (
    types.BuiltinFunctionType,
    types.BuiltinMethodType,
    types.FunctionType,
    types.MethodType,
    types.ModuleType,
    type,
)
SCALAR_TYPES = (type(None), bool, int, float, complex)
UNSUPPORTED_ITERATOR_TYPES = (
    type(iter([])),
    type(iter(())),
    type(iter(range(1))),
    type(iter({})),
    type(iter(set())),
    type(iter("")),
    type(iter(b"")),
    type(iter(bytearray())),
    type(iter(frozenset())),
    type(iter(collections.deque())),
    type(reversed([])),
    enumerate,
    filter,
    map,
    reversed,
    zip,
)
CONTAINER_TYPES = (str, bytes, bytearray, list, tuple, set, frozenset, dict)


class StateMeasurementError(Exception):
    type_name: str


class UnsupportedStateValue(StateMeasurementError):
    def __init__(self, value: Any) -> None:
        value_type = type(value)
        self.type_name = f"{value_type.__module__}.{value_type.__qualname__}"
        super().__init__(f"unsupported reachable value type: {self.type_name}")


class StateTraversalLimit(StateMeasurementError):
    type_name = "STATE_TRAVERSAL_WORK_LIMIT"

    def __init__(self) -> None:
        super().__init__(
            f"exact state traversal exceeded {MAX_STATE_CELL_VISITS} semantic-cell visits"
        )


def load_c_state_module() -> Any | None:
    if os.environ.get("PROGRAM_COMPLEXITY_STATE_COUNTER") == "python":
        return None
    source = Path(__file__).with_name("python_state_cells.c")
    suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    identity = "\0".join(
        (
            hashlib.sha256(source.read_bytes()).hexdigest(),
            sys.implementation.cache_tag or "python",
            sysconfig.get_platform(),
        )
    )
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]
    build = Path(tempfile.gettempdir()) / "program-complexity-python-state-counter"
    build.mkdir(parents=True, exist_ok=True)
    library = build / f"_program_state_cells-{digest}{suffix}"
    if not library.is_file():
        descriptor, temporary_name = tempfile.mkstemp(
            prefix="._program_state_cells-", suffix=suffix, dir=build
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            command = [
                *shlex.split(str(sysconfig.get_config_var("LDSHARED"))),
                *shlex.split(str(sysconfig.get_config_var("CCSHARED") or "-fPIC")),
                "-O3",
                f"-I{sysconfig.get_paths()['include']}",
                str(source),
                "-o",
                str(temporary),
            ]
            completed = subprocess.run(command, text=True, capture_output=True)
            if completed.returncode != 0:
                if os.environ.get("PROGRAM_COMPLEXITY_STATE_COUNTER") == "c":
                    raise RuntimeError(
                        "could not compile exact C state walker: "
                        + completed.stderr.strip()
                    )
                return None
            os.replace(temporary, library)
        finally:
            temporary.unlink(missing_ok=True)
    spec = importlib.util.spec_from_file_location("_program_state_cells", library)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load exact C state walker from {library}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


C_STATE_MODULE = load_c_state_module()
C_STATE_COUNTER = C_STATE_MODULE.count if C_STATE_MODULE is not None else None


@dataclass(frozen=True)
class ScopeNames:
    module: frozenset[str]
    functions: dict[tuple[str, int], frozenset[str]]
    excluded: frozenset[str]


class BindingCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.module: set[str] = set()
        self.functions: dict[tuple[str, int], set[str]] = {}
        self.excluded: set[str] = set()
        self.current: set[str] = self.module

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname or alias.name.split(".", 1)[0]
            self.current.add(name)
            self.excluded.add(name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            name = alias.asname or alias.name
            self.current.add(name)
            self.excluded.add(name)

    def _visit_function(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
    ) -> None:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            self.current.add(node.name)
            self.excluded.add(node.name)
            function_name = node.name
        else:
            function_name = "<lambda>"
        names: set[str] = set()
        arguments = [
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        ]
        names.update(argument.arg for argument in arguments)
        if node.args.vararg is not None:
            names.add(node.args.vararg.arg)
        if node.args.kwarg is not None:
            names.add(node.args.kwarg.arg)
        previous = self.current
        self.current = names
        if isinstance(node, ast.Lambda):
            self.visit(node.body)
        else:
            for statement in node.body:
                self.visit(statement)
        self.current = previous
        self.functions[(function_name, node.lineno)] = names

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function
    visit_Lambda = _visit_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.current.add(node.name)
        self.excluded.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.current.add(node.id)


def discover_scope_names(source: str, filename: str) -> ScopeNames:
    collector = BindingCollector()
    collector.visit(ast.parse(source, filename=filename))
    return ScopeNames(
        module=frozenset(collector.module),
        functions={key: frozenset(value) for key, value in collector.functions.items()},
        excluded=frozenset(collector.excluded),
    )


def semantic_size(value: Any, seen: set[int], work: list[int] | None = None) -> int:
    if work is not None:
        work[0] += 1
        if work[0] > MAX_STATE_CELL_VISITS:
            raise StateTraversalLimit
    value_type = type(value)
    if value_type in SCALAR_TYPES:
        return 1
    if isinstance(value, EXCLUDED_VALUE_TYPES):
        return 0
    if value_type in UNSUPPORTED_ITERATOR_TYPES or isinstance(value, Iterator):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1
    if isinstance(value, str):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + str.__len__(value)
    if isinstance(value, bytes):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + bytes.__len__(value)
    if isinstance(value, bytearray):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + bytearray.__len__(value)
    if isinstance(value, range):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + len(value)
    if isinstance(value, list):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(item, seen, work) for item in list.__iter__(value)
        )
    if isinstance(value, tuple):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(item, seen, work) for item in tuple.__iter__(value)
        )
    if isinstance(value, set):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(item, seen, work) for item in set.__iter__(value)
        )
    if isinstance(value, frozenset):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(item, seen, work) for item in frozenset.__iter__(value)
        )
    if isinstance(value, dict):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(key, seen, work) + semantic_size(item, seen, work)
            for key, item in dict.items(value)
        )
    if isinstance(value, collections.deque):
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1 + sum(
            semantic_size(item, seen, work)
            for item in collections.deque.__iter__(value)
        )
    if value_type.__module__ != "__main__":
        identity = id(value)
        if identity in seen:
            return 0
        seen.add(identity)
        return 1
    try:
        fields = object.__getattribute__(value, "__dict__")
    except (AttributeError, TypeError):
        fields = safe_slot_fields(value)
    if type(fields) is not dict:
        raise UnsupportedStateValue(value)
    identity = id(value)
    if identity in seen:
        return 0
    seen.add(identity)
    return 1 + sum(semantic_size(item, seen, work) for item in fields.values())


def safe_slot_fields(value: Any) -> dict[str, Any]:
    value_type = type(value)
    result = {}
    for owner in type.__getattribute__(value_type, "__mro__"):
        namespace = type.__getattribute__(owner, "__dict__")
        slots = namespace.get("__slots__")
        if slots is None:
            continue
        if isinstance(slots, str):
            names = (slots,)
        elif type(slots) in (tuple, list) and all(
            isinstance(name, str) for name in slots
        ):
            names = tuple(slots)
        else:
            raise UnsupportedStateValue(value)
        for name in names:
            if name in {"__dict__", "__weakref__"}:
                continue
            descriptor = namespace.get(name)
            if not isinstance(descriptor, types.MemberDescriptorType):
                raise UnsupportedStateValue(value)
            try:
                result[name] = object.__getattribute__(value, name)
            except AttributeError:
                pass
    if not result and not any(
        "__slots__" in type.__getattribute__(owner, "__dict__")
        for owner in type.__getattribute__(value_type, "__mro__")
    ):
        raise UnsupportedStateValue(value)
    return result


class RuntimeTracer:
    def __init__(
        self,
        source_path: Path,
        source_label: str,
        scopes: ScopeNames,
        output: Path,
        progress_path: Path,
    ) -> None:
        self.source_path = source_path.resolve()
        self.source_label = source_label
        self.scopes = scopes
        self.output = output
        self.progress_path = progress_path
        self.native_trace = 0
        self.event_index = 0
        self.max_state_count = 0
        self.max_state_size = 0
        self.total_state_size = 0
        self.max_state_count_event = 0
        self.max_state_size_event = 0
        self.state_error: dict[str, Any] | None = None
        self.state_cell_visits = [0]
        self._pending_mutation: dict[int, str | None] = {}
        self._opnames: dict[types.CodeType, dict[int, str]] = {}
        self._last_root_shape: tuple[tuple[str, str, int, type[Any]], ...] | None = None
        self._last_state_size: int | None = None
        self._last_observation_work: int | None = None
        self._dict_mutation_snapshot = self.dict_mutation_state()
        self._rows = io.StringIO(newline="")
        self._last_progress_write = 0.0
        self._writer = csv.DictWriter(
            self._rows, fieldnames=FIELDS, lineterminator="\n"
        )
        self._writer.writeheader()
        self.checkpoint_progress(force=True)

    def included(self, frame: types.FrameType) -> bool:
        return Path(frame.f_code.co_filename).resolve() == self.source_path

    def frame_names(self, frame: types.FrameType) -> frozenset[str]:
        if frame.f_code.co_name == "<module>":
            return self.scopes.module
        return self.scopes.functions.get(
            (frame.f_code.co_name, frame.f_code.co_firstlineno),
            frozenset(frame.f_code.co_varnames),
        )

    def roots(self, frame: types.FrameType) -> list[tuple[str, Any]]:
        frames: list[types.FrameType] = []
        cursor: types.FrameType | None = frame
        while cursor is not None:
            if self.included(cursor):
                frames.append(cursor)
            cursor = cursor.f_back
        roots: list[tuple[str, Any]] = []
        module_frame = next(
            (candidate for candidate in reversed(frames) if candidate.f_code.co_name == "<module>"),
            None,
        )
        if module_frame is not None:
            roots.extend(self.selected_values(module_frame, self.scopes.module))
        for active in reversed(frames):
            if active is module_frame:
                continue
            roots.extend(self.selected_values(active, self.frame_names(active)))
        return roots

    def selected_values(
        self, frame: types.FrameType, names: frozenset[str]
    ) -> list[tuple[str, Any]]:
        result = []
        for name in sorted(names):
            if (
                name.startswith("_lcb_")
                or name.startswith(".")
                or name in self.scopes.excluded
                or name not in frame.f_locals
            ):
                continue
            value = frame.f_locals[name]
            if isinstance(value, EXCLUDED_VALUE_TYPES):
                continue
            result.append((name, value))
        return result

    def location(self, frame: types.FrameType) -> str:
        return f"{self.source_label}:{frame.f_lineno}"

    def observe(
        self,
        frame: types.FrameType,
        event_kind: str,
        pending_opname: str | None = None,
    ) -> None:
        if self.state_error is not None:
            return
        try:
            roots = self.roots(frame)
            state_count = len(roots)
            values = [value for _, value in roots]
            state_size = self.incremental_state(
                roots, pending_opname, event_kind
            )
            if state_size is None:
                state_size = self.measure_state(values)
            self.remember_state(roots, state_size)
        except StateMeasurementError as exc:
            self.state_error = {
                "event_index": self.event_index,
                "event_kind": event_kind,
                "source_location": self.location(frame),
                "type": exc.type_name,
                "reason": str(exc),
            }
            self.checkpoint_progress(force=True)
            return
        except RecursionError:
            self.state_error = {
                "event_index": self.event_index,
                "event_kind": event_kind,
                "source_location": self.location(frame),
                "type": "STATE_TRAVERSAL_RECURSION_LIMIT",
                "reason": "exact state traversal exceeded the CPython recursion limit",
            }
            return
        self._writer.writerow(
            {
                "event_index": self.event_index,
                "event_kind": event_kind,
                "source_location": self.location(frame),
                "state_count": state_count,
                "state_size": state_size,
            }
        )
        self.total_state_size += state_size
        if state_count > self.max_state_count:
            self.max_state_count = state_count
            self.max_state_count_event = self.event_index
        if state_size > self.max_state_size:
            self.max_state_size = state_size
            self.max_state_size_event = self.event_index
        self.event_index += 1
        self.checkpoint_progress()

    def checkpoint_progress(self, *, force: bool = False) -> None:
        now = time.monotonic()
        if not force and now - self._last_progress_write < 1.0:
            return
        self._last_progress_write = now
        payload = {
            "status": "running",
            "adapter_version": ADAPTER_VERSION,
            "state_counter": (
                "c-iterative-flat-cache-v2"
                if C_STATE_COUNTER
                else "python-reference-v1"
            ),
            "observation_convention": OBSERVATION_CONVENTION,
            "Omega_hat_NativeTraceLowerBound": self.native_trace,
            "Omega_hat_StateSizeLowerBound": self.max_state_size,
            "Omega_hat_StateLoadLowerBound": self.total_state_size,
            "state_cell_visits": self.state_cell_visits[0],
            "raw_observation_rows": self.event_index,
            "state_failure": self.state_error,
            "state_cell_visit_limit": MAX_STATE_CELL_VISITS,
        }
        self.progress_path.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.progress_path.name}.", dir=self.progress_path.parent
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            temporary.write_text(
                json.dumps(payload, sort_keys=True), encoding="utf-8"
            )
            os.replace(temporary, self.progress_path)
        finally:
            temporary.unlink(missing_ok=True)

    def dict_mutation_state(self) -> tuple[int, int, int]:
        if C_STATE_MODULE is None:
            return (0, 0, 0)
        generation, inexact_generation, scalar_delta = (
            C_STATE_MODULE.dict_mutation_state()
        )
        return int(generation), int(inexact_generation), int(scalar_delta)

    @staticmethod
    def root_shape(
        roots: list[tuple[str, Any]],
    ) -> tuple[tuple[str, str, int, type[Any]], ...]:
        return tuple(
            (
                name,
                "scalar" if type(value) in SCALAR_TYPES else "object",
                0 if type(value) in SCALAR_TYPES else id(value),
                type(value),
            )
            for name, value in roots
        )

    def remember_state(
        self, roots: list[tuple[str, Any]], state_size: int
    ) -> None:
        self._last_root_shape = self.root_shape(roots)
        self._last_state_size = state_size
        self._dict_mutation_snapshot = self.dict_mutation_state()

    def incremental_state(
        self,
        roots: list[tuple[str, Any]],
        pending_opname: str | None,
        event_kind: str,
    ) -> int | None:
        if (
            C_STATE_MODULE is None
            or self._last_root_shape is None
            or self._last_state_size is None
            or self._last_observation_work is None
            or event_kind not in {"mutation_boundary", "return"}
        ):
            return None
        if self.root_shape(roots) != self._last_root_shape:
            return None
        generation, inexact_generation, scalar_delta = self.dict_mutation_state()
        old_generation, _, old_scalar_delta = self._dict_mutation_snapshot
        if inexact_generation > old_generation:
            return None
        event_count = generation - old_generation
        if pending_opname in DIRECT_DICT_MUTATIONS:
            if event_count <= 0:
                return None
        elif pending_opname in SCALAR_BINDING_MUTATIONS or pending_opname is None:
            if event_count != 0:
                return None
        else:
            return None
        delta = scalar_delta - old_scalar_delta
        state_size = self._last_state_size + delta
        observation_work = self._last_observation_work + delta
        if state_size < 0 or observation_work < 0:
            return None
        if self.state_cell_visits[0] + observation_work > MAX_STATE_CELL_VISITS:
            self.state_cell_visits[0] = MAX_STATE_CELL_VISITS + 1
            raise StateTraversalLimit
        self.state_cell_visits[0] += observation_work
        self._last_observation_work = observation_work
        return state_size

    def measure_state(self, values: list[Any]) -> int:
        starting_work = self.state_cell_visits[0]
        if C_STATE_COUNTER is not None:
            status, state_size, updated_work = C_STATE_COUNTER(
                values, starting_work, MAX_STATE_CELL_VISITS
            )
            if status == 0:
                self.state_cell_visits[0] = int(updated_work)
                self._last_observation_work = int(updated_work) - starting_work
                return int(state_size)
            if status == 2:
                self.state_cell_visits[0] = int(updated_work)
                raise StateTraversalLimit
            if status != 1:
                raise RuntimeError(f"unknown C state walker status: {status}")
        seen: set[int] = set()
        state_size = sum(
            semantic_size(value, seen, self.state_cell_visits) for value in values
        )
        self._last_observation_work = self.state_cell_visits[0] - starting_work
        return state_size

    def instruction(self, code: types.CodeType, offset: int) -> None:
        frame = sys._getframe(1)
        identity = id(frame)
        if identity not in self._pending_mutation:
            self._pending_mutation[identity] = None
            self.observe(frame, "initial")
        self.native_trace += 1
        pending_opname = self._pending_mutation[identity]
        if pending_opname is not None:
            self.observe(frame, "mutation_boundary", pending_opname)
        opname = self._opnames[code][offset]
        self._pending_mutation[identity] = (
            opname if opname in MUTATION_OPCODES else None
        )
        if opname in {"RETURN_VALUE", "RETURN_CONST"}:
            self.observe(frame, "return")
            self._pending_mutation.pop(identity, None)

    def unwind(self, code: types.CodeType, offset: int, exception: BaseException) -> None:
        if code not in self._opnames:
            return
        frame = sys._getframe(1)
        identity = id(frame)
        if identity in self._pending_mutation:
            self.observe(
                frame, "unwind", self._pending_mutation.get(identity)
            )
            self._pending_mutation.pop(identity, None)

    def register(self, code: types.CodeType) -> list[types.CodeType]:
        codes = []
        pending = [code]
        while pending:
            current = pending.pop()
            codes.append(current)
            self._opnames[current] = {
                instruction.offset: instruction.opname
                for instruction in dis.get_instructions(current)
            }
            pending.extend(
                value for value in current.co_consts if isinstance(value, types.CodeType)
            )
        return codes

    def write(self) -> tuple[str, int]:
        content = self._rows.getvalue().encode("utf-8")
        self.output.parent.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{self.output.name}.", dir=self.output.parent
        )
        os.close(descriptor)
        temporary = Path(temporary_name)
        try:
            with temporary.open("wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as zipped:
                    zipped.write(content)
            os.replace(temporary, self.output)
        finally:
            temporary.unlink(missing_ok=True)
        return hashlib.sha256(self.output.read_bytes()).hexdigest(), self.event_index


def run(source_path: Path, source_label: str, output: Path, result_path: Path) -> int:
    source = source_path.read_text(encoding="utf-8")
    scopes = discover_scope_names(source, str(source_path))
    tracer = RuntimeTracer(source_path, source_label, scopes, output, result_path)
    globals_dict: dict[str, Any] = {
        "__name__": "__main__",
        "__file__": str(source_path),
        "__package__": None,
    }
    code = compile(source, str(source_path), "exec")
    status = "ok"
    error = None
    tool = sys.monitoring.PROFILER_ID
    events = sys.monitoring.events
    sys.monitoring.use_tool_id(tool, "lcb-runtime-metrics")
    sys.monitoring.register_callback(tool, events.INSTRUCTION, tracer.instruction)
    sys.monitoring.register_callback(tool, events.PY_UNWIND, tracer.unwind)
    codes = tracer.register(code)
    for target_code in codes:
        sys.monitoring.set_local_events(tool, target_code, events.INSTRUCTION)
    sys.monitoring.set_events(tool, events.PY_UNWIND)
    try:
        exec(code, globals_dict)
    except SystemExit:
        pass
    except BaseException as exc:
        status = "error"
        error = f"{type(exc).__name__}: {exc}"
    finally:
        for target_code in codes:
            sys.monitoring.set_local_events(tool, target_code, events.NO_EVENTS)
        sys.monitoring.set_events(tool, events.NO_EVENTS)
        sys.monitoring.register_callback(tool, events.INSTRUCTION, None)
        sys.monitoring.register_callback(tool, events.PY_UNWIND, None)
        sys.monitoring.free_tool_id(tool)
    artifact_hash, row_count = tracer.write()
    result = {
        "status": status,
        "error": error,
        "adapter_version": ADAPTER_VERSION,
        "state_counter": (
            "c-iterative-flat-cache-v2"
            if C_STATE_COUNTER
            else "python-reference-v1"
        ),
        "observation_convention": OBSERVATION_CONVENTION,
        "Omega_hat_NativeTrace": tracer.native_trace,
        "Omega_hat_StateSize": (
            "NOT_MEASURED" if tracer.state_error else tracer.max_state_size
        ),
        "Omega_hat_StateLoad": (
            "NOT_MEASURED" if tracer.state_error else tracer.total_state_size
        ),
        "Omega_hat_StateSizeLowerBound": tracer.max_state_size,
        "Omega_hat_StateLoadLowerBound": (
            MAX_STATE_CELL_VISITS + 1
            if (tracer.state_error or {}).get("type")
            == "STATE_TRAVERSAL_WORK_LIMIT"
            else tracer.total_state_size
        ),
        "state_size_peak_event": (
            None if tracer.state_error else tracer.max_state_size_event
        ),
        "state_failure": tracer.state_error,
        "state_cell_visits": tracer.state_cell_visits[0],
        "state_cell_visit_limit": MAX_STATE_CELL_VISITS,
        "raw_artifact_sha256": artifact_hash,
        "raw_observation_rows": row_count,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, sort_keys=True), encoding="utf-8")
    return 0 if status == "ok" else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source", type=Path)
    result.add_argument("source_label")
    result.add_argument("output", type=Path)
    result.add_argument("result", type=Path)
    return result


def main(argv: list[str] | None = None) -> int:
    arguments = parser().parse_args(argv)
    return run(
        arguments.source.resolve(),
        arguments.source_label,
        arguments.output.resolve(),
        arguments.result.resolve(),
    )


if __name__ == "__main__":
    raise SystemExit(main())
