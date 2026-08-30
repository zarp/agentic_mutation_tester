"""AST mutation operators.

A mutant is one single-point change to the module under test. If the test suite
still passes with that change in place, the suite cannot detect that behavior,
and the mutant survives.

Two properties matter more than operator coverage here:

Determinism. Every mutant gets an id derived from its node's position in a
pre-order walk, not from generation order. The same source always produces the
same mutant set with the same ids, so survivor sets from different runs and
different arms are directly comparable.

Validity. Mutations are applied to the AST and unparsed, so a mutant is always
syntactically valid Python. There is no "failed to compile" category to argue
about when reporting the score.
"""

from __future__ import annotations

import ast
import copy
from collections.abc import Callable
from dataclasses import dataclass

from pindown.models import Mutant

COMPARE_SWAP: dict[type[ast.cmpop], type[ast.cmpop]] = {
    ast.Lt: ast.LtE,
    ast.LtE: ast.Lt,
    ast.Gt: ast.GtE,
    ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq,
    ast.NotEq: ast.Eq,
    ast.Is: ast.IsNot,
    ast.IsNot: ast.Is,
    ast.In: ast.NotIn,
    ast.NotIn: ast.In,
}

BINOP_SWAP: dict[type[ast.operator], type[ast.operator]] = {
    ast.Add: ast.Sub,
    ast.Sub: ast.Add,
    ast.Mult: ast.Div,
    ast.Div: ast.Mult,
    ast.FloorDiv: ast.Div,
    ast.Mod: ast.Mult,
    ast.Pow: ast.Mult,
    ast.LShift: ast.RShift,
    ast.RShift: ast.LShift,
    ast.BitAnd: ast.BitOr,
    ast.BitOr: ast.BitAnd,
    ast.BitXor: ast.BitAnd,
}

BOOLOP_SWAP: dict[type[ast.boolop], type[ast.boolop]] = {
    ast.And: ast.Or,
    ast.Or: ast.And,
}

SYMBOL: dict[type[ast.AST], str] = {
    ast.Lt: "<",
    ast.LtE: "<=",
    ast.Gt: ">",
    ast.GtE: ">=",
    ast.Eq: "==",
    ast.NotEq: "!=",
    ast.Is: "is",
    ast.IsNot: "is not",
    ast.In: "in",
    ast.NotIn: "not in",
    ast.Add: "+",
    ast.Sub: "-",
    ast.Mult: "*",
    ast.Div: "/",
    ast.FloorDiv: "//",
    ast.Mod: "%",
    ast.Pow: "**",
    ast.LShift: "<<",
    ast.RShift: ">>",
    ast.BitAnd: "&",
    ast.BitOr: "|",
    ast.BitXor: "^",
    ast.And: "and",
    ast.Or: "or",
}


@dataclass
class Site:
    """A place where exactly one mutation can be applied."""

    index: int
    sub: int
    operator: str
    description: str
    lineno: int
    apply: Callable[[ast.AST], ast.AST]

    @property
    def id(self) -> str:
        return f"m{self.index:05d}.{self.sub}-{self.operator}"


def _walk_indexed(tree: ast.AST):
    """Pre-order walk yielding (index, node).

    The order must match `_Applier` exactly. Both rely on `ast.iter_child_nodes`
    field ordering, which is what `NodeTransformer.generic_visit` also uses.
    """
    counter = 0

    def rec(node: ast.AST):
        nonlocal counter
        idx = counter
        counter += 1
        yield idx, node
        for child in ast.iter_child_nodes(node):
            yield from rec(child)

    yield from rec(tree)


class _Applier(ast.NodeTransformer):
    """Applies a single mutation at a target pre-order index."""

    def __init__(self, target: int, fn: Callable[[ast.AST], ast.AST]) -> None:
        self.target = target
        self.fn = fn
        self.counter = 0
        self.applied = False

    def visit(self, node: ast.AST) -> ast.AST:
        idx = self.counter
        self.counter += 1
        if idx == self.target:
            self.applied = True
            # Do not descend: indices past this point are irrelevant once the
            # single mutation has landed.
            return self.fn(node)
        return self.generic_visit(node)


