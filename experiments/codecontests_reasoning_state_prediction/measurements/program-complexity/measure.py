from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
import argparse
import csv
import hashlib
import json
import math
import os
import re
import shlex
import subprocess
import tempfile

EXPERIMENT = Path(__file__).resolve().parents[2]
REPOSITORY = EXPERIMENT.parents[1]
DEFAULT_OUTPUT = EXPERIMENT / "measurements/program-complexity/profiles.json"
DEFAULT_REPORT = EXPERIMENT / "measurements/program-complexity/README.md"
DEFAULT_STATIC_CSV = EXPERIMENT / "measurements/program-complexity/static-profiles.csv"
DEFAULT_DYNAMIC_CSV = EXPERIMENT / "measurements/program-complexity/dynamic-profiles.csv"
DEFAULT_ARM_MAP_CSV = EXPERIMENT / "measurements/program-complexity/arm-profile-map.csv"
STATE_RUNTIME = EXPERIMENT / "measurements/program-complexity/state_runtime.hpp"
SCHEMA = "program-complexity-cpp-v4"
SKILL_VERSION = "measure-program-complexity-v4"
DYNAMIC_ADAPTER_VERSION = "clang-18.1.8-coverage-state-load-v1"
DOCKER_IMAGE = "silkeh/clang@sha256:9388794775d1393c16b6897b4775b6d3e29459319de0bfafec59a20262e1fa68"
DOCKER_PLATFORM = "linux/amd64"
AST_NAMESPACE = "__measure_scope"
AST_PREFIX = "#define main __measure_main\nnamespace __measure_scope {\n"
LOOP_KINDS = {"ForStmt", "WhileStmt", "DoStmt", "CXXForRangeStmt"}
FUNCTION_KINDS = {
    "FunctionDecl",
    "CXXMethodDecl",
    "CXXConstructorDecl",
    "CXXDestructorDecl",
    "CXXConversionDecl",
}
VARIABLE_DECL_KINDS = {
    "VarDecl",
    "ParmVarDecl",
    "BindingDecl",
    "DecompositionDecl",
    "NonTypeTemplateParmDecl",
}
ASSIGNMENT_OPERATORS = {
    "=",
    "+=",
    "-=",
    "*=",
    "/=",
    "%=",
    "<<=",
    ">>=",
    "&=",
    "|=",
    "^=",
}
OVERLOADED_ASSIGNMENT_NAMES = {
    "operator=",
    "operator+=",
    "operator-=",
    "operator*=",
    "operator/=",
    "operator%=",
    "operator<<=",
    "operator>>=",
    "operator&=",
    "operator|=",
    "operator^=",
    "operator++",
    "operator--",
}
CXX_KEYWORDS = {
    "alignas",
    "alignof",
    "and",
    "and_eq",
    "asm",
    "auto",
    "bitand",
    "bitor",
    "bool",
    "break",
    "case",
    "catch",
    "char",
    "char16_t",
    "char32_t",
    "class",
    "compl",
    "concept",
    "const",
    "constexpr",
    "const_cast",
    "continue",
    "co_await",
    "co_return",
    "co_yield",
    "decltype",
    "default",
    "delete",
    "do",
    "double",
    "dynamic_cast",
    "else",
    "enum",
    "explicit",
    "export",
    "extern",
    "false",
    "float",
    "for",
    "friend",
    "goto",
    "if",
    "inline",
    "int",
    "long",
    "mutable",
    "namespace",
    "new",
    "noexcept",
    "not",
    "not_eq",
    "nullptr",
    "operator",
    "or",
    "or_eq",
    "private",
    "protected",
    "public",
    "register",
    "reinterpret_cast",
    "requires",
    "return",
    "short",
    "signed",
    "sizeof",
    "static",
    "static_assert",
    "static_cast",
    "struct",
    "switch",
    "template",
    "this",
    "thread_local",
    "throw",
    "true",
    "try",
    "typedef",
    "typeid",
    "typename",
    "union",
    "unsigned",
    "using",
    "virtual",
    "void",
    "volatile",
    "wchar_t",
    "while",
    "xor",
    "xor_eq",
}
HALSTEAD_IGNORED_KINDS = {
    "unknown",
    "comment",
    "l_paren",
    "r_paren",
    "l_brace",
    "r_brace",
    "comma",
    "semi",
}
LITERAL_KINDS = {
    "numeric_constant",
    "char_constant",
    "wide_char_constant",
    "utf8_char_constant",
    "utf16_char_constant",
    "utf32_char_constant",
    "string_literal",
    "wide_string_literal",
    "utf8_string_literal",
    "utf16_string_literal",
    "utf32_string_literal",
    "header_name",
}
TOKEN_LINE = re.compile(
    r"^(?P<kind>[a-z_]+) '(?P<spelling>.*)'\s+"
    r"(?:\[[^]]+\]\s+)?Loc=<.*:(?P<line>\d+):(?P<column>\d+)>$"
)


@dataclass(frozen=True)
class SourceMap:
    source: str
    first_line_bytes: int
    added_bytes: int

    def original_offset(self, wrapped_offset: int) -> int | None:
        start = self.first_line_bytes + self.added_bytes
        if wrapped_offset < start:
            return None
        original = wrapped_offset - self.added_bytes
        return original if 0 <= original < len(self.source.encode()) else None

    def line_column(self, offset: int) -> tuple[int, int]:
        data = self.source.encode()
        line = data.count(b"\n", 0, offset) + 1
        line_start = data.rfind(b"\n", 0, offset) + 1
        return line, offset - line_start + 1


@dataclass(frozen=True)
class FunctionBody:
    node: dict[str, Any]
    body: dict[str, Any]
    body_key: tuple[Any, ...]
    parameters: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class Coverage:
    positions: tuple[tuple[int, int], ...]
    segments: tuple[tuple[int, int, int, bool], ...]
    line_shift_after_first: int
    native_trace_length: int
    native_trace_region_count: int

    def count(self, line: int, column: int) -> int:
        transformed_line = line + (
            self.line_shift_after_first if line > 1 else 0
        )
        index = bisect_right(self.positions, (transformed_line, column)) - 1
        if index < 0:
            return 0
        _, _, count, has_count = self.segments[index]
        return count if has_count else 0


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def run(command: list[str], **kwargs: Any) -> subprocess.CompletedProcess:
    process = subprocess.run(command, capture_output=True, **kwargs)
    if process.returncode:
        stderr = process.stderr.decode(errors="replace") if isinstance(process.stderr, bytes) else process.stderr
        raise RuntimeError(f"command failed ({process.returncode}): {' '.join(command)}\n{stderr[-4000:]}")
    return process


def wrapped_source(source: str) -> tuple[str, SourceMap]:
    lines = source.splitlines(keepends=True)
    includes = [line for line in lines if line.lstrip().startswith("#include")]
    if not includes:
        raise RuntimeError("expected at least one #include directive")
    masked = "".join(
        (" " * (len(line) - 1) + "\n")
        if line.endswith("\n") and line.lstrip().startswith("#include")
        else (" " * len(line))
        if line.lstrip().startswith("#include")
        else line
        for line in lines
    )
    masked = masked.replace("::visit", "  visit")
    prefix = "".join(includes) + AST_PREFIX
    wrapped = prefix + masked + "\n}\n"
    return wrapped, SourceMap(
        source=source,
        first_line_bytes=0,
        added_bytes=len(prefix.encode()),
    )


def location_point(location: dict[str, Any]) -> dict[str, Any]:
    if "expansionLoc" in location:
        return location_point(location["expansionLoc"])
    if "spellingLoc" in location:
        return location_point(location["spellingLoc"])
    return location


def source_range(
    node: dict[str, Any], source_map: SourceMap
) -> tuple[int, int] | None:
    range_value = node.get("range")
    if not isinstance(range_value, dict):
        return None
    begin = location_point(range_value.get("begin", {}))
    end = location_point(range_value.get("end", {}))
    if not isinstance(begin.get("offset"), int) or not isinstance(end.get("offset"), int):
        return None
    start = source_map.original_offset(begin["offset"])
    finish_start = source_map.original_offset(end["offset"])
    if start is None or finish_start is None:
        return None
    finish = finish_start + int(end.get("tokLen", 1))
    if finish > len(source_map.source.encode()) or start >= finish:
        return None
    return start, finish


def node_key(node: dict[str, Any], source_map: SourceMap) -> tuple[Any, ...] | None:
    measured_range = source_range(node, source_map)
    if measured_range is None:
        return None
    return (
        node.get("kind"),
        *measured_range,
        node.get("name"),
        node.get("opcode"),
    )


def explicit_node(node: dict[str, Any], source_map: SourceMap) -> bool:
    return not node.get("isImplicit", False) and source_range(node, source_map) is not None


def node_source(node: dict[str, Any], source_map: SourceMap) -> str:
    measured_range = source_range(node, source_map)
    if measured_range is None:
        return ""
    return source_map.source.encode()[measured_range[0] : measured_range[1]].decode(
        errors="replace"
    )


def measurement_helper_node(node: dict[str, Any], source_map: SourceMap) -> bool:
    """Identify inserted __cc_ counter events that must not count as program work."""
    return "__cc_" in node_source(node, source_map)


