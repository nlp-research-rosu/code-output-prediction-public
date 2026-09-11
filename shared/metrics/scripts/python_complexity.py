"""Canonical Python source adapter for the retained Omega_CC metric."""

from __future__ import annotations

import ast


class CyclomaticVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.decisions = 0

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        self.decisions += max(0, len(node.values) - 1)
        self.generic_visit(node)

    def visit_If(self, node: ast.If) -> None:
        self.decisions += 1
        self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        self.decisions += 1
        self.generic_visit(node)

    def _visit_loop(self, node: ast.For | ast.AsyncFor | ast.While) -> None:
        self.decisions += 1
        self.generic_visit(node)

    visit_For = _visit_loop
    visit_AsyncFor = _visit_loop
    visit_While = _visit_loop

    def _visit_comprehension(self, node: ast.AST) -> None:
        for generator in node.generators:
            self.decisions += 1 + len(generator.ifs)
        self.generic_visit(node)

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
        for case in node.cases:
            irrefutable = (
                isinstance(case.pattern, ast.MatchAs)
                and case.pattern.pattern is None
                and case.pattern.name is None
                and case.guard is None
            )
            if not irrefutable:
                self.decisions += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        self.decisions += 1
        self.generic_visit(node)


def measure_python_static(source: str) -> dict[str, int]:
    """Return the single retained static metric for exact Python source bytes."""
    visitor = CyclomaticVisitor()
    visitor.visit(ast.parse(source))
    return {"Omega_CC": 1 + visitor.decisions}
