from __future__ import annotations

import ast
import io
import keyword
import math
import tokenize
from dataclasses import dataclass, field
from typing import Iterable

GROUPING_PUNCTUATION = {"(", ")", "[", "]", "{", "}", ",", ":", ";", "."}
LITERAL_KEYWORDS = {"True", "False", "None"}


def target_count(node: ast.AST) -> int:
    if isinstance(node, (ast.Tuple, ast.List)):
        return sum(target_count(child) for child in node.elts)
    if isinstance(node, ast.Starred):
        return target_count(node.value)
    if isinstance(node, (ast.Name, ast.Attribute, ast.Subscript)):
        return 1
    return 0


def target_uses_reserved_lcb_name(node: ast.AST) -> bool:
    names = [child.id for child in ast.walk(node) if isinstance(child, ast.Name)]
    return bool(names) and all(name.startswith("_lcb_") for name in names)


def expression_uses_reserved_lcb_name(node: ast.AST) -> bool:
    return any(
        child.id.startswith("_lcb_")
        for child in ast.walk(node)
        if isinstance(child, ast.Name)
    )


def pattern_names(pattern: ast.pattern) -> list[str]:
    names: list[str] = []
    for node in ast.walk(pattern):
        if isinstance(node, ast.MatchAs) and node.name is not None:
            names.append(node.name)
        elif isinstance(node, ast.MatchStar) and node.name is not None:
            names.append(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest is not None:
            names.append(node.rest)
    return names


class PythonControlShape(ast.NodeVisitor):
    def __init__(self) -> None:
        self.decisions = 0
        self.if_depth = 0
        self.loop_depth = 0
        self.max_if_depth = 0
        self.max_loop_depth = 0

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.decisions += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def _visit_if(self, node: ast.If, is_elif: bool) -> None:
        self.decisions += 1
        self.visit(node.test)
        previous = self.if_depth
        if not is_elif:
            self.if_depth += 1
            self.max_if_depth = max(self.max_if_depth, self.if_depth)
        for child in node.body:
            self.visit(child)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            self._visit_if(node.orelse[0], True)
        else:
            for child in node.orelse:
                self.visit(child)
        self.if_depth = previous

    def visit_If(self, node: ast.If) -> None:
        self._visit_if(node, False)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.decisions += 1
        previous = self.if_depth
        self.if_depth += 1
        self.max_if_depth = max(self.max_if_depth, self.if_depth)
        self.generic_visit(node)
        self.if_depth = previous

    def _visit_loop(self, node: ast.For | ast.AsyncFor | ast.While) -> None:
        self.decisions += 1
        if isinstance(node, (ast.For, ast.AsyncFor)):
            self.visit(node.iter)
            self.visit(node.target)
        else:
            self.visit(node.test)
        previous = self.loop_depth
        self.loop_depth += 1
        self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
        for child in node.body:
            self.visit(child)
        self.loop_depth = previous
        for child in node.orelse:
            self.visit(child)

    visit_For = _visit_loop
    visit_AsyncFor = _visit_loop
    visit_While = _visit_loop

    def _visit_comprehension(self, node: ast.AST) -> None:
        previous_if = self.if_depth
        previous_loop = self.loop_depth
        for generator in node.generators:
            self.visit(generator.iter)
            self.decisions += 1
            self.loop_depth += 1
            self.max_loop_depth = max(self.max_loop_depth, self.loop_depth)
            self.visit(generator.target)
            for condition in generator.ifs:
                self.decisions += 1
                self.if_depth += 1
                self.max_if_depth = max(self.max_if_depth, self.if_depth)
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.if_depth = previous_if
        self.loop_depth = previous_loop

    visit_ListComp = _visit_comprehension
    visit_SetComp = _visit_comprehension
    visit_GeneratorExp = _visit_comprehension
    visit_DictComp = _visit_comprehension

    def visit_Try(self, node: ast.Try) -> None:
        self.decisions += len(node.handlers)
        self.generic_visit(node)

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self.visit_Try(node)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        previous = self.if_depth
        self.if_depth += 1
        self.max_if_depth = max(self.max_if_depth, self.if_depth)
        for case in node.cases:
            irrefutable = (
                isinstance(case.pattern, ast.MatchAs)
                and case.pattern.pattern is None
                and case.pattern.name is None
                and case.guard is None
            )
            if not irrefutable:
                self.decisions += 1
            if case.guard is not None:
                self.visit(case.guard)
            for child in case.body:
                self.visit(child)
        self.if_depth = previous

    def visit_Assert(self, node: ast.Assert) -> None:
        self.decisions += 1
        self.generic_visit(node)

    def _visit_new_scope(self, body: Iterable[ast.stmt]) -> None:
        previous_if = self.if_depth
        previous_loop = self.loop_depth
        self.if_depth = 0
        self.loop_depth = 0
        for child in body:
            self.visit(child)
        self.if_depth = previous_if
        self.loop_depth = previous_loop

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        for child in node.decorator_list:
            self.visit(child)
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        self._visit_new_scope(node.body)

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.decorator_list + node.bases:
            self.visit(child)
        for keyword_node in node.keywords:
            self.visit(keyword_node.value)
        self._visit_new_scope(node.body)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        self._visit_new_scope([ast.Expr(value=node.body)])


@dataclass(eq=False)
class PythonScope:
    uid: int
    kind: str
    parent: PythonScope | None
    locals: set[str] = field(default_factory=set)
    globals: set[str] = field(default_factory=set)
    nonlocals: set[str] = field(default_factory=set)
    parameters: set[str] = field(default_factory=set)
    binding_kinds: dict[str, set[str]] = field(default_factory=dict)


Symbol = tuple[int, str]


class PythonScopeModel(ast.NodeVisitor):
    def __init__(self, tree: ast.Module) -> None:
        self.next_uid = 1
        self.module = PythonScope(0, "module", None)
        self.current = self.module
        self.scope_nodes: dict[int, PythonScope] = {id(tree): self.module}
        self.visit(tree)
        self._finalize(self.module)

    def _finalize(self, scope: PythonScope) -> None:
        scope.locals.difference_update(scope.globals)
        scope.locals.difference_update(scope.nonlocals)
        for child in set(self.scope_nodes.values()):
            if child.parent is scope:
                self._finalize(child)

    def child_scope(self, node: ast.AST, kind: str) -> PythonScope:
        scope = PythonScope(self.next_uid, kind, self.current)
        self.next_uid += 1
        self.scope_nodes[id(node)] = scope
        return scope

    def bind(self, name: str, kind: str) -> None:
        target = self.current
        if name in self.current.globals:
            target = self.module
        elif name in self.current.nonlocals:
            parent = self.current.parent
            while parent is not None:
                if parent.kind != "class" and name in parent.locals:
                    target = parent
                    break
                parent = parent.parent
        target.locals.add(name)
        target.binding_kinds.setdefault(name, set()).add(kind)

    def visit_Global(self, node: ast.Global) -> None:
        self.current.globals.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.current.nonlocals.update(node.names)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            self.bind(node.id, "assignment")

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.bind(alias.asname or alias.name.split(".")[0], "import")

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name != "*":
                self.bind(alias.asname or alias.name, "import")

    def _parameters(self, arguments: ast.arguments) -> set[str]:
        values = (
            arguments.posonlyargs
            + arguments.args
            + arguments.kwonlyargs
            + ([arguments.vararg] if arguments.vararg else [])
            + ([arguments.kwarg] if arguments.kwarg else [])
        )
        return {argument.arg for argument in values}

    def _visit_outer_function_parts(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef
    ) -> None:
        for child in node.decorator_list:
            self.visit(child)
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        for argument in (
            node.args.posonlyargs
            + node.args.args
            + node.args.kwonlyargs
            + ([node.args.vararg] if node.args.vararg else [])
            + ([node.args.kwarg] if node.args.kwarg else [])
        ):
            if argument.annotation is not None:
                self.visit(argument.annotation)
        if node.returns is not None:
            self.visit(node.returns)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self._visit_outer_function_parts(node)
        self.bind(node.name, "function")
        parent = self.current
        scope = self.child_scope(node, "function")
        scope.parameters = self._parameters(node.args)
        scope.locals.update(scope.parameters)
        for name in scope.parameters:
            scope.binding_kinds.setdefault(name, set()).add("parameter")
        self.current = scope
        for child in node.body:
            self.visit(child)
        self.current = parent

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        parent = self.current
        scope = self.child_scope(node, "lambda")
        scope.parameters = self._parameters(node.args)
        scope.locals.update(scope.parameters)
        for name in scope.parameters:
            scope.binding_kinds.setdefault(name, set()).add("parameter")
        self.current = scope
        self.visit(node.body)
        self.current = parent

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.decorator_list + node.bases:
            self.visit(child)
        for keyword_node in node.keywords:
            self.visit(keyword_node.value)
        self.bind(node.name, "class")
        parent = self.current
        self.current = self.child_scope(node, "class")
        for child in node.body:
            self.visit(child)
        self.current = parent

    def _visit_comprehension(self, node: ast.AST) -> None:
        self.visit(node.generators[0].iter)
        parent = self.current
        self.current = self.child_scope(node, "comprehension")
        for index, generator in enumerate(node.generators):
            if index:
                self.visit(generator.iter)
            self.visit(generator.target)
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.current = parent

    visit_ListComp = _visit_comprehension
    visit_SetComp = _visit_comprehension
    visit_GeneratorExp = _visit_comprehension
    visit_DictComp = _visit_comprehension

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is not None:
            self.visit(node.type)
        if node.name is not None:
            self.bind(node.name, "assignment")
        for child in node.body:
            self.visit(child)

    def visit_Match(self, node: ast.Match) -> None:
        self.visit(node.subject)
        for case in node.cases:
            for name in pattern_names(case.pattern):
                self.bind(name, "assignment")
            if case.guard is not None:
                self.visit(case.guard)
            for child in case.body:
                self.visit(child)

    def resolve(self, scope: PythonScope, name: str) -> Symbol | None:
        if name in scope.globals:
            return (self.module.uid, name) if name in self.module.locals else None
        if name in scope.nonlocals:
            parent = scope.parent
            while parent is not None:
                if parent.kind != "class" and name in parent.locals:
                    return (parent.uid, name)
                parent = parent.parent
            return None
        if name in scope.locals:
            return (scope.uid, name)
        parent = scope.parent
        while parent is not None:
            if parent.kind != "class" and name in parent.locals:
                return (parent.uid, name)
            parent = parent.parent
        return None

    def scope_by_uid(self, uid: int) -> PythonScope:
        for scope in set(self.scope_nodes.values()):
            if scope.uid == uid:
                return scope
        raise KeyError(uid)

    def is_variable(self, symbol: Symbol) -> bool:
        scope = self.scope_by_uid(symbol[0])
        kinds = scope.binding_kinds.get(symbol[1], set())
        return bool(kinds - {"function", "class", "import"})


class PythonUseCounter(ast.NodeVisitor):
    def __init__(self, model: PythonScopeModel, tree: ast.Module) -> None:
        self.model = model
        self.scope = model.module
        self.uses = 0
        self.visit(tree)

    def visit_Name(self, node: ast.Name) -> None:
        if isinstance(node.ctx, ast.Load):
            symbol = self.model.resolve(self.scope, node.id)
            if symbol is not None and self.model.is_variable(symbol):
                self.uses += 1

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        for child in node.decorator_list:
            self.visit(child)
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        previous = self.scope
        self.scope = self.model.scope_nodes[id(node)]
        for child in node.body:
            self.visit(child)
        self.scope = previous

    visit_FunctionDef = _visit_function
    visit_AsyncFunctionDef = _visit_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        for child in node.decorator_list + node.bases:
            self.visit(child)
        for keyword_node in node.keywords:
            self.visit(keyword_node.value)
        previous = self.scope
        self.scope = self.model.scope_nodes[id(node)]
        for child in node.body:
            self.visit(child)
        self.scope = previous

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for child in node.args.defaults + node.args.kw_defaults:
            if child is not None:
                self.visit(child)
        previous = self.scope
        self.scope = self.model.scope_nodes[id(node)]
        self.visit(node.body)
        self.scope = previous

    def _visit_comprehension(self, node: ast.AST) -> None:
        self.visit(node.generators[0].iter)
        previous = self.scope
        self.scope = self.model.scope_nodes[id(node)]
        for index, generator in enumerate(node.generators):
            if index:
                self.visit(generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        if isinstance(node, ast.DictComp):
            self.visit(node.key)
            self.visit(node.value)
        else:
            self.visit(node.elt)
        self.scope = previous

    visit_ListComp = _visit_comprehension
    visit_SetComp = _visit_comprehension
    visit_GeneratorExp = _visit_comprehension
    visit_DictComp = _visit_comprehension

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        if isinstance(node.target, ast.Name):
            symbol = self.model.resolve(self.scope, node.target.id)
            if symbol is not None and self.model.is_variable(symbol):
                self.uses += 1
        else:
            self.visit(node.target)
        self.visit(node.value)


class PythonRedefinitionCounter:
    def __init__(self, model: PythonScopeModel, tree: ast.Module) -> None:
        self.model = model
        self.redefinitions: set[tuple[int, Symbol]] = set()
        self.analyzed_scopes: set[int] = set()
        self.process_scope(tree, model.module)

    def bind_name(
        self,
        name: str,
        marker: int,
        scope: PythonScope,
        state: set[Symbol],
        repeated: bool,
    ) -> set[Symbol]:
        symbol = self.model.resolve(scope, name)
        if symbol is None:
            if name in scope.globals:
                symbol = (self.model.module.uid, name)
            elif name in scope.nonlocals:
                return state
            else:
                symbol = (scope.uid, name)
        if self.model.is_variable(symbol) and (symbol in state or repeated):
            self.redefinitions.add((marker, symbol))
        return state | {symbol}

    def bind_target(
        self,
        node: ast.AST,
        scope: PythonScope,
        state: set[Symbol],
        repeated: bool,
    ) -> set[Symbol]:
        if isinstance(node, ast.Name):
            return self.bind_name(node.id, id(node), scope, state, repeated)
        if isinstance(node, (ast.Tuple, ast.List)):
            for child in node.elts:
                state = self.bind_target(child, scope, state, repeated)
            return state
        if isinstance(node, ast.Starred):
            return self.bind_target(node.value, scope, state, repeated)
        return self.process_expression(node, scope, state, repeated)

    def process_expression(
        self,
        node: ast.AST | None,
        scope: PythonScope,
        state: set[Symbol],
        repeated: bool,
    ) -> set[Symbol]:
        if node is None:
            return state
        if isinstance(node, ast.NamedExpr):
            state = self.process_expression(node.value, scope, state, repeated)
            return self.bind_target(node.target, scope, state, repeated)
        if isinstance(node, ast.IfExp):
            tested = self.process_expression(node.test, scope, state, repeated)
            left = self.process_expression(node.body, scope, set(tested), repeated)
            right = self.process_expression(node.orelse, scope, set(tested), repeated)
            return left | right
        if isinstance(node, ast.BoolOp):
            result = set(state)
            current = set(state)
            for value in node.values:
                current = self.process_expression(value, scope, current, repeated)
                result |= current
            return result
        if isinstance(
            node, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)
        ):
            state = self.process_expression(
                node.generators[0].iter, scope, state, repeated
            )
            child = self.model.scope_nodes[id(node)]
            self.process_comprehension(node, child)
            return state
        for child in ast.iter_child_nodes(node):
            state = self.process_expression(child, scope, state, repeated)
        return state

    def process_comprehension(self, node: ast.AST, scope: PythonScope) -> None:
        if scope.uid in self.analyzed_scopes:
            return
        self.analyzed_scopes.add(scope.uid)
        state: set[Symbol] = set()
        for index, generator in enumerate(node.generators):
            if index:
                state = self.process_expression(generator.iter, scope, state, True)
            state = self.bind_target(generator.target, scope, state, True)
            for condition in generator.ifs:
                state = self.process_expression(condition, scope, state, True)
        if isinstance(node, ast.DictComp):
            state = self.process_expression(node.key, scope, state, True)
            self.process_expression(node.value, scope, state, True)
        else:
            self.process_expression(node.elt, scope, state, True)

    def process_scope(self, node: ast.AST, scope: PythonScope) -> None:
        if scope.uid in self.analyzed_scopes:
            return
        self.analyzed_scopes.add(scope.uid)
        initial = {(scope.uid, name) for name in scope.parameters}
        for name in scope.globals:
            symbol = self.model.resolve(scope, name)
            if symbol is not None:
                initial.add(symbol)
        for name in scope.nonlocals:
            symbol = self.model.resolve(scope, name)
            if symbol is not None:
                initial.add(symbol)
        body = (
            node.body
            if isinstance(
                node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            )
            else []
        )
        self.process_block(body, scope, initial, False)

    def process_block(
        self,
        body: Iterable[ast.stmt],
        scope: PythonScope,
        state: set[Symbol],
        repeated: bool,
    ) -> set[Symbol]:
        current = set(state)
        for node in body:
            current = self.process_statement(node, scope, current, repeated)
        return current

    def process_statement(
        self,
        node: ast.stmt,
        scope: PythonScope,
        state: set[Symbol],
        repeated: bool,
    ) -> set[Symbol]:
        if isinstance(node, ast.Assign):
            state = self.process_expression(node.value, scope, state, repeated)
            for target in node.targets:
                state = self.bind_target(target, scope, state, repeated)
            return state
        if isinstance(node, ast.AnnAssign):
            state = self.process_expression(node.annotation, scope, state, repeated)
            state = self.process_expression(node.value, scope, state, repeated)
            if node.value is not None:
                state = self.bind_target(node.target, scope, state, repeated)
            return state
        if isinstance(node, ast.AugAssign):
            state = self.process_expression(node.target, scope, state, repeated)
            state = self.process_expression(node.value, scope, state, repeated)
            return self.bind_target(node.target, scope, state, repeated)
        if isinstance(node, ast.Expr):
            return self.process_expression(node.value, scope, state, repeated)
        if isinstance(node, ast.If):
            tested = self.process_expression(node.test, scope, state, repeated)
            left = self.process_block(node.body, scope, set(tested), repeated)
            right = self.process_block(node.orelse, scope, set(tested), repeated)
            return left | right
        if isinstance(node, (ast.For, ast.AsyncFor)):
            state = self.process_expression(node.iter, scope, state, repeated)
            loop_state = self.bind_target(node.target, scope, set(state), True)
            loop_state = self.process_block(node.body, scope, loop_state, True)
            after = state | loop_state
            return self.process_block(node.orelse, scope, after, repeated)
        if isinstance(node, ast.While):
            state = self.process_expression(node.test, scope, state, repeated)
            loop_state = self.process_block(node.body, scope, set(state), True)
            after = state | loop_state
            return self.process_block(node.orelse, scope, after, repeated)
        if isinstance(node, (ast.With, ast.AsyncWith)):
            for item in node.items:
                state = self.process_expression(
                    item.context_expr, scope, state, repeated
                )
                if item.optional_vars is not None:
                    state = self.bind_target(item.optional_vars, scope, state, repeated)
            return self.process_block(node.body, scope, state, repeated)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for child in node.decorator_list:
                state = self.process_expression(child, scope, state, repeated)
            for child in node.args.defaults + node.args.kw_defaults:
                state = self.process_expression(child, scope, state, repeated)
            state = self.bind_name(node.name, id(node), scope, state, repeated)
            self.process_scope(node, self.model.scope_nodes[id(node)])
            return state
        if isinstance(node, ast.ClassDef):
            for child in node.decorator_list + node.bases:
                state = self.process_expression(child, scope, state, repeated)
            state = self.bind_name(node.name, id(node), scope, state, repeated)
            self.process_scope(node, self.model.scope_nodes[id(node)])
            return state
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            aliases = node.names
            for alias in aliases:
                if alias.name == "*":
                    continue
                name = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else alias.name
                )
                state = self.bind_name(name, id(alias), scope, state, repeated)
            return state
        if isinstance(node, (ast.Try, ast.TryStar)):
            body_state = self.process_block(node.body, scope, set(state), repeated)
            branches = [body_state]
            for handler in node.handlers:
                handler_state = set(state) | body_state
                if handler.name is not None:
                    handler_state = self.bind_name(
                        handler.name, id(handler), scope, handler_state, repeated
                    )
                branches.append(
                    self.process_block(handler.body, scope, handler_state, repeated)
                )
            merged = set().union(*branches)
            merged = self.process_block(node.orelse, scope, merged, repeated)
            return self.process_block(node.finalbody, scope, merged, repeated)
        if isinstance(node, ast.Match):
            state = self.process_expression(node.subject, scope, state, repeated)
            branches = [set(state)]
            for case in node.cases:
                branch = set(state)
                for name in pattern_names(case.pattern):
                    branch = self.bind_name(
                        name, id(case.pattern), scope, branch, repeated
                    )
                branch = self.process_expression(case.guard, scope, branch, repeated)
                branches.append(self.process_block(case.body, scope, branch, repeated))
            return set().union(*branches)
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.expr):
                state = self.process_expression(child, scope, state, repeated)
        return state