def direct_body(node: dict[str, Any]) -> dict[str, Any] | None:
    for child in reversed(node.get("inner", [])):
        if child.get("kind") in {"CompoundStmt", "CXXTryStmt"}:
            return child
    return None


def collect_function_bodies(
    root: dict[str, Any], source_map: SourceMap
) -> list[FunctionBody]:
    bodies: dict[tuple[Any, ...], FunctionBody] = {}

    def visit(node: dict[str, Any]) -> None:
        if node.get("kind") in FUNCTION_KINDS and explicit_node(node, source_map):
            body = direct_body(node)
            body_key = node_key(body, source_map) if body is not None else None
            if body is not None and body_key is not None and body_key not in bodies:
                parameters = tuple(
                    child
                    for child in node.get("inner", [])
                    if child.get("kind") == "ParmVarDecl"
                    and explicit_node(child, source_map)
                )
                bodies[body_key] = FunctionBody(node, body, body_key, parameters)
        for child in node.get("inner", []):
            visit(child)

    visit(root)
    return sorted(
        bodies.values(),
        key=lambda item: source_range(item.body, source_map) or (0, 0),
    )


def branch_children(node: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    children = list(node.get("inner", []))
    if not children:
        return [], []
    if node.get("kind") == "IfStmt":
        count = 2 if node.get("hasElse") else 1
        return children[:-count], children[-count:]
    if node.get("kind") in {"ConditionalOperator", "BinaryConditionalOperator"}:
        return children[:-2], children[-2:]
    return children, []


def loop_body(node: dict[str, Any]) -> dict[str, Any] | None:
    children = node.get("inner", [])
    if not children:
        return None
    return children[0] if node.get("kind") == "DoStmt" else children[-1]


def static_control_metrics(
    functions: list[FunctionBody], source_map: SourceMap
) -> dict[str, int]:
    body_keys = {item.body_key for item in functions}
    decisions: set[tuple[Any, ...]] = set()
    max_if_depth = 0
    max_loop_depth = 0

    def visit(
        node: dict[str, Any],
        current_body: tuple[Any, ...],
        if_depth: int,
        loop_depth: int,
    ) -> None:
        nonlocal max_if_depth, max_loop_depth
        key = node_key(node, source_map)
        if key in body_keys and key != current_body:
            return
        kind = node.get("kind")
        is_explicit = explicit_node(node, source_map)
        if is_explicit and (
            kind in {"IfStmt", "ConditionalOperator", "BinaryConditionalOperator", "CaseStmt", "CXXCatchStmt"}
            or kind in LOOP_KINDS
            or (kind == "BinaryOperator" and node.get("opcode") in {"&&", "||"})
        ):
            decisions.add(key)

        if is_explicit and kind in {"IfStmt", "ConditionalOperator", "BinaryConditionalOperator"}:
            next_depth = if_depth + 1
            max_if_depth = max(max_if_depth, next_depth)
            other, branches = branch_children(node)
            for child in other:
                visit(child, current_body, if_depth, loop_depth)
            for index, child in enumerate(branches):
                if kind == "IfStmt" and index == 1 and child.get("kind") == "IfStmt":
                    visit(child, current_body, if_depth, loop_depth)
                else:
                    visit(child, current_body, next_depth, loop_depth)
            return

        if is_explicit and kind in LOOP_KINDS:
            next_depth = loop_depth + 1
            max_loop_depth = max(max_loop_depth, next_depth)
            body = loop_body(node)
            for child in node.get("inner", []):
                visit(
                    child,
                    current_body,
                    if_depth,
                    next_depth if child is body else loop_depth,
                )
            return

        for child in node.get("inner", []):
            visit(child, current_body, if_depth, loop_depth)

    for function in functions:
        visit(function.body, function.body_key, 0, 0)
    return {
        "cyclomatic_complexity": len(functions) + len(decisions),
        "function_bodies": len(functions),
        "decision_sites": len(decisions),
        "max_if_else_depth": max_if_depth,
        "max_loop_depth": max_loop_depth,
    }


def operator_reference_names(node: dict[str, Any]) -> set[str]:
    names: set[str] = set()

    def visit(value: dict[str, Any]) -> None:
        if value.get("kind") == "DeclRefExpr":
            name = value.get("referencedDecl", {}).get("name")
            if isinstance(name, str) and name.startswith("operator"):
                names.add(name)
        for child in value.get("inner", []):
            visit(child)

    visit(node)
    return names


def is_explicit_overloaded_assignment(
    node: dict[str, Any], source_map: SourceMap
) -> bool:
    if not operator_reference_names(node) & OVERLOADED_ASSIGNMENT_NAMES:
        return False
    measured_range = source_range(node, source_map)
    if measured_range is None:
        return False
    text = source_map.source.encode()[measured_range[0] : measured_range[1]].decode(
        errors="replace"
    )
    return bool(
        re.search(r"(?:\+\+|--|(?<![=!<>])=(?!=)|[+\-*/%&|^]|<<|>>)\s*=", text)
        or "++" in text
        or "--" in text
    )


def static_dependency_degree(root: dict[str, Any], source_map: SourceMap) -> dict[str, int]:
    visible_names: set[str] = set()
    redefinition_sites: set[tuple[Any, ...]] = set()
    use_sites: set[tuple[Any, ...]] = set()

    def collect_names(node: dict[str, Any]) -> None:
        if (
            node.get("kind") in VARIABLE_DECL_KINDS
            and explicit_node(node, source_map)
            and isinstance(node.get("name"), str)
            and not node["name"].startswith("__")
        ):
            visible_names.add(node["name"])
        for child in node.get("inner", []):
            collect_names(child)

    def visit(node: dict[str, Any], parents: tuple[dict[str, Any], ...]) -> None:
        kind = node.get("kind")
        key = node_key(node, source_map)
        if key is not None and explicit_node(node, source_map):
            is_redefinition = (
                kind in {"BinaryOperator", "CompoundAssignOperator"}
                and node.get("opcode") in ASSIGNMENT_OPERATORS
            ) or (
                kind == "UnaryOperator" and node.get("opcode") in {"++", "--"}
            ) or (
                kind == "CXXOperatorCallExpr"
                and is_explicit_overloaded_assignment(node, source_map)
            )
            if is_redefinition:
                redefinition_sites.add(key)

            if kind == "DeclRefExpr":
                referenced = node.get("referencedDecl", {})
                name = referenced.get("name")
                if referenced.get("kind") in VARIABLE_DECL_KINDS and name in visible_names:
                    pure_assignment_target = False
                    if parents:
                        parent = parents[-1]
                        if (
                            parent.get("kind") == "BinaryOperator"
                            and parent.get("opcode") == "="
                            and parent.get("inner")
                        ):
                            left_range = source_range(parent["inner"][0], source_map)
                            pure_assignment_target = left_range == source_range(node, source_map)
                    if not pure_assignment_target:
                        use_sites.add((*key, name))
        for child in node.get("inner", []):
            visit(child, (*parents, node))

    collect_names(root)
    visit(root, ())
    return {
        "dependency_degree": len(use_sites) + len(redefinition_sites),
        "variable_use_sites": len(use_sites),
        "variable_redefinition_sites": len(redefinition_sites),
    }


def strip_comments(source: str) -> str:
    output: list[str] = []
    index = 0
    state = "code"
    quote = ""
    while index < len(source):
        char = source[index]
        next_char = source[index + 1] if index + 1 < len(source) else ""
        if state == "code":
            if char == "/" and next_char == "/":
                output.extend("  ")
                index += 2
                state = "line_comment"
                continue
            if char == "/" and next_char == "*":
                output.extend("  ")
                index += 2
                state = "block_comment"
                continue
            if char in {'"', "'"}:
                quote = char
                state = "string"
            output.append(char)
        elif state == "line_comment":
            output.append("\n" if char == "\n" else " ")
            if char == "\n":
                state = "code"
        elif state == "block_comment":
            output.append("\n" if char == "\n" else " ")
            if char == "*" and next_char == "/":
                output.append(" ")
                index += 2
                state = "code"
                continue
        else:
            output.append(char)
            if char == "\\" and next_char:
                output.append(next_char)
                index += 2
                continue
            if char == quote:
                state = "code"
        index += 1
    return "".join(output)


def halstead_and_loc(source: str, token_dump: str) -> dict[str, int | float]:
    operators: list[str] = []
    operands: list[str] = []
    source_lines = source.splitlines()
    include_lines = {
        index
        for index, line in enumerate(source_lines, 1)
        if line.lstrip().startswith("#include")
    }
    for line in token_dump.splitlines():
        match = TOKEN_LINE.fullmatch(line)
        if match is None:
            continue
        kind = match.group("kind")
        spelling = match.group("spelling")
        line_number = int(match.group("line"))
        if line_number in include_lines or kind in HALSTEAD_IGNORED_KINDS:
            continue
        if kind == "raw_identifier":
            (operators if spelling in CXX_KEYWORDS else operands).append(spelling)
        elif kind in LITERAL_KINDS:
            operands.append(spelling)
        else:
            operators.append(spelling)
    distinct_operators = set(operators)
    distinct_operands = set(operands)
    vocabulary = len(distinct_operators) + len(distinct_operands)
    length = len(operators) + len(operands)
    volume = length * math.log2(vocabulary) if vocabulary else 0.0
    lines_of_code = sum(bool(line.strip()) for line in strip_comments(source).splitlines())
    return {
        "lines_of_code": lines_of_code,
        "halstead_volume": round(volume, 3),
        "halstead_vocabulary": vocabulary,
        "halstead_operator_occurrences": len(operators),
        "halstead_operand_occurrences": len(operands),
        "halstead_distinct_operators": len(distinct_operators),
        "halstead_distinct_operands": len(distinct_operands),
    }


def load_ast(
    source_path: Path,
    source: str,
    ast_path: Path,
) -> tuple[dict[str, Any], SourceMap]:
    _, source_map = wrapped_source(source)
    root = json.loads(ast_path.read_text())
    if root.get("kind") != "NamespaceDecl" or root.get("name") != AST_NAMESPACE:
        raise RuntimeError(f"unexpected AST root for {source_path}")
    return root, source_map


def compatible_execution_source(problem_id: str, source: str) -> tuple[str, int, str | None]:
    if problem_id != "codecontests-validation-1569f":
        return source, 0, None
    first, separator, rest = source.partition("\n")
    transformed = first + separator + "#define visit cc_visit\n" + rest
    return transformed, 1, "Added a post-include macro rename for the global `visit` array to avoid Clang/libstdc++ `std::visit` ambiguity; source control flow and variable operations are unchanged."


def state_binding_expression(nodes: list[dict[str, Any]], identifier: int) -> str:
    bindings = [
        (node, node.get("name"))
        for node in nodes
        if isinstance(node.get("name"), str)
        and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", node["name"])
        and not node["name"].startswith("__")
    ]
    if not bindings:
        return ""
    cells = []
    for node, name in bindings:
        qualifier = str(node.get("type", {}).get("qualType", ""))
        is_pack = bool(node.get("isParameterPack")) or "..." in qualifier
        if "&" in qualifier:
            continue
        cell = (
            "::__cc_state::cell_count<std::remove_reference_t<decltype("
            f"{name})>>::value"
        )
        cells.append(f"({cell} + ... + 0)" if is_pack else cell)
    cell_expression = " + ".join(cells) if cells else "0"
    storage = "static " if any(node.get("storageClass") == "static" for node in nodes) else ""
    return (
        f"; {storage}::__cc_state::binding_guard __cc_state_binding_{identifier}"
        f"({cell_expression});"
    )


def state_instrumented_source(
    root: dict[str, Any], source_map: SourceMap
) -> str:
    source = source_map.source
    source_bytes = source.encode()
    insertions: dict[int, list[str]] = {}
    global_groups: dict[int, list[dict[str, Any]]] = {}
    identifier = 0

    def insert(offset: int, text: str) -> None:
        if text:
            insertions.setdefault(offset, []).append(text)

    def next_guard(nodes: list[dict[str, Any]]) -> str:
        nonlocal identifier
        identifier += 1
        return state_binding_expression(nodes, identifier)

    record_specs: list[tuple[int, int, str]] = []

    def field_cell_term(field: dict[str, Any]) -> str:
        qualifier = str(field.get("type", {}).get("qualType", ""))
        if re.search(
            r"(?:^|::)(?:vector|deque|map|unordered_map|set|unordered_set|string|queue|stack|priority_queue)\b",
            qualifier,
        ):
            return "0"
        dimensions = [int(value) for value in re.findall(r"\[([0-9]+)\]", qualifier)]
        if dimensions:
            cells = 1
            width = 1
            for dimension in dimensions:
                width *= dimension
                cells += width
            return str(cells)
        if "pair<" in qualifier:
            return "3"
        array_match = re.search(r"(?:^|::)array<[^,>]+,\s*([0-9]+)>", qualifier)
        if array_match:
            return str(1 + int(array_match.group(1)))
        return "1"

    def collect_records(
        node: dict[str, Any],
        parents: tuple[str, ...] = (),
        template_parameters: tuple[dict[str, Any], ...] = (),
        outer_end: int | None = None,
        namespaces: tuple[str, ...] = (),
    ) -> None:
        kind = node.get("kind")
        if kind == "NamespaceDecl" and node is not root:
            namespace_name = node.get("name")
            if not isinstance(namespace_name, str) or not namespace_name:
                return
            for child in node.get("inner", []):
                collect_records(
                    child,
                    parents,
                    template_parameters,
                    outer_end,
                    (*namespaces, namespace_name),
                )
            return
        if kind == "ClassTemplateDecl" and explicit_node(node, source_map):
            parameters = tuple(
                child
                for child in node.get("inner", [])
                if child.get("kind")
                in {"TemplateTypeParmDecl", "NonTypeTemplateParmDecl"}
            )
            record = next(
                (
                    child
                    for child in node.get("inner", [])
                    if child.get("kind") == "CXXRecordDecl"
                    and child.get("completeDefinition")
                    and isinstance(child.get("name"), str)
                    and explicit_node(child, source_map)
                ),
                None,
            )
            if record is not None and not parents:
                declarations = []
                arguments = []
                for parameter in parameters:
                    parameter_name = parameter.get("name") or f"T{len(arguments)}"
                    if parameter.get("kind") == "TemplateTypeParmDecl":
                        declarations.append(f"class {parameter_name}")
                    else:
                        parameter_type = parameter.get("type", {}).get("qualType", "int")
                        declarations.append(f"{parameter_type} {parameter_name}")
                    arguments.append(parameter_name)
                fields = [
                    child
                    for child in record.get("inner", [])
                    if child.get("kind") == "FieldDecl"
                    and explicit_node(child, source_map)
                ]
                field_terms = [field_cell_term(field) for field in fields]
                value = "1" + (
                    " + " + " + ".join(field_terms) if field_terms else ""
                )
                measured = source_range(node, source_map)
                if measured is not None:
                    name = record["name"]
                    qualified = "::".join((*namespaces, name))
                    template = f"template <{', '.join(declarations)}>"
                    close_namespaces = "} " * len(namespaces)
                    reopen_namespaces = " ".join(
                        f"namespace {namespace} {{" for namespace in namespaces
                    )
                    tag = record.get("tagUsed") or "class"
                    record_specs.append(
                        (
                            measured[0],
                            0,
                            f"{template} {tag} {name}; {close_namespaces}"
                            "namespace __cc_state { "
                            f"{template} struct cell_count<::{qualified}"
                            f"<{', '.join(arguments)}>> {{ "
                            f"static constexpr long long value = {value}; }}; }} "
                            f"{reopen_namespaces}\n",
                        )
                    )
            for child in node.get("inner", []):
                collect_records(
                    child, parents, parameters, outer_end, namespaces
                )
            return
        next_parents = parents
        if (
            kind == "CXXRecordDecl"
            and node.get("completeDefinition")
            and isinstance(node.get("name"), str)
            and explicit_node(node, source_map)
            and not parents
            and not template_parameters
        ):
            name = node["name"]
            qualified = "::".join((*namespaces, *parents, name))
            fields = [
                child
                for child in node.get("inner", [])
                if child.get("kind") == "FieldDecl"
                and explicit_node(child, source_map)
            ]
            field_terms = [field_cell_term(field) for field in fields]
            value = "1" + (" + " + " + ".join(field_terms) if field_terms else "")
            template = "template <>"
            target = f"::{qualified}"
            measured = source_range(node, source_map)
            if measured is not None:
                close_namespaces = "} " * len(namespaces)
                reopen_namespaces = " ".join(
                    f"namespace {namespace} {{" for namespace in namespaces
                )
                tag = node.get("tagUsed") or "struct"
                record_specs.append(
                    (
                        measured[0],
                        0,
                        f"{tag} {name}; {close_namespaces}"
                        "namespace __cc_state { "
                        f"{template} struct cell_count<{target}> {{ "
                        f"static constexpr long long value = {value}; }}; }} "
                        f"{reopen_namespaces}\n",
                    )
                )
            next_parents = (*parents, name)
            if outer_end is None and measured is not None:
                outer_end = measured[1]
        for child in node.get("inner", []):
            if kind == "ClassTemplateDecl":
                continue
            collect_records(
                child,
                next_parents,
                template_parameters,
                outer_end,
                namespaces,
            )

    collect_records(root)
    for offset, _, text in sorted(record_specs, key=lambda item: (item[0], -item[1])):
        insert(offset, text)

    body_keys = {
        item.body_key: item
        for item in collect_function_bodies(root, source_map)
    }

    def visit(node: dict[str, Any], parent: dict[str, Any] | None = None) -> None:
        key = node_key(node, source_map)
        if (
            node.get("kind") in {"VarDecl", "DecompositionDecl"}
            and parent is not None
            and parent.get("kind") == "NamespaceDecl"
            and node.get("storageClass") != "extern"
            and explicit_node(node, source_map)
        ):
            measured = source_range(node, source_map)
            if measured is not None:
                semicolon = source_bytes.find(b";", measured[1])
                if semicolon < 0:
                    raise RuntimeError("could not locate global declaration terminator")
                global_groups.setdefault(semicolon + 1, []).append(node)
        function = body_keys.get(key)
        if function is not None:
            measured = source_range(node, source_map)
            if measured is not None:
                insert(measured[0] + 1, next_guard(list(function.parameters)))

        if node.get("kind") == "DeclStmt" and explicit_node(node, source_map):
            if parent is None or parent.get("kind") not in {
                "ForStmt",
                "CXXForRangeStmt",
                "IfStmt",
                "SwitchStmt",
                "WhileStmt",
            }:
                declarations = [
                    child
                    for child in node.get("inner", [])
                    if child.get("kind") in {"VarDecl", "DecompositionDecl"}
                    and child.get("init") is not None
                    and explicit_node(child, source_map)
                ]
                measured = source_range(node, source_map)
                if declarations and measured is not None:
                    insert(measured[1], next_guard(declarations))

        if node.get("kind") in {"ForStmt", "CXXForRangeStmt"}:
            body = loop_body(node)
            if body is not None and body.get("kind") == "CompoundStmt":
                declarations = []
                for child in node.get("inner", []):
                    if child is body:
                        continue
                    stack = [child]
                    while stack:
                        item = stack.pop()
                        if (
                            item.get("kind") in {"VarDecl", "DecompositionDecl", "BindingDecl"}
                            and explicit_node(item, source_map)
                            and isinstance(item.get("name"), str)
                        ):
                            declarations.append(item)
                        stack.extend(item.get("inner", []))
                measured = source_range(body, source_map)
                if declarations and measured is not None:
                    unique = {node.get("name"): node for node in declarations}
                    insert(measured[0] + 1, next_guard(list(unique.values())))

        for child in node.get("inner", []):
            visit(child, node)

    visit(root)
    for offset, declarations in sorted(global_groups.items()):
        insert(offset, next_guard(declarations))
    first_newline = source.find("\n")
    if first_newline < 0:
        raise RuntimeError("state adapter requires a leading include line")
    state_header = repository_container_path(STATE_RUNTIME)
    insert(first_newline + 1, f'#include "{state_header}"\n')

    data = source_bytes
    for offset in sorted(insertions, reverse=True):
        addition = "".join(insertions[offset]).encode()
        data = data[:offset] + addition + data[offset:]
    return data.decode().replace("std::_Exit(0);", "std::exit(0);")


def repository_container_path(path: Path) -> str:
    return "/repo/" + path.resolve().relative_to(REPOSITORY.resolve()).as_posix()


def run_container_measurement(
    problem_id: str,
    standard: str,
    sources: dict[str, tuple[Path, str]],
    executions: dict[str, tuple[str, Path]],
    directory: Path,
    repetitions: int,
) -> tuple[dict[str, int], dict[str, str | None]]:
    line_shifts: dict[str, int] = {}
    transform_notes: dict[str, str | None] = {}
    commands = [
        "set -euxo pipefail",
    ]
    for source_key, (source_path, source) in sources.items():
        wrapped, _ = wrapped_source(source)
        (directory / f"{source_key}-ast-wrapper.cpp").write_text(wrapped)
        execution_source, line_shift, transform_note = compatible_execution_source(
            problem_id, source
        )
        execution_source = execution_source.replace(
            "std::_Exit(0);", "std::exit(0);"
        )
        (directory / f"{source_key}-program.cpp").write_text(execution_source)
        line_shifts[source_key] = line_shift
        transform_notes[source_key] = transform_note
        commands.extend(
            [
                f"clang++ -std={shlex.quote(standard)} -Wno-return-type -fsyntax-only "
                f"-Xclang -ast-dump=json -Xclang -ast-dump-filter={AST_NAMESPACE} "
                f"/work/{source_key}-ast-wrapper.cpp > /work/{source_key}-ast.json",
                f"clang++ -std={shlex.quote(standard)} -O2 -fprofile-instr-generate "
                f"-fcoverage-mapping /work/{source_key}-program.cpp "
                f"-o /work/{source_key}-program",
            ]
        )
        source_in_container = repository_container_path(source_path)
        commands.append(
            f"clang++ -std={shlex.quote(standard)} -Xclang -dump-raw-tokens "
            f"-fsyntax-only {shlex.quote(source_in_container)} "
            f">/dev/null 2>/work/{source_key}-tokens.txt"
        )
    for label, (source_key, task) in executions.items():
        input_path = repository_container_path(task / "input.txt")
        expected_path = repository_container_path(task / "ground-output.txt")
        for repetition in range(1, repetitions + 1):
            prefix = f"{label}-{repetition}"
            commands.extend(
                [
                    f"LLVM_PROFILE_FILE=/work/{prefix}.profraw timeout 180 "
                    f"/work/{source_key}-program "
                    f"< {shlex.quote(input_path)} > /work/{prefix}.out",
                    f"cmp /work/{prefix}.out {shlex.quote(expected_path)}",
                    f"llvm-profdata merge -sparse /work/{prefix}.profraw "
                    f"-o /work/{prefix}.profdata",
                    f"llvm-cov export /work/{source_key}-program "
                    f"-instr-profile=/work/{prefix}.profdata "
                    f"/work/{source_key}-program.cpp > /work/{prefix}.coverage.json",
                ]
            )
    commands.extend(
        [
            "clang++ --version | head -1 > /work/clang-version.txt",
            "llvm-cov --version | head -1 > /work/llvm-cov-version.txt",
        ]
    )
    run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            DOCKER_PLATFORM,
            "--network",
            "none",
            "--read-only",
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
            "--mount",
            f"type=bind,src={REPOSITORY.resolve()},dst=/repo,readonly",
            "--mount",
            f"type=bind,src={directory.resolve()},dst=/work",
            "--tmpfs",
            "/tmp:rw,nosuid,size=1g",
            DOCKER_IMAGE,
            "bash",
            "-lc",
            ";\n".join(commands),
        ],
        timeout=1800,
    )
    return line_shifts, transform_notes


