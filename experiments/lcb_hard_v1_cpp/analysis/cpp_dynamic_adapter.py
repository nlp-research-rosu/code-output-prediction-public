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

EXPERIMENT = Path(__file__).resolve().parents[1]
REPOSITORY = EXPERIMENT.parents[1]
STATE_RUNTIME = EXPERIMENT / "measurements/program-complexity/state_runtime.hpp"
SUPPORT_INCLUDE = EXPERIMENT / "measurements/program-complexity/support/include"
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
    namespace_imports = (
        "using std::max;\n"
        if re.search(r"template\s*<[^>]+>\s*auto\s+max\s*\(", source)
        else ""
    )
    prefix = "".join(includes) + AST_PREFIX + namespace_imports
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


def macro_expanded_range(node: dict[str, Any]) -> bool:
    measured_range = node.get("range")
    if not isinstance(measured_range, dict):
        return False
    return any(
        isinstance(measured_range.get(endpoint), dict)
        and "expansionLoc" in measured_range[endpoint]
        for endpoint in ("begin", "end")
    )


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
    del problem_id
    return source, 0, None


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
        is_pack = bool(node.get("isParameterPack"))
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

    def visit(
        node: dict[str, Any],
        parent: dict[str, Any] | None = None,
        inside_constexpr: bool = False,
    ) -> None:
        inside_constexpr = inside_constexpr or (
            node.get("kind") in FUNCTION_KINDS
            and bool(node.get("constexpr") or node.get("consteval"))
        )
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
        if function is not None and not inside_constexpr:
            measured = source_range(node, source_map)
            if measured is not None:
                insert(measured[0] + 1, next_guard(list(function.parameters)))

        if (
            not inside_constexpr
            and node.get("kind") == "DeclStmt"
            and explicit_node(node, source_map)
        ):
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
                    insertion_point = measured[1]
                    if macro_expanded_range(node):
                        semicolon = source_bytes.find(b";", insertion_point)
                        if semicolon < 0:
                            raise RuntimeError(
                                "could not locate macro declaration terminator"
                            )
                        insertion_point = semicolon + 1
                    insert(insertion_point, next_guard(declarations))

        if not inside_constexpr and node.get("kind") in {
            "ForStmt",
            "CXXForRangeStmt",
        }:
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
            visit(child, node, inside_constexpr)

    visit(root)
    for offset, declarations in sorted(global_groups.items()):
        insert(offset, next_guard(declarations))
    first_include = re.search(r"^[ \t]*#include[^\n]*\n", source, re.MULTILINE)
    if first_include is None:
        raise RuntimeError("state adapter requires an include line")
    state_header = repository_container_path(STATE_RUNTIME)
    insert(first_include.end(), f'#include "{state_header}"\n')

    data = source_bytes
    for offset in sorted(insertions, reverse=True):
        addition = "".join(insertions[offset]).encode()
        data = data[:offset] + addition + data[offset:]
    return data.decode().replace("std::_Exit(0);", "std::exit(0);")


def repository_container_path(path: Path) -> str:
    return "/repo/" + path.resolve().relative_to(REPOSITORY.resolve()).as_posix()


def support_include_flag() -> str:
    return f"-I{shlex.quote(repository_container_path(SUPPORT_INCLUDE))}"


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
    include_flag = support_include_flag()
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
                f"clang++ {include_flag} -std={shlex.quote(standard)} -Wno-return-type -fsyntax-only "
                f"-Xclang -ast-dump=json -Xclang -ast-dump-filter={AST_NAMESPACE} "
                f"/work/{source_key}-ast-wrapper.cpp > /work/{source_key}-ast.json",
                f"clang++ {include_flag} -std={shlex.quote(standard)} -O2 -fprofile-instr-generate "
                f"-fcoverage-mapping /work/{source_key}-program.cpp "
                f"-o /work/{source_key}-program",
            ]
        )
        source_in_container = repository_container_path(source_path)
        commands.append(
            f"clang++ {include_flag} -std={shlex.quote(standard)} -Xclang -dump-raw-tokens "
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
    include_flag = support_include_flag()
    for source_key, (_, source) in sources.items():
        wrapped, _ = wrapped_source(source)
        (directory / f"{source_key}-ast-wrapper.cpp").write_text(wrapped)
        commands.append(
            f"clang++ {include_flag} -std={shlex.quote(standard)} -Wno-return-type -fsyntax-only "
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
    include_flag = support_include_flag()
    for source_key, (_, source) in sources.items():
        root, source_map, _ = ast_profiles[source_key]
        instrumented = state_instrumented_source(root, source_map)
        instrumented, _, _ = compatible_execution_source(problem_id, instrumented)
        (directory / f"{source_key}-state.cpp").write_text(instrumented)
        commands.append(
            f"clang++ {include_flag} -std={shlex.quote(standard)} -O2 "
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
