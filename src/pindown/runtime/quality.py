"""Filters that decide which generated tests are allowed to count.

Three kinds of test come back from a model and must not survive into the
delivered suite:

Vacuous tests, which call the code and assert nothing. They raise coverage and
kill no mutants, so they cost the user review time and buy nothing.

Failing tests, which contradict current behavior. A characterization suite exists
to record what the code does today, so a failing test is either a mistake or a
bug report - and in both cases it is not a characterization test.

Order-dependent and non-deterministic tests, which pass once and then fail in CI
next week. These are the expensive ones, because they teach a team to distrust
the suite. Catching them costs a handful of subprocess runs here and saves the
argument later.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass, field

from pindown.config import Budget
from pindown.models import PytestResult
from pindown.runtime.pytest_runner import run_suite

ASSERT_METHOD_PREFIX = "assert"


@dataclass
class TestUnit:
    name: str
    start: int
    end: int
    node: ast.FunctionDef | ast.AsyncFunctionDef


@dataclass
class FilterOutcome:
    source: str
    kept: list[str] = field(default_factory=list)
    discarded: list[str] = field(default_factory=list)
    fatal: str | None = None
    final_result: PytestResult | None = None

    @property
    def n_tests(self) -> int:
        return len(self.kept)


def _is_test_class(node: ast.ClassDef) -> bool:
    """Would pytest collect tests from this class?

    Two rules, matching pytest's own: a class named `Test*`, or a
    `unittest.TestCase` subclass regardless of its name. Checking only the name
    undercounts real suites -- xmltodict's tests live in `XMLToDictTestCase`, and
    reporting that file as containing zero tests is a quietly wrong number in the
    results table.
    """
    if node.name.startswith("Test"):
        return True
    for base in node.bases:
        name = base.attr if isinstance(base, ast.Attribute) else getattr(base, "id", "")
        if "TestCase" in name:
            return True
    return False


def find_tests(source: str) -> list[TestUnit]:
    """Every test pytest would collect from this file."""
    tree = ast.parse(source)
    units: list[TestUnit] = []

    def add(node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        start = node.lineno
        if node.decorator_list:
            start = min(start, min(d.lineno for d in node.decorator_list))
        units.append(TestUnit(node.name, start, node.end_lineno or node.lineno, node))

    for node in tree.body:
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name.startswith("test"):
            add(node)
        elif isinstance(node, ast.ClassDef) and _is_test_class(node):
            for sub in node.body:
                if isinstance(sub, ast.FunctionDef | ast.AsyncFunctionDef) and sub.name.startswith(
                    "test"
                ):
                    add(sub)

    return units


def is_vacuous(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """True when the body can never fail on a wrong value.

    An `assert`, a `pytest.raises` block, or a unittest-style `assertX` call all
    count as a real check. Anything else is a test that only proves the code did
    not crash, which every mutant that returns a wrong answer will also survive.
    """
    for child in ast.walk(node):
        if isinstance(child, ast.Assert):
            return False
        if isinstance(child, ast.With | ast.AsyncWith):
            for item in child.items:
                call = item.context_expr
                if isinstance(call, ast.Call):
                    fn = call.func
                    name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", "")
                    if name in {"raises", "warns", "deprecated_call"}:
                        return False
        if isinstance(child, ast.Call):
            fn = child.func
            if isinstance(fn, ast.Attribute) and fn.attr.startswith(ASSERT_METHOD_PREFIX):
                return False
    return True


def count_tests(source: str) -> int:
    try:
        return len(find_tests(source))
    except SyntaxError:
        return 0


def remove_tests(source: str, names: set[str]) -> str:
    """Drop the named tests, preferring line surgery so formatting survives.

    Falls back to an AST rewrite if the line-based removal produces something
    that will not parse, which can happen with unusual decorator layouts. The
    fallback loses comments, so it is a last resort rather than the default.
    """
    if not names:
        return source

    units = find_tests(source)
    targets = [u for u in units if u.name in names]
    if not targets:
        return source

    lines = source.splitlines(keepends=True)
    for unit in sorted(targets, key=lambda u: u.start, reverse=True):
        del lines[unit.start - 1 : unit.end]
    candidate = "".join(lines)

    try:
        tree = ast.parse(candidate)
    except SyntaxError:
        return _remove_via_ast(source, names)

    # A class whose tests were all removed is now an empty body.
    if _has_empty_class(tree):
        return _remove_via_ast(source, names)
    return candidate


def _has_empty_class(tree: ast.Module) -> bool:
    return any(isinstance(n, ast.ClassDef) and not n.body for n in ast.walk(tree))


def _remove_via_ast(source: str, names: set[str]) -> str:
    tree = ast.parse(source)

    def keep(node: ast.stmt) -> bool:
        return not (
            isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.name in names
        )

    new_body: list[ast.stmt] = []
    for node in tree.body:
        if not keep(node):
            continue
        if isinstance(node, ast.ClassDef):
            node.body = [s for s in node.body if keep(s)]
            if not node.body:
                continue
        new_body.append(node)

    tree.body = new_body
    return ast.unparse(tree)


def filter_suite(
    module_name: str,
    module_source: str,
    test_source: str,
    budget: Budget,
    isolation: bool = True,
) -> FilterOutcome:
    """Reduce a proposed suite to the tests that actually earn their place."""
    try:
        units = find_tests(test_source)
    except SyntaxError as exc:
        return FilterOutcome(source="", fatal=f"generated file does not parse: {exc}")

    if not units:
        return FilterOutcome(source="", fatal="no test functions found")

    discarded: list[str] = []
    source = test_source

    vacuous = {u.name for u in units if is_vacuous(u.node)}
    if vacuous:
        discarded += [f"{n}: asserts nothing" for n in sorted(vacuous)]
        source = remove_tests(source, vacuous)
        if not find_tests(source):
            return FilterOutcome(source="", discarded=discarded, fatal="every test was vacuous")

    # Failing tests do not describe current behavior. Two rounds, because
    # removing one failure sometimes reveals another that it masked.
    result = run_suite(module_name, module_source, source, budget.pytest_timeout_s)
    for _ in range(2):
        if result.collection_error:
            return FilterOutcome(
                source="",
                discarded=discarded,
                fatal=f"suite fails at import: {result.stdout[-600:]}",
                final_result=result,
            )
        if result.ok or not result.failed_tests:
            break
        failing = set(result.failed_tests)
        discarded += [f"{n}: fails against current behavior" for n in sorted(failing)]
        source = remove_tests(source, failing)
        if not find_tests(source):
            return FilterOutcome(
                source="", discarded=discarded, fatal="every test failed against current behavior"
            )
        result = run_suite(module_name, module_source, source, budget.pytest_timeout_s)

    if not result.usable:
        return FilterOutcome(
            source="",
            discarded=discarded,
            fatal=f"suite still not green after pruning failures: {result.stdout[-600:]}",
            final_result=result,
        )

    # Vary the hash seed. Anything that iterates a set or dict and depends on the
    # order will flip here, and nowhere else.
    unstable: set[str] = set()
    for seed in range(1, budget.flake_reruns + 1):
        rerun = run_suite(module_name, module_source, source, budget.pytest_timeout_s, hash_seed=seed)
        unstable |= set(rerun.failed_tests)
        if rerun.collection_error:
            return FilterOutcome(
                source="", discarded=discarded, fatal="suite import is not deterministic"
            )

    if unstable:
        discarded += [f"{n}: not deterministic across hash seeds" for n in sorted(unstable)]
        source = remove_tests(source, unstable)
        if not find_tests(source):
            return FilterOutcome(source="", discarded=discarded, fatal="every test was flaky")

    # Run each test alone. A test that needs a sibling to have run first is a
    # trap: it passes today and fails the moment someone reorders the file.
    if isolation:
        dependent: set[str] = set()
        for unit in find_tests(source):
            alone = run_suite(
                module_name,
                module_source,
                source,
                budget.pytest_timeout_s,
                node_id=unit.name,
            )
            if not alone.ok:
                dependent.add(unit.name)
        if dependent:
            discarded += [f"{n}: only passes when run after another test" for n in sorted(dependent)]
            source = remove_tests(source, dependent)
            if not find_tests(source):
                return FilterOutcome(
                    source="", discarded=discarded, fatal="every test was order dependent"
                )

    final = run_suite(module_name, module_source, source, budget.pytest_timeout_s)
    if not final.usable:
        return FilterOutcome(
            source="", discarded=discarded, fatal="suite not green after filtering", final_result=final
        )

    return FilterOutcome(
        source=source,
        kept=[u.name for u in find_tests(source)],
        discarded=discarded,
        final_result=final,
    )