def run_ast_measurement(
    standard: str,
    sources: dict[str, tuple[Path, str]],
    directory: Path,
) -> str:
    """Materialize only the ASTs needed by the state adapter."""
    commands = ["set -euxo pipefail"]
    for source_key, (_, source) in sources.items():
        wrapped, _ = wrapped_source(source)
        (directory / f"{source_key}-ast-wrapper.cpp").write_text(wrapped)
        commands.append(
            f"clang++ -std={shlex.quote(standard)} -Wno-return-type -fsyntax-only "
            f"-Xclang -ast-dump=json -Xclang -ast-dump-filter={AST_NAMESPACE} "
            f"/work/{source_key}-ast-wrapper.cpp > /work/{source_key}-ast.json"
        )
    commands.append("clang++ --version | head -1 > /work/clang-version.txt")
    run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            DOCKER_PLATFORM,
            "--network",
            "none",
            "--read-only",
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
            "--mount",
            f"type=bind,src={REPOSITORY.resolve()},dst=/repo,readonly",
            "--mount",
            f"type=bind,src={directory.resolve()},dst=/work",
            "--tmpfs",
            "/tmp:rw,nosuid,size=1g",
            DOCKER_IMAGE,
            "bash",
            "-lc",
            ";\n".join(commands),
        ],
        timeout=1800,
    )
    return (directory / "clang-version.txt").read_text().strip()


