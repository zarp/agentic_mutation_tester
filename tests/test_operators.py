"""Tests for the mutation engine.

Every number this project reports comes out of this code, so it is the one place
where a quiet bug would invalidate the whole result rather than just degrade it.
The negative cases matter more than the positive ones: a mutator that silently
generates zero mutants for a construct makes every suite look better than it is.
"""

from __future__ import annotations

import ast

import pytest

from pindown.mutation.operators import build_mutants, collect_sites

SAMPLE = '''
"""Module docstring, which must never be mutated."""

THRESHOLD = 10


def clamp(value, low, high):
    """Docstring, also never mutated."""
    if value < low:
        return low
    if value > high:
        return high
    return value


def label(n):
    if n > 0 and n < THRESHOLD:
        return "small"
    if not n:
        return "zero"
    return "large"


def total(items):
    running = 0
    for item in items:
        if item is None:
            continue
        running += item
    return running


if __name__ == "__main__":
    print(clamp(1, 2, 3))
'''


def _by_operator(source: str) -> dict[str, list]:
    out: dict[str, list] = {}
    for site in collect_sites(source):
        out.setdefault(site.operator, []).append(site)
    return out


def test_every_mutant_is_valid_python():
    for mutant in build_mutants(SAMPLE):
        ast.parse(mutant.source)


def test_every_mutant_actually_differs_from_the_original():
    original = ast.unparse(ast.parse(SAMPLE))
    for mutant in build_mutants(SAMPLE):
        assert mutant.source != original, f"{mutant.id} changed nothing"


def test_mutant_ids_are_unique():
    mutants = build_mutants(SAMPLE)
    assert len({m.id for m in mutants}) == len(mutants)


def test_generation_is_deterministic():
    first = [(m.id, m.source) for m in build_mutants(SAMPLE)]
    second = [(m.id, m.source) for m in build_mutants(SAMPLE)]
    assert first == second


def test_comparison_operators_are_swapped():
    descriptions = [s.description for s in _by_operator(SAMPLE)["comparison"]]
    assert "comparison `<` -> `<=`" in descriptions
    assert "comparison `>` -> `>=`" in descriptions
    assert "comparison `is` -> `is not`" in descriptions


def test_boolean_and_negation_operators():
    ops = _by_operator(SAMPLE)
    assert any("`and` -> `or`" in s.description for s in ops["boolean"])
    assert any("removed `not`" in s.description for s in ops["negation"])


def test_return_and_control_flow_operators():
    ops = _by_operator(SAMPLE)
    assert ops["return"], "no return-value mutants generated"
    assert any("`continue` -> `break`" in s.description for s in ops["control"])


def test_augmented_assignment_is_mutated():
    ops = _by_operator(SAMPLE)
    assert any("augmented assign `+=` -> `-=`" in s.description for s in ops["arithmetic"])


def test_docstrings_are_never_mutated():
    for mutant in build_mutants(SAMPLE):
        tree = ast.parse(mutant.source)
        assert ast.get_docstring(tree) == "Module docstring, which must never be mutated."


def test_main_guard_is_never_mutated():
    # The guarded block is unreachable under pytest, so a mutant there can only
    # ever survive. Including them would depress every arm's score with noise.
    for mutant in build_mutants(SAMPLE):
        assert 'print(clamp(1, 2, 3))' in mutant.source


def test_string_constants_are_mutated_but_kept_valid():
    string_sites = [
        s for s in _by_operator(SAMPLE)["constant"] if "string" in s.description
    ]
    assert string_sites, "string constants produced no mutants"


def test_return_none_is_not_mutated_to_return_none():
    source = "def f():\n    return None\n"
    assert not [s for s in collect_sites(source) if s.operator == "return"]


def test_limit_samples_across_the_file_rather_than_truncating():
    mutants = build_mutants(SAMPLE, limit=5)
    assert len(mutants) == 5
    linenos = [m.lineno for m in mutants]
    all_linenos = [m.lineno for m in build_mutants(SAMPLE)]
    # A truncating implementation would only ever return the top of the file.
    assert max(linenos) > (min(all_linenos) + max(all_linenos)) / 2


def test_limit_is_stable_across_calls():
    first = [m.id for m in build_mutants(SAMPLE, limit=7)]
    second = [m.id for m in build_mutants(SAMPLE, limit=7)]
    assert first == second


@pytest.mark.parametrize(
    "source",
    [
        "x = 1\n",
        "def f(a, b):\n    return a @ b\n",
        "async def f():\n    return 1\n",
        "class A:\n    x: int = 1\n",
        "def f():\n    yield 1\n",
        "f = lambda x: x + 1\n",
        "def f(x):\n    return [i for i in x if i > 0]\n",
        "def f(x):\n    return {k: v for k, v in x}\n",
        "def f(x):\n    match x:\n        case 1:\n            return 2\n        case _:\n            return 3\n",
    ],
)
def test_unusual_constructs_do_not_crash_the_mutator(source):
    for mutant in build_mutants(source):
        ast.parse(mutant.source)


def test_empty_module_produces_no_mutants():
    assert build_mutants("") == []