def python_tokens(source: str) -> tuple[list[str], list[str], set[int]]:
    operators: list[str] = []
    operands: list[str] = []
    code_lines: set[int] = set()
    ignored = {
        tokenize.ENCODING,
        tokenize.ENDMARKER,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.NEWLINE,
        tokenize.NL,
        tokenize.COMMENT,
    }
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type not in ignored:
            code_lines.update(range(token.start[0], token.end[0] + 1))
        if token.type in ignored:
            continue
        if token.type == tokenize.NAME:
            if token.string in LITERAL_KEYWORDS:
                operands.append(token.string)
            elif keyword.iskeyword(token.string):
                operators.append(token.string)
            else:
                operands.append(token.string)
        elif token.type in (tokenize.NUMBER, tokenize.STRING):
            operands.append(token.string)
        elif token.type == tokenize.OP and token.string not in GROUPING_PUNCTUATION:
            operators.append(token.string)
    return operators, operands, code_lines


def halstead(operators: list[str], operands: list[str]) -> tuple[float, int]:
    vocabulary = len(set(operators)) + len(set(operands))
    length = len(operators) + len(operands)
    volume = 0.0 if vocabulary <= 1 else length * math.log2(vocabulary)
    return round(volume, 6), vocabulary


def measure_python_static(source: str) -> dict[str, int | float]:
    tree = ast.parse(source)
    shape = PythonControlShape()
    shape.visit(tree)
    scopes = PythonScopeModel(tree)
    uses = PythonUseCounter(scopes, tree).uses
    redefinitions = len(PythonRedefinitionCounter(scopes, tree).redefinitions)
    operators, operands, code_lines = python_tokens(source)
    volume, vocabulary = halstead(operators, operands)
    return {
        "Omega_CC": 1 + shape.decisions,
        "Omega_If": shape.max_if_depth,
        "Omega_Loop": shape.max_loop_depth,
        "Omega_DD": uses + redefinitions,
        "Omega_Loc": len(code_lines),
        "Omega_Vol": volume,
        "Omega_Voc": vocabulary,
    }