def run_state_measurement(
    problem_id: str,
    standard: str,
    sources: dict[str, tuple[Path, str]],
    ast_profiles: dict[str, tuple[dict[str, Any], SourceMap, list[FunctionBody]]],
    executions: dict[str, tuple[str, Path]],
    directory: Path,
    repetitions: int,
) -> None:
    commands = ["set -euxo pipefail"]
    for source_key, (_, source) in sources.items():
        root, source_map, _ = ast_profiles[source_key]
        instrumented = state_instrumented_source(root, source_map)
        instrumented, _, _ = compatible_execution_source(problem_id, instrumented)
        (directory / f"{source_key}-state.cpp").write_text(instrumented)
        commands.append(
            f"clang++ -std={shlex.quote(standard)} -O2 "
            f"/work/{source_key}-state.cpp -o /work/{source_key}-state"
        )
    for label, (source_key, task) in executions.items():
        input_path = repository_container_path(task / "input.txt")
        expected_path = repository_container_path(task / "ground-output.txt")
        for repetition in range(1, repetitions + 1):
            prefix = f"{label}-{repetition}"
            commands.extend(
                [
                    f"timeout 180 /work/{source_key}-state "
                    f"< {shlex.quote(input_path)} > /work/{prefix}.state.out "
                    f"2> /work/{prefix}.state.txt",
                    f"cmp /work/{prefix}.state.out {shlex.quote(expected_path)}",
                    f"grep -E '^__CC_STATE_(SIZE|LOAD|OBSERVATIONS)__ [0-9]+$' "
                    f"/work/{prefix}.state.txt > /work/{prefix}.state.result",
                ]
            )
    run(
        [
            "docker",
            "run",
            "--rm",
            "--platform",
            DOCKER_PLATFORM,
            "--network",
            "none",
            "--read-only",
            "--security-opt",
            "no-new-privileges",
            "--cap-drop",
            "ALL",
            "--mount",
            f"type=bind,src={REPOSITORY.resolve()},dst=/repo,readonly",
            "--mount",
            f"type=bind,src={directory.resolve()},dst=/work",
            "--tmpfs",
            "/tmp:rw,nosuid,size=1g",
            DOCKER_IMAGE,
            "bash",
            "-lc",
            ";\n".join(commands),
        ],
        timeout=1800,
    )