def _docstring_nodes(tree: ast.AST) -> set[int]:
    """Ids of Constant nodes that are docstrings. Mutating prose proves nothing."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            body = getattr(node, "body", [])
            if (
                body
                and isinstance(body[0], ast.Expr)
                and isinstance(body[0].value, ast.Constant)
                and isinstance(body[0].value.value, str)
            ):
                out.add(id(body[0].value))
    return out


def _main_guard_nodes(tree: ast.AST) -> set[int]:
    """Ids of every node under `if __name__ == "__main__":`, which tests never run."""
    out: set[int] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (
            isinstance(test, ast.Compare)
            and isinstance(test.left, ast.Name)
            and test.left.id == "__name__"
        ):
            for child in ast.walk(node):
                out.add(id(child))
    return out


def collect_sites(source: str) -> list[Site]:
    """Every mutation site in `source`, in deterministic order."""
    tree = ast.parse(source)
    skip = _docstring_nodes(tree) | _main_guard_nodes(tree)
    sites: list[Site] = []

    for index, node in _walk_indexed(tree):
        if id(node) in skip:
            continue
        lineno = getattr(node, "lineno", 0)

        if isinstance(node, ast.Compare):
            for i, op in enumerate(node.ops):
                new_type = COMPARE_SWAP.get(type(op))
                if new_type is None:
                    continue
                desc = f"comparison `{SYMBOL[type(op)]}` -> `{SYMBOL[new_type]}`"
                sites.append(
                    Site(index, i, "comparison", desc, lineno, _swap_compare(i, new_type))
                )

        elif isinstance(node, ast.BinOp):
            new_type = BINOP_SWAP.get(type(node.op))
            if new_type is not None:
                desc = f"operator `{SYMBOL[type(node.op)]}` -> `{SYMBOL[new_type]}`"
                sites.append(Site(index, 0, "arithmetic", desc, lineno, _swap_binop(new_type)))

        elif isinstance(node, ast.AugAssign):
            new_type = BINOP_SWAP.get(type(node.op))
            if new_type is not None:
                desc = f"augmented assign `{SYMBOL[type(node.op)]}=` -> `{SYMBOL[new_type]}=`"
                sites.append(Site(index, 0, "arithmetic", desc, lineno, _swap_binop(new_type)))

        elif isinstance(node, ast.BoolOp):
            new_type = BOOLOP_SWAP[type(node.op)]
            desc = f"`{SYMBOL[type(node.op)]}` -> `{SYMBOL[new_type]}`"
            sites.append(Site(index, 0, "boolean", desc, lineno, _swap_boolop(new_type)))

        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            sites.append(Site(index, 0, "negation", "removed `not`", lineno, _drop_unary))

        elif isinstance(node, ast.Return) and node.value is not None:
            if not (isinstance(node.value, ast.Constant) and node.value.value is None):
                sites.append(
                    Site(index, 0, "return", "return value replaced with `None`", lineno, _return_none)
                )

        elif isinstance(node, ast.Break):
            sites.append(Site(index, 0, "control", "`break` -> `continue`", lineno, _to_continue))

        elif isinstance(node, ast.Continue):
            sites.append(Site(index, 0, "control", "`continue` -> `break`", lineno, _to_break))

        elif isinstance(node, ast.Constant):
            site = _constant_site(index, node, lineno)
            if site is not None:
                sites.append(site)

    return sites


def _swap_compare(pos: int, new_type: type[ast.cmpop]) -> Callable[[ast.AST], ast.AST]:
    def fn(node: ast.AST) -> ast.AST:
        assert isinstance(node, ast.Compare)
        node.ops[pos] = new_type()
        return node

    return fn


def _swap_binop(new_type: type[ast.operator]) -> Callable[[ast.AST], ast.AST]:
    def fn(node: ast.AST) -> ast.AST:
        node.op = new_type()  # type: ignore[attr-defined]
        return node

    return fn


def _swap_boolop(new_type: type[ast.boolop]) -> Callable[[ast.AST], ast.AST]:
    def fn(node: ast.AST) -> ast.AST:
        node.op = new_type()  # type: ignore[attr-defined]
        return node

    return fn


def _drop_unary(node: ast.AST) -> ast.AST:
    assert isinstance(node, ast.UnaryOp)
    return node.operand


def _return_none(node: ast.AST) -> ast.AST:
    return ast.Return(value=ast.Constant(value=None))


def _to_continue(node: ast.AST) -> ast.AST:
    return ast.Continue()


def _to_break(node: ast.AST) -> ast.AST:
    return ast.Break()


def _constant_site(index: int, node: ast.Constant, lineno: int) -> Site | None:
    value = node.value

    if isinstance(value, bool):
        new = not value
        return Site(index, 0, "constant", f"`{value}` -> `{new}`", lineno, _set_constant(new))

    if isinstance(value, int):
        new_int = value + 1
        return Site(index, 0, "constant", f"`{value}` -> `{new_int}`", lineno, _set_constant(new_int))

    if isinstance(value, float):
        new_float = value + 1.0
        return Site(
            index, 0, "constant", f"`{value}` -> `{new_float}`", lineno, _set_constant(new_float)
        )

    if isinstance(value, str):
        new_str = "XX" + value + "XX"
        shown = value if len(value) <= 20 else value[:20] + "..."
        return Site(
            index,
            0,
            "constant",
            f"string `{shown!r}` -> `'XX...XX'`",
            lineno,
            _set_constant(new_str),
        )

    return None


def _set_constant(new_value: object) -> Callable[[ast.AST], ast.AST]:
    def fn(node: ast.AST) -> ast.AST:
        return ast.Constant(value=new_value)

    return fn


def build_mutants(source: str, limit: int | None = None) -> list[Mutant]:
    """Generate mutants from `source`.

    When `limit` is set and there are more sites than that, sites are sampled by
    a fixed stride rather than randomly or by truncation. Truncation would only
    ever mutate the top of the file; a stride keeps the sample spread across the
    module and is identical on every run.
    """
    sites = collect_sites(source)
    if limit is not None and len(sites) > limit:
        stride = len(sites) / limit
        sites = [sites[int(i * stride)] for i in range(limit)]

    tree = ast.parse(source)
    lines = source.splitlines()
    mutants: list[Mutant] = []

    for site in sites:
        mutated_tree = _Applier(site.index, site.apply).visit(copy.deepcopy(tree))
        ast.fix_missing_locations(mutated_tree)
        original_line = lines[site.lineno - 1] if 0 < site.lineno <= len(lines) else ""
        mutants.append(
            Mutant(
                id=site.id,
                operator=site.operator,
                lineno=site.lineno,
                description=site.description,
                original_line=original_line,
                source=ast.unparse(mutated_tree),
            )
        )

    return mutants