class PythonDynamicTransformer(ast.NodeTransformer):
    def __init__(self) -> None:
        self.if_depth = 0
        self.loop_depth = 0

    def assign_call(self, count: int, node: ast.AST) -> ast.Expr:
        return ast.copy_location(
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id="_plsb_measure_assign", ctx=ast.Load()),
                    args=[ast.Constant(count)],
                    keywords=[],
                )
            ),
            node,
        )

    def depth_call(self, name: str, depth: int, node: ast.AST) -> ast.Expr:
        return ast.copy_location(
            ast.Expr(
                value=ast.Call(
                    func=ast.Name(id=name, ctx=ast.Load()),
                    args=[ast.Constant(depth)],
                    keywords=[],
                )
            ),
            node,
        )

    def expression_call(
        self, name: str, arguments: list[ast.expr], node: ast.AST
    ) -> ast.Call:
        return ast.copy_location(
            ast.Call(
                func=ast.Name(id=name, ctx=ast.Load()),
                args=arguments,
                keywords=[],
            ),
            node,
        )

    def visit_Assign(self, node: ast.Assign) -> ast.AST | list[ast.stmt]:
        if all(target_uses_reserved_lcb_name(target) for target in node.targets):
            return node
        node = self.generic_visit(node)
        count = sum(target_count(target) for target in node.targets)
        return [node, self.assign_call(count, node)]

    def visit_AnnAssign(self, node: ast.AnnAssign) -> ast.AST | list[ast.stmt]:
        if target_uses_reserved_lcb_name(node.target):
            return node
        node = self.generic_visit(node)
        if node.value is None:
            return node
        return [node, self.assign_call(target_count(node.target), node)]

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST | list[ast.stmt]:
        if target_uses_reserved_lcb_name(node.target):
            return node
        node = self.generic_visit(node)
        return [node, self.assign_call(target_count(node.target), node)]

    def visit_NamedExpr(self, node: ast.NamedExpr) -> ast.NamedExpr:
        if target_uses_reserved_lcb_name(node.target):
            return node
        node.value = self.visit(node.value)
        node.value = self.expression_call(
            "_plsb_measure_assign_value",
            [ast.Constant(target_count(node.target)), node.value],
            node.value,
        )
        return node

    def _visit_if(self, node: ast.If, is_elif: bool) -> ast.If:
        node.test = self.visit(node.test)
        previous = self.if_depth
        if not is_elif:
            self.if_depth += 1
        depth = self.if_depth
        node.body = self._visit_stmt_list(node.body)
        if len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If):
            node.orelse = [self._visit_if(node.orelse[0], True)]
        else:
            node.orelse = self._visit_stmt_list(node.orelse)
        node.body.insert(0, self.depth_call("_plsb_measure_if", depth, node))
        if node.orelse and not (
            len(node.orelse) == 1 and isinstance(node.orelse[0], ast.If)
        ):
            node.orelse.insert(0, self.depth_call("_plsb_measure_if", depth, node))
        self.if_depth = previous
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        if expression_uses_reserved_lcb_name(node.test):
            return node
        return self._visit_if(node, False)

    def visit_IfExp(self, node: ast.IfExp) -> ast.IfExp:
        previous = self.if_depth
        self.if_depth += 1
        depth = self.if_depth
        test = self.visit(node.test)
        node.test = self.expression_call(
            "_plsb_measure_if_expr", [ast.Constant(depth), test], node.test
        )
        node.body = self.visit(node.body)
        node.orelse = self.visit(node.orelse)
        self.if_depth = previous
        return node

    def _visit_loop(self, node: ast.For | ast.AsyncFor | ast.While) -> ast.AST:
        if isinstance(node, (ast.For, ast.AsyncFor)):
            node.target = self.visit(node.target)
            node.iter = self.visit(node.iter)
            prefix = self.assign_call(target_count(node.target), node)
        else:
            node.test = self.visit(node.test)
            prefix = None
        previous = self.loop_depth
        self.loop_depth += 1
        depth = self.loop_depth
        body = self._visit_stmt_list(node.body)
        self.loop_depth = previous
        if prefix is not None:
            body.insert(0, prefix)
        body.insert(0, self.depth_call("_plsb_measure_loop", depth, node))
        node.body = body
        node.orelse = self._visit_stmt_list(node.orelse)
        return node

    visit_For = _visit_loop
    visit_AsyncFor = _visit_loop
    visit_While = _visit_loop

    def _visit_comprehension(self, node: ast.AST) -> ast.AST:
        previous_if = self.if_depth
        previous_loop = self.loop_depth
        for generator in node.generators:
            generator.iter = self.visit(generator.iter)
            self.loop_depth += 1
            generator.iter = self.expression_call(
                "_plsb_measure_iter",
                [
                    ast.Constant(self.loop_depth),
                    ast.Constant(target_count(generator.target)),
                    generator.iter,
                ],
                generator.iter,
            )
            generator.target = self.visit(generator.target)
            conditions = []
            for condition in generator.ifs:
                self.if_depth += 1
                condition = self.visit(condition)
                conditions.append(
                    self.expression_call(
                        "_plsb_measure_if_filter",
                        [ast.Constant(self.if_depth), condition],
                        condition,
                    )
                )
            generator.ifs = conditions
        if isinstance(node, ast.DictComp):
            node.key = self.visit(node.key)
            node.value = self.visit(node.value)
        else:
            node.elt = self.visit(node.elt)
        self.if_depth = previous_if
        self.loop_depth = previous_loop
        return node

    visit_ListComp = _visit_comprehension
    visit_SetComp = _visit_comprehension
    visit_GeneratorExp = _visit_comprehension
    visit_DictComp = _visit_comprehension

    def visit_With(self, node: ast.With) -> ast.With:
        count = 0
        for item in node.items:
            item.context_expr = self.visit(item.context_expr)
            if item.optional_vars is not None:
                count += target_count(item.optional_vars)
        node.body = self._visit_stmt_list(node.body)
        if count:
            node.body.insert(0, self.assign_call(count, node))
        return node

    visit_AsyncWith = visit_With

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> ast.ExceptHandler:
        if node.type is not None:
            node.type = self.visit(node.type)
        node.body = self._visit_stmt_list(node.body)
        if node.name is not None:
            node.body.insert(0, self.assign_call(1, node))
        return node

    def visit_Match(self, node: ast.Match) -> ast.Match:
        node.subject = self.visit(node.subject)
        previous = self.if_depth
        self.if_depth += 1
        depth = self.if_depth
        for case in node.cases:
            if case.guard is not None:
                case.guard = self.visit(case.guard)
            case.body = self._visit_stmt_list(case.body)
            count = len(pattern_names(case.pattern))
            if count:
                case.body.insert(0, self.assign_call(count, case.pattern))
            case.body.insert(
                0, self.depth_call("_plsb_measure_if", depth, case.pattern)
            )
        self.if_depth = previous
        return node

    def _visit_stmt_list(self, body: list[ast.stmt]) -> list[ast.stmt]:
        result: list[ast.stmt] = []
        for child in body:
            visited = self.visit(child)
            if isinstance(visited, list):
                result.extend(visited)
            elif visited is not None:
                result.append(visited)
        return result

    def _visit_new_scope(self, body: list[ast.stmt]) -> list[ast.stmt]:
        previous_if = self.if_depth
        previous_loop = self.loop_depth
        self.if_depth = 0
        self.loop_depth = 0
        result = self._visit_stmt_list(body)
        self.if_depth = previous_if
        self.loop_depth = previous_loop
        return result

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        node.decorator_list = [self.visit(child) for child in node.decorator_list]
        node.args = self.visit(node.args)
        node.returns = self.visit(node.returns) if node.returns else None
        node.body = self._visit_new_scope(node.body)
        return node

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        node.decorator_list = [self.visit(child) for child in node.decorator_list]
        node.bases = [self.visit(child) for child in node.bases]
        node.keywords = [self.visit(child) for child in node.keywords]
        node.body = self._visit_new_scope(node.body)
        return node

    def visit_Lambda(self, node: ast.Lambda) -> ast.Lambda:
        node.args = self.visit(node.args)
        previous_if = self.if_depth
        previous_loop = self.loop_depth
        self.if_depth = 0
        self.loop_depth = 0
        node.body = self.visit(node.body)
        self.if_depth = previous_if
        self.loop_depth = previous_loop
        return node