def load_state_metrics(path: Path) -> tuple[int, int, int]:
    matches = dict(
        re.findall(
            r"^__CC_STATE_(SIZE|LOAD|OBSERVATIONS)__ ([0-9]+)$",
            path.read_text(),
            flags=re.MULTILINE,
        )
    )
    if set(matches) != {"SIZE", "LOAD", "OBSERVATIONS"}:
        raise RuntimeError(f"invalid state result: {path}")
    return int(matches["SIZE"]), int(matches["LOAD"]), int(matches["OBSERVATIONS"])


def load_coverage(
    path: Path,
    line_shift: int,
    source_key: str,
    source: str,
) -> Coverage:
    document = json.loads(path.read_text())
    data = document["data"][0]
    files = data["files"]
    target = f"/work/{source_key}-program.cpp"
    coverage_file = next(
        item
        for item in files
        if item["filename"] == target
    )
    segments = tuple(
        (int(row[0]), int(row[1]), int(row[2]), bool(row[3]))
        for row in coverage_file["segments"]
    )
    source_lines = source.splitlines()
    native_regions: list[int] = []
    for function in data.get("functions", []):
        filenames = function.get("filenames", [])
        for region in function.get("regions", []):
            if len(region) < 8:
                raise RuntimeError(f"unexpected llvm-cov region in {path}: {region}")
            start_line, _, _, _, count, file_id, _, region_kind = region[:8]
            if region_kind != 0 or not (0 <= file_id < len(filenames)):
                continue
            if filenames[file_id] != target:
                continue
            original_line = int(start_line) - (line_shift if int(start_line) > 1 else 0)
            if 1 <= original_line <= len(source_lines) and "__cc_" in source_lines[original_line - 1]:
                continue
            native_regions.append(int(count))
    return Coverage(
        positions=tuple((row[0], row[1]) for row in segments),
        segments=segments,
        line_shift_after_first=line_shift,
        native_trace_length=sum(native_regions),
        native_trace_region_count=len(native_regions),
    )


def coverage_count_for_node(
    node: dict[str, Any], source_map: SourceMap, coverage: Coverage
) -> int:
    measured_range = source_range(node, source_map)
    if measured_range is None:
        return 0
    line, column = source_map.line_column(measured_range[0])
    return coverage.count(line, column)


def dynamic_control_metrics(
    functions: list[FunctionBody], source_map: SourceMap, coverage: Coverage
) -> tuple[int, int]:
    body_keys = {item.body_key for item in functions}
    max_if_depth = 0
    max_loop_depth = 0

    def visit(
        node: dict[str, Any],
        current_body: tuple[Any, ...],
        if_depth: int,
        loop_depth: int,
    ) -> None:
        nonlocal max_if_depth, max_loop_depth
        key = node_key(node, source_map)
        if key in body_keys and key != current_body:
            return
        kind = node.get("kind")
        if explicit_node(node, source_map) and kind in {
            "IfStmt",
            "ConditionalOperator",
            "BinaryConditionalOperator",
        }:
            if kind == "IfStmt" and measurement_helper_node(node, source_map):
                return
            other, branches = branch_children(node)
            for child in other:
                visit(child, current_body, if_depth, loop_depth)
            for index, child in enumerate(branches):
                if kind == "IfStmt" and index == 1 and child.get("kind") == "IfStmt":
                    if coverage_count_for_node(child, source_map, coverage) > 0:
                        visit(child, current_body, if_depth, loop_depth)
                elif coverage_count_for_node(child, source_map, coverage) > 0:
                    next_depth = if_depth + 1
                    max_if_depth = max(max_if_depth, next_depth)
                    visit(child, current_body, next_depth, loop_depth)
            return
        if explicit_node(node, source_map) and kind in LOOP_KINDS:
            body = loop_body(node)
            for child in node.get("inner", []):
                if child is body and coverage_count_for_node(child, source_map, coverage) > 0:
                    next_depth = loop_depth + 1
                    max_loop_depth = max(max_loop_depth, next_depth)
                    visit(child, current_body, if_depth, next_depth)
                elif child is not body:
                    visit(child, current_body, if_depth, loop_depth)
            return
        for child in node.get("inner", []):
            visit(child, current_body, if_depth, loop_depth)

    for function in functions:
        visit(function.body, function.body_key, 0, 0)
    return max_if_depth, max_loop_depth


def decomposition_weight(node: dict[str, Any]) -> int:
    if node.get("kind") != "DecompositionDecl":
        return 1
    bindings = sum(child.get("kind") == "BindingDecl" for child in node.get("inner", []))
    return max(1, bindings)


def executed_assignments(
    root: dict[str, Any],
    functions: list[FunctionBody],
    source_map: SourceMap,
    coverage: Coverage,
) -> int:
    body_keys = {item.body_key for item in functions}
    total = 0
    counted: set[tuple[Any, ...]] = set()

    for child in root.get("inner", []):
        if (
            child.get("kind") in {"VarDecl", "DecompositionDecl"}
            and child.get("init") is not None
            and explicit_node(child, source_map)
        ):
            key = node_key(child, source_map)
            if key is not None and key not in counted:
                counted.add(key)
                total += decomposition_weight(child)

    for function in functions:
        function_count = coverage_count_for_node(function.body, source_map, coverage)
        total += function_count * len(function.parameters)

        def visit(
            node: dict[str, Any],
            parents: tuple[dict[str, Any], ...],
        ) -> None:
            nonlocal total
            key = node_key(node, source_map)
            if key in body_keys and key != function.body_key:
                return
            if key is not None and key not in counted and explicit_node(node, source_map):
                kind = node.get("kind")
                weight = 0
                count_node = node
                if measurement_helper_node(node, source_map) and kind in {
                    "VarDecl",
                    "DecompositionDecl",
                    "BinaryOperator",
                    "CompoundAssignOperator",
                    "UnaryOperator",
                    "CXXOperatorCallExpr",
                }:
                    return
                if kind in {"VarDecl", "DecompositionDecl"} and node.get("init") is not None:
                    weight = decomposition_weight(node)
                    if node.get("storageClass") == "static":
                        execution_count = min(
                            1, coverage_count_for_node(node, source_map, coverage)
                        )
                    else:
                        range_parent = next(
                            (
                                parent
                                for parent in reversed(parents)
                                if parent.get("kind") == "CXXForRangeStmt"
                            ),
                            None,
                        )
                        if range_parent is not None:
                            body = loop_body(range_parent)
                            count_node = body if body is not None else node
                        execution_count = coverage_count_for_node(
                            count_node, source_map, coverage
                        )
                    counted.add(key)
                    total += weight * execution_count
                else:
                    is_assignment = (
                        kind in {"BinaryOperator", "CompoundAssignOperator"}
                        and node.get("opcode") in ASSIGNMENT_OPERATORS
                    ) or (
                        kind == "UnaryOperator" and node.get("opcode") in {"++", "--"}
                    ) or (
                        kind == "CXXOperatorCallExpr"
                        and is_explicit_overloaded_assignment(node, source_map)
                    )
                    if is_assignment:
                        counted.add(key)
                        total += coverage_count_for_node(node, source_map, coverage)
            for child in node.get("inner", []):
                visit(child, (*parents, node))

        visit(function.body, ())
    return total


def dynamic_profile(
    root: dict[str, Any],
    functions: list[FunctionBody],
    source_map: SourceMap,
    coverage: Coverage,
    state_size: int,
    state_load: int,
    state_observation_count: int,
) -> dict[str, Any]:
    return {
        "native_trace_length": coverage.native_trace_length,
        "state_size": state_size,
        "state_load": state_load,
        "state_observation_count": state_observation_count,
        "state_measurement_status": "OK",
    }


def complexity_note(static: dict[str, Any], long_trace: dict[str, Any]) -> str:
    return (
        f"Omega_CC={static['cyclomatic_complexity']}; on the long-trace input, "
        f"Omega_hat_NativeTrace={long_trace['native_trace_length']:,} native events and "
        f"Omega_hat_StateSize={long_trace['state_size']:,} peak reachable runtime value cells, "
        f"with Omega_hat_StateLoad={long_trace['state_load']:,} value-cell observations accumulated across the run."
    )


def measure_problem(
    selection: dict[str, Any], repetitions: int
) -> dict[str, Any]:
    problem_id = selection["problem_id"]
    problem = EXPERIMENT / "problems" / problem_id
    tasks = {
        "short-trace-final": problem / "short-trace-final",
        "long-trace-final": problem / "long-trace-final",
        "inside-loop-state": problem / "inside-loop-state",
        "post-loop-state": problem / "post-loop-state",
    }
    source_paths = {
        "original": tasks["long-trace-final"] / "program.cpp",
        "inside": tasks["inside-loop-state"] / "program.cpp",
        "post": tasks["post-loop-state"] / "program.cpp",
    }
    sources = {key: path.read_text() for key, path in source_paths.items()}
    if (tasks["short-trace-final"] / "program.cpp").read_bytes() != source_paths["original"].read_bytes():
        raise RuntimeError(f"original source differs between E1 and E2: {problem_id}")
    standard = selection["compiler_standard"]
    execution_sources = {
        "short-trace-final": "original",
        "long-trace-final": "original",
        "inside-loop-state": "inside",
        "post-loop-state": "post",
    }

    with tempfile.TemporaryDirectory(prefix=f"complexity-{problem_id}-") as temporary:
        directory = Path(temporary)
        line_shifts, transform_notes = run_container_measurement(
            problem_id,
            standard,
            {
                key: (source_paths[key], sources[key])
                for key in ("original", "inside", "post")
            },
            {
                label: (execution_sources[label], task)
                for label, task in tasks.items()
            },
            directory,
            repetitions,
        )
        ast_profiles = {}
        for source_key in ("original", "inside", "post"):
            root, source_map = load_ast(
                source_paths[source_key],
                sources[source_key],
                directory / f"{source_key}-ast.json",
            )
            ast_profiles[source_key] = (
                root,
                source_map,
                collect_function_bodies(root, source_map),
            )
        run_state_measurement(
            problem_id,
            standard,
            {
                key: (source_paths[key], sources[key])
                for key in ("original", "inside", "post")
            },
            ast_profiles,
            {
                label: (execution_sources[label], task)
                for label, task in tasks.items()
            },
            directory,
            repetitions,
        )
        static_profiles: dict[str, dict[str, Any]] = {}
        for source_key in ("original", "inside", "post"):
            root, source_map, functions = ast_profiles[source_key]
            control = static_control_metrics(functions, source_map)
            static_profiles[source_key] = {
                "cyclomatic_complexity": control["cyclomatic_complexity"],
                "source_sha256": sha256_bytes(source_paths[source_key].read_bytes()),
            }
        static = {
            key: value
            for key, value in static_profiles["original"].items()
            if key != "source_sha256"
        }

        dynamic: dict[str, dict[str, Any]] = {}
        for label, task in tasks.items():
            source_key = execution_sources[label]
            dynamic_root, dynamic_source_map, dynamic_functions = ast_profiles[
                source_key
            ]
            observed = []
            for repetition in range(1, repetitions + 1):
                coverage = load_coverage(
                    directory / f"{label}-{repetition}.coverage.json",
                    line_shifts[source_key],
                    source_key,
                    sources[source_key],
                )
                state_size, state_load, state_observation_count = load_state_metrics(
                    directory / f"{label}-{repetition}.state.result"
                )
                observed.append(
                    dynamic_profile(
                        dynamic_root,
                        dynamic_functions,
                        dynamic_source_map,
                        coverage,
                        state_size,
                        state_load,
                        state_observation_count,
                    )
                )
            if observed[1:] != observed[:-1]:
                raise RuntimeError(
                    f"nondeterministic dynamic complexity for {problem_id}/{label}: {observed}"
                )
            dynamic[label] = {
                **observed[0],
                "input_sha256": sha256_bytes((task / "input.txt").read_bytes()),
                "source_sha256": sha256_bytes(
                    source_paths[source_key].read_bytes()
                ),
                "repeated_measurements": repetitions,
            }
        clang_version = (directory / "clang-version.txt").read_text().strip()
        llvm_cov_version = (directory / "llvm-cov-version.txt").read_text().strip()

    return {
        "problem_id": problem_id,
        "split": selection["split"],
        "rating": selection["cf_rating"],
        "language": f"C++ ({standard})",
        "scope": "Static and dynamic metrics cover the four canonical arms; inserted __cc_ measurement helpers are excluded from dynamic event counts.",
        "source_sha256": sha256_bytes(source_paths["original"].read_bytes()),
        "static": static,
        "static_profiles": static_profiles,
        "dynamic": dynamic,
        "arm_profiles": {
            "short-trace-final": {
                "static_profile": "original",
                "source_input_execution_profile": "short-trace-final",
                "prediction_target_profile": "short-trace-final",
            },
            "long-trace-final": {
                "static_profile": "original",
                "source_input_execution_profile": "long-trace-final",
                "prediction_target_profile": "long-trace-final",
            },
            "inside-loop-state": {
                "static_profile": "inside",
                "source_input_execution_profile": "inside-loop-state",
                "prediction_target_profile": "inside-loop-state",
            },
            "post-loop-state": {
                "static_profile": "post",
                "source_input_execution_profile": "post-loop-state",
                "prediction_target_profile": "post-loop-state",
            },
        },
        "execution_compatibility_transform": transform_notes,
        "tools": {
            "clang": clang_version,
            "llvm_cov": llvm_cov_version,
        },
        "plain_english_profile": complexity_note(static, dynamic["long-trace-final"]),
    }


def refresh_state_profiles_problem(
    selection: dict[str, Any],
    existing: dict[str, Any],
    repetitions: int,
) -> dict[str, Any]:
    """Remeasure changed inside/post sources without rerunning clean executions."""
    problem_id = selection["problem_id"]
    problem = EXPERIMENT / "problems" / problem_id
    tasks = {
        "inside-loop-state": problem / "inside-loop-state",
        "post-loop-state": problem / "post-loop-state",
    }
    source_paths = {
        "inside": tasks["inside-loop-state"] / "program.cpp",
        "post": tasks["post-loop-state"] / "program.cpp",
    }
    sources = {key: path.read_text() for key, path in source_paths.items()}
    execution_sources = {
        "inside-loop-state": "inside",
        "post-loop-state": "post",
    }
    original_path = problem / "long-trace-final/program.cpp"
    original_sha256 = sha256_bytes(original_path.read_bytes())
    if original_sha256 != existing["source_sha256"]:
        raise RuntimeError(
            f"clean source changed for {problem_id}; a full remeasurement is required"
        )

    standard = selection["compiler_standard"]
    with tempfile.TemporaryDirectory(prefix=f"state-profiles-{problem_id}-") as temporary:
        directory = Path(temporary)
        line_shifts, transform_notes = run_container_measurement(
            problem_id,
            standard,
            {key: (source_paths[key], sources[key]) for key in source_paths},
            {
                label: (execution_sources[label], task)
                for label, task in tasks.items()
            },
            directory,
            repetitions,
        )
        ast_profiles = {}
        for source_key in source_paths:
            root, source_map = load_ast(
                source_paths[source_key],
                sources[source_key],
                directory / f"{source_key}-ast.json",
            )
            ast_profiles[source_key] = (
                root,
                source_map,
                collect_function_bodies(root, source_map),
            )
        run_state_measurement(
            problem_id,
            standard,
            {key: (source_paths[key], sources[key]) for key in source_paths},
            ast_profiles,
            {
                label: (execution_sources[label], task)
                for label, task in tasks.items()
            },
            directory,
            repetitions,
        )

        static_profiles: dict[str, dict[str, Any]] = {}
        for source_key in source_paths:
            _, source_map, functions = ast_profiles[source_key]
            control = static_control_metrics(functions, source_map)
            static_profiles[source_key] = {
                "cyclomatic_complexity": control["cyclomatic_complexity"],
                "source_sha256": sha256_bytes(source_paths[source_key].read_bytes()),
            }

        dynamic: dict[str, dict[str, Any]] = {}
        for label, task in tasks.items():
            source_key = execution_sources[label]
            dynamic_root, dynamic_source_map, dynamic_functions = ast_profiles[
                source_key
            ]
            observed = []
            for repetition in range(1, repetitions + 1):
                coverage = load_coverage(
                    directory / f"{label}-{repetition}.coverage.json",
                    line_shifts[source_key],
                    source_key,
                    sources[source_key],
                )
                state_size, state_load, state_observation_count = load_state_metrics(
                    directory / f"{label}-{repetition}.state.result"
                )
                observed.append(
                    dynamic_profile(
                        dynamic_root,
                        dynamic_functions,
                        dynamic_source_map,
                        coverage,
                        state_size,
                        state_load,
                        state_observation_count,
                    )
                )
            if observed[1:] != observed[:-1]:
                raise RuntimeError(
                    f"nondeterministic dynamic complexity for {problem_id}/{label}: "
                    f"{observed}"
                )
            dynamic[label] = {
                **observed[0],
                "input_sha256": sha256_bytes((task / "input.txt").read_bytes()),
                "source_sha256": sha256_bytes(source_paths[source_key].read_bytes()),
                "repeated_measurements": repetitions,
            }

        clang_version = (directory / "clang-version.txt").read_text().strip()
        llvm_cov_version = (directory / "llvm-cov-version.txt").read_text().strip()

    updated = json.loads(json.dumps(existing))
    updated["static_profiles"].update(static_profiles)
    updated["dynamic"].update(dynamic)
    updated["execution_compatibility_transform"].update(transform_notes)
    updated["tools"] = {
        "clang": clang_version,
        "llvm_cov": llvm_cov_version,
    }
    updated["plain_english_profile"] = complexity_note(
        updated["static"], updated["dynamic"]["long-trace-final"]
    )
    print(f"Refreshed state profiles for {problem_id}", flush=True)
    return updated


def refresh_state_profiles(
    document: dict[str, Any], problem_ids: list[str], repetitions: int
) -> dict[str, Any]:
    selections = {
        item["problem_id"]: item
        for item in json.loads((EXPERIMENT / "cases.json").read_text())
    }
    requested = set(problem_ids)
    unknown = requested - set(selections)
    if unknown:
        raise RuntimeError(f"unknown problem IDs: {sorted(unknown)}")
    existing = {program["problem_id"]: program for program in document["programs"]}
    missing = requested - set(existing)
    if missing:
        raise RuntimeError(f"missing committed profiles: {sorted(missing)}")

    workers = max(1, int(os.environ.get("COMPLEXITY_WORKERS", "1")))
    ordered = [selections[problem_id] for problem_id in problem_ids]
    with ThreadPoolExecutor(max_workers=workers) as executor:
        refreshed = list(
            executor.map(
                lambda item: refresh_state_profiles_problem(
                    item, existing[item["problem_id"]], repetitions
                ),
                ordered,
            )
        )
    replacements = {program["problem_id"]: program for program in refreshed}
    programs = [
        replacements.get(program["problem_id"], program)
        for program in document["programs"]
    ]
    programs.sort(key=lambda row: (-row["rating"], row["problem_id"]))

    clang_versions = {program["tools"]["clang"] for program in refreshed}
    coverage_versions = {program["tools"]["llvm_cov"] for program in refreshed}
    if len(clang_versions) != 1 or len(coverage_versions) != 1:
        raise RuntimeError("compiler tool versions changed during measurement")
    if next(iter(clang_versions)) != document["tools"]["ast_and_lexer"]:
        raise RuntimeError("Clang version differs from the committed measurement set")
    if next(iter(coverage_versions)) != document["tools"]["coverage"]:
        raise RuntimeError("llvm-cov version differs from the committed measurement set")

    updated = dict(document)
    updated["tools"] = {
        **document["tools"],
        "adapter_sha256": sha256_bytes(Path(__file__).read_bytes()),
    }
    updated["programs"] = programs
    return updated


def write_retained_report(document: dict[str, Any], path: Path) -> None:
    """Write the human report for the retained complexity fields."""
    programs = document["programs"]
    lines = [
        "# Complexity measurements",
        "",
        "This experiment retains the repository's four separate complexity dimensions. Metric names, formulas, units, and interpretation are defined in the [shared metric definitions](../../../../shared/metrics/README.md).",
        "",
        "## Omega_CC",
        "",
        "| Program | Original | Inside-loop | Post-loop |",
        "| --- | ---: | ---: | ---: |",
    ]
    for program in programs:
        profiles = program["static_profiles"]
        lines.append(
            f"| {program['problem_id'].split('-', 2)[-1].upper()} | "
            f"{profiles['original']['cyclomatic_complexity']} | "
            f"{profiles['inside']['cyclomatic_complexity']} | "
            f"{profiles['post']['cyclomatic_complexity']} |"
        )
    for metric, field in (
        ("Omega_hat_NativeTrace", "native_trace_length"),
        ("Omega_hat_StateSize", "state_size"),
        ("Omega_hat_StateLoad", "state_load"),
    ):
        lines.extend(
            [
                "",
                f"## {metric}",
                "",
                "| Program | Short-trace final | Long-trace final | Inside-loop state | Post-loop state |",
                "| --- | ---: | ---: | ---: | ---: |",
            ]
        )
        for program in programs:
            values = program["dynamic"]
            lines.append(
                f"| {program['problem_id'].split('-', 2)[-1].upper()} | "
                f"{values['short-trace-final'][field]:,} | "
                f"{values['long-trace-final'][field]:,} | "
                f"{values['inside-loop-state'][field]:,} | "
                f"{values['post-loop-state'][field]:,} |"
            )
    lines.extend(
        [
            "",
            "## Method",
            "",
            "Each runtime profile was measured three times and required identical metrics plus byte-exact oracle output. For the two abrupt state arms, the measurement-only copy replaces the final `std::_Exit(0)` with `std::exit(0)` after the same oracle write so LLVM and state reporters can flush; execution up to the checkpoint is unchanged. NativeTrace excludes library internals and inserted checkpoint-counter lines. StateSize recursively counts supported scalars, aggregates, strings, arrays, and container elements; shared compound objects are counted once, while instrumentation and runtime internals are excluded. StateLoad sums that same reachable-value count over the complete StateSize observation series.",
            "",
            "## Files",
            "",
            "- `profiles.json`: authoritative retained profiles and arm mappings.",
            "- `static-profiles.csv`: Omega_CC for every byte-distinct source profile.",
            "- `dynamic-profiles.csv`: NativeTrace, StateSize, and StateLoad for every independent execution.",
            "- `arm-profile-map.csv`: arm-to-source and arm-to-execution mappings.",
            "- `measure.py`: deterministic measurement generator.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def write_measurement_csvs(
    document: dict[str, Any], static_path: Path, dynamic_path: Path, arm_map_path: Path
) -> None:
    static_path.parent.mkdir(parents=True, exist_ok=True)
    with static_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=(
                "problem_id",
                "profile",
                "source_sha256",
                "Omega_CC",
            ),
        )
        writer.writeheader()
        for program in document["programs"]:
            for profile_name in ("original", "inside", "post"):
                profile = program["static_profiles"][profile_name]
                writer.writerow(
                    {
                        "problem_id": program["problem_id"],
                        "profile": profile_name,
                        "source_sha256": profile["source_sha256"],
                        "Omega_CC": profile["cyclomatic_complexity"],
                    }
                )

    with dynamic_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=(
                "problem_id",
                "profile",
                "source_sha256",
                "input_sha256",
                "Omega_hat_NativeTrace",
                "Omega_hat_StateSize",
                "Omega_hat_StateLoad",
                "state_observation_count",
                "measurement_status",
                "repetitions",
            ),
        )
        writer.writeheader()
        for program in document["programs"]:
            for profile_name in (
                "short-trace-final",
                "long-trace-final",
                "inside-loop-state",
                "post-loop-state",
            ):
                profile = program["dynamic"][profile_name]
                writer.writerow(
                    {
                        "problem_id": program["problem_id"],
                        "profile": profile_name,
                        "source_sha256": profile["source_sha256"],
                        "input_sha256": profile["input_sha256"],
                        "Omega_hat_NativeTrace": profile["native_trace_length"],
                        "Omega_hat_StateSize": profile["state_size"],
                        "Omega_hat_StateLoad": profile["state_load"],
                        "state_observation_count": profile["state_observation_count"],
                        "measurement_status": profile["state_measurement_status"],
                        "repetitions": profile["repeated_measurements"],
                    }
                )

    with arm_map_path.open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            lineterminator="\n",
            fieldnames=(
                "problem_id",
                "arm",
                "static_profile",
                "source_input_execution_profile",
                "prediction_target_profile",
            ),
        )
        writer.writeheader()
        for program in document["programs"]:
            for arm, mapping in program["arm_profiles"].items():
                writer.writerow(
                    {
                        "problem_id": program["problem_id"],
                        "arm": arm,
                        **mapping,
                    }
                )


def retain_four_metrics(document: dict[str, Any]) -> dict[str, Any]:
    """Drop superseded fields without re-executing unchanged measurements."""
    retained = dict(document)
    retained["schema"] = "codecontests-complexity-profile-v4-four-metrics"
    retained["tools"] = {
        **document["tools"],
        "adapter_sha256": sha256_bytes(Path(__file__).read_bytes()),
    }
    retained["metric_names"] = {
        "cyclomatic_complexity": "Omega_CC",
        "native_trace_length": "Omega_hat_NativeTrace",
        "state_size": "Omega_hat_StateSize",
        "state_load": "Omega_hat_StateLoad",
    }
    retained_programs = []
    for source_program in document["programs"]:
        program = dict(source_program)
        program["static_profiles"] = {
            profile_name: {
                "cyclomatic_complexity": profile["cyclomatic_complexity"],
                "source_sha256": profile["source_sha256"],
            }
            for profile_name, profile in source_program["static_profiles"].items()
        }
        program["static"] = {
            "cyclomatic_complexity": source_program["static"]["cyclomatic_complexity"]
        }
        program["dynamic"] = {
            profile_name: {
                key: profile[key]
                for key in (
                    "native_trace_length",
                    "state_size",
                    "state_load",
                    "state_observation_count",
                    "state_measurement_status",
                    "input_sha256",
                    "source_sha256",
                    "repeated_measurements",
                )
            }
            for profile_name, profile in source_program["dynamic"].items()
        }
        program["plain_english_profile"] = complexity_note(
            program["static"], program["dynamic"]["long-trace-final"]
        )
        retained_programs.append(program)
    retained["programs"] = retained_programs
    return retained


def backfill_state_load_problem(
    selection: dict[str, Any],
    existing: dict[str, Any],
    repetitions: int,
) -> dict[str, Any]:
    """Rerun only the state observer and preserve static and NativeTrace data."""
    problem_id = selection["problem_id"]
    problem = EXPERIMENT / "problems" / problem_id
    tasks = {
        "short-trace-final": problem / "short-trace-final",
        "long-trace-final": problem / "long-trace-final",
        "inside-loop-state": problem / "inside-loop-state",
        "post-loop-state": problem / "post-loop-state",
    }
    source_paths = {
        "original": tasks["long-trace-final"] / "program.cpp",
        "inside": tasks["inside-loop-state"] / "program.cpp",
        "post": tasks["post-loop-state"] / "program.cpp",
    }
    sources = {key: path.read_text() for key, path in source_paths.items()}
    execution_sources = {
        "short-trace-final": "original",
        "long-trace-final": "original",
        "inside-loop-state": "inside",
        "post-loop-state": "post",
    }
    standard = selection["compiler_standard"]
    with tempfile.TemporaryDirectory(prefix=f"state-load-{problem_id}-") as temporary:
        directory = Path(temporary)
        clang_version = run_ast_measurement(
            standard,
            {key: (source_paths[key], sources[key]) for key in source_paths},
            directory,
        )
        ast_profiles = {}
        for source_key in source_paths:
            root, source_map = load_ast(
                source_paths[source_key],
                sources[source_key],
                directory / f"{source_key}-ast.json",
            )
            ast_profiles[source_key] = (
                root,
                source_map,
                collect_function_bodies(root, source_map),
            )
        run_state_measurement(
            problem_id,
            standard,
            {key: (source_paths[key], sources[key]) for key in source_paths},
            ast_profiles,
            {label: (execution_sources[label], task) for label, task in tasks.items()},
            directory,
            repetitions,
        )
        updated = json.loads(json.dumps(existing))
        for label in tasks:
            observed = [
                load_state_metrics(directory / f"{label}-{repetition}.state.result")
                for repetition in range(1, repetitions + 1)
            ]
            if observed[1:] != observed[:-1]:
                raise RuntimeError(
                    f"nondeterministic state load for {problem_id}/{label}: {observed}"
                )
            peak, state_load, observation_count = observed[0]
            previous_peak = int(updated["dynamic"][label]["state_size"])
            if peak != previous_peak:
                raise RuntimeError(
                    f"StateSize changed for {problem_id}/{label}: "
                    f"committed={previous_peak}, rerun={peak}"
                )
            updated["dynamic"][label]["state_load"] = state_load
            updated["dynamic"][label]["state_observation_count"] = observation_count
            updated["dynamic"][label]["repeated_measurements"] = repetitions
        updated["tools"]["clang"] = clang_version
        updated["plain_english_profile"] = complexity_note(
            updated["static"], updated["dynamic"]["long-trace-final"]
        )
        print(f"Measured StateLoad for {problem_id}", flush=True)
        return updated


def backfill_state_load(document: dict[str, Any], repetitions: int) -> dict[str, Any]:
    selection = json.loads((EXPERIMENT / "cases.json").read_text())
    existing = {program["problem_id"]: program for program in document["programs"]}
    if set(existing) != {item["problem_id"] for item in selection}:
        raise RuntimeError("Committed profiles do not match cases.json")
    workers = max(1, int(os.environ.get("COMPLEXITY_WORKERS", "1")))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        programs = list(
            executor.map(
                lambda item: backfill_state_load_problem(
                    item, existing[item["problem_id"]], repetitions
                ),
                selection,
            )
        )
    programs.sort(key=lambda row: (-row["rating"], row["problem_id"]))
    updated = dict(document)
    updated["schema"] = SCHEMA
    updated["skill"] = {
        "name": "measure-program-complexity",
        "version": SKILL_VERSION,
        "path": "shared/metrics/README.md",
    }
    updated["metric_names"] = {
        "cyclomatic_complexity": "Omega_CC",
        "native_trace_length": "Omega_hat_NativeTrace",
        "state_size": "Omega_hat_StateSize",
        "state_load": "Omega_hat_StateLoad",
    }
    updated["dynamic_adapter_version"] = DYNAMIC_ADAPTER_VERSION
    updated["tools"] = {
        **updated["tools"],
        "adapter_sha256": sha256_bytes(Path(__file__).read_bytes()),
    }
    updated["state_adapter"] = {
        "path": str(STATE_RUNTIME.relative_to(REPOSITORY)),
        "sha256": sha256_bytes(STATE_RUNTIME.read_bytes()),
        "observation": "incremental observation after binding or supported-container state changes",
        "state_load_aggregation": "sum of the reachable-value count over the same complete observation series used for StateSize",
    }
    updated["programs"] = programs
    return updated


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--static-csv", type=Path, default=DEFAULT_STATIC_CSV)
    parser.add_argument("--dynamic-csv", type=Path, default=DEFAULT_DYNAMIC_CSV)
    parser.add_argument("--arm-map-csv", type=Path, default=DEFAULT_ARM_MAP_CSV)
    parser.add_argument("--repetitions", type=int, default=3)
    parser.add_argument(
        "--reuse-retained-measurements",
        action="store_true",
        help="prune the committed exact measurements to the retained fields without rerunning C++ programs",
    )
    parser.add_argument(
        "--state-load-backfill",
        action="store_true",
        help="rerun only state observation and add StateLoad while preserving committed static and NativeTrace measurements",
    )
    parser.add_argument(
        "--refresh-state-profiles",
        action="store_true",
        help="remeasure only changed inside-loop and post-loop state profiles",
    )
    parser.add_argument(
        "--problem",
        action="append",
        default=[],
        help="problem ID to refresh; repeat once per problem",
    )
    arguments = parser.parse_args()
    if arguments.repetitions < 1:
        raise SystemExit("--repetitions must be positive")

    if arguments.reuse_retained_measurements:
        document = retain_four_metrics(json.loads(arguments.output.read_text()))
        write_retained_report(document, arguments.report)
        write_measurement_csvs(
            document,
            arguments.static_csv,
            arguments.dynamic_csv,
            arguments.arm_map_csv,
        )
        arguments.output.write_text(json.dumps(document, indent=2) + "\n")
        return

    if arguments.state_load_backfill:
        document = backfill_state_load(
            json.loads(arguments.output.read_text()), arguments.repetitions
        )
        write_retained_report(document, arguments.report)
        write_measurement_csvs(
            document,
            arguments.static_csv,
            arguments.dynamic_csv,
            arguments.arm_map_csv,
        )
        arguments.output.write_text(json.dumps(document, indent=2) + "\n")
        return

    if arguments.refresh_state_profiles:
        if not arguments.problem:
            raise SystemExit("--refresh-state-profiles requires at least one --problem")
        document = refresh_state_profiles(
            json.loads(arguments.output.read_text()),
            arguments.problem,
            arguments.repetitions,
        )
        write_retained_report(document, arguments.report)
        write_measurement_csvs(
            document,
            arguments.static_csv,
            arguments.dynamic_csv,
            arguments.arm_map_csv,
        )
        arguments.output.write_text(json.dumps(document, indent=2) + "\n")
        return

    selection = json.loads((EXPERIMENT / "cases.json").read_text())
    programs = []
    for index, item in enumerate(selection, 1):
        measured = measure_problem(item, arguments.repetitions)
        programs.append(measured)
        print(f"{index:02d}/{len(selection)} {item['problem_id']}", flush=True)

    programs.sort(key=lambda row: (-row["rating"], row["problem_id"]))
    clang_versions = {program["tools"]["clang"] for program in programs}
    coverage_versions = {program["tools"]["llvm_cov"] for program in programs}
    if len(clang_versions) != 1 or len(coverage_versions) != 1:
        raise RuntimeError("compiler tool versions changed during measurement")
    clang_version = next(iter(clang_versions))
    llvm_cov_version = next(iter(coverage_versions))
    document = {
        "schema": SCHEMA,
        "skill": {
            "name": "measure-program-complexity",
            "version": SKILL_VERSION,
            "path": "shared/metrics/README.md",
        },
        "benchmark": "CodeContests reasoning and state prediction-arm benchmark",
        "program_count": len(programs),
        "measured_scope": "Exact clean and instrumented sources plus all four canonical execution profiles",
        "tools": {
            "container_image": DOCKER_IMAGE,
            "container_platform": DOCKER_PLATFORM,
            "network": "disabled",
            "root_filesystem": "read-only",
            "ast_and_lexer": clang_version,
            "coverage": llvm_cov_version,
            "adapter_sha256": sha256_bytes(Path(__file__).read_bytes()),
        },
        "metric_names": {
            "cyclomatic_complexity": "Omega_CC",
            "native_trace_length": "Omega_hat_NativeTrace",
            "state_size": "Omega_hat_StateSize",
            "state_load": "Omega_hat_StateLoad",
        },
        "dynamic_adapter_version": DYNAMIC_ADAPTER_VERSION,
        "state_adapter": {
            "path": str(STATE_RUNTIME.relative_to(REPOSITORY)),
            "sha256": sha256_bytes(STATE_RUNTIME.read_bytes()),
            "observation": "incremental observation after binding or supported-container state changes",
        },
        "programs": programs,
    }
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.report.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(json.dumps(document, indent=2) + "\n")
    write_retained_report(document, arguments.report)
    write_measurement_csvs(
        document,
        arguments.static_csv,
        arguments.dynamic_csv,
        arguments.arm_map_csv,
    )
    print(f"Wrote {arguments.output}")
    print(f"Wrote {arguments.report}")
    print(f"Wrote {arguments.static_csv}")
    print(f"Wrote {arguments.dynamic_csv}")
    print(f"Wrote {arguments.arm_map_csv}")


if __name__ == "__main__":
    main()
