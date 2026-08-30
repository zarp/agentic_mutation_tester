"""Tests for the filters that decide which generated tests are allowed to count.

These run real subprocesses against a real toy module, because the thing being
tested is exactly the behavior that only appears when the code actually executes.
"""

from __future__ import annotations

from pindown.agent.merge import merge_suites
from pindown.config import Budget
from pindown.runtime.quality import count_tests, filter_suite, find_tests, is_vacuous, remove_tests

MODULE = '''
def double(n):
    return n * 2


def label(n):
    if n < 0:
        return "negative"
    return "non-negative"
'''

FAST_BUDGET = Budget(flake_reruns=2, pytest_timeout_s=20.0)


def _names(source: str) -> set[str]:
    return {u.name for u in find_tests(source)}


def test_vacuous_test_is_detected():
    source = "import m\n\ndef test_nothing():\n    m.double(2)\n"
    unit = find_tests(source)[0]
    assert is_vacuous(unit.node)


def test_assertion_makes_a_test_not_vacuous():
    source = "import m\n\ndef test_value():\n    assert m.double(2) == 4\n"
    assert not is_vacuous(find_tests(source)[0].node)


def test_pytest_raises_counts_as_a_check():
    source = (
        "import pytest\nimport m\n\n"
        "def test_raises():\n    with pytest.raises(TypeError):\n        m.double(None)\n"
    )
    assert not is_vacuous(find_tests(source)[0].node)


def test_remove_tests_preserves_the_rest_of_the_file():
    source = (
        "import m\n\n"
        "HELPER = 3\n\n"
        "def test_one():\n    assert m.double(1) == 2\n\n"
        "def test_two():\n    assert m.double(2) == 4\n"
    )
    trimmed = remove_tests(source, {"test_one"})
    assert _names(trimmed) == {"test_two"}
    assert "HELPER = 3" in trimmed
    assert "import m" in trimmed


def test_filter_drops_the_vacuous_test_and_keeps_the_real_one():
    suite = (
        "import module_under_test as m\n\n"
        "def test_real():\n    assert m.double(3) == 6\n\n"
        "def test_vacuous():\n    m.double(3)\n"
    )
    outcome = filter_suite("module_under_test", MODULE, suite, FAST_BUDGET, isolation=False)
    assert outcome.fatal is None
    assert outcome.kept == ["test_real"]
    assert any("asserts nothing" in d for d in outcome.discarded)


def test_filter_drops_a_test_that_contradicts_current_behavior():
    suite = (
        "import module_under_test as m\n\n"
        "def test_true():\n    assert m.label(-1) == 'negative'\n\n"
        "def test_wrong():\n    assert m.label(-1) == 'positive'\n"
    )
    outcome = filter_suite("module_under_test", MODULE, suite, FAST_BUDGET, isolation=False)
    assert outcome.kept == ["test_true"]
    assert any("fails against current behavior" in d for d in outcome.discarded)


def test_filter_drops_an_order_dependent_test():
    # `test_b` only passes because `test_a` populated the shared list first.
    suite = (
        "import module_under_test as m\n\n"
        "SEEN = []\n\n"
        "def test_a():\n    SEEN.append(m.double(1))\n    assert SEEN == [2]\n\n"
        "def test_b():\n    assert SEEN == [2]\n"
    )
    outcome = filter_suite("module_under_test", MODULE, suite, FAST_BUDGET, isolation=True)
    assert outcome.kept == ["test_a"]
    assert any("only passes when run after another test" in d for d in outcome.discarded)


def test_filter_reports_a_suite_that_will_not_import():
    suite = "import nonexistent_dependency\n\ndef test_x():\n    assert True\n"
    outcome = filter_suite("module_under_test", MODULE, suite, FAST_BUDGET, isolation=False)
    assert outcome.fatal is not None
    assert outcome.source == ""


def test_filter_reports_a_file_that_does_not_parse():
    outcome = filter_suite("module_under_test", MODULE, "def test_(:\n", FAST_BUDGET)
    assert outcome.fatal is not None
    assert "does not parse" in outcome.fatal


def test_merge_skips_duplicate_test_names():
    existing = "import m\n\ndef test_one():\n    assert m.double(1) == 2\n"
    addition = (
        "import m\n\n"
        "def test_one():\n    assert False\n\n"
        "def test_two():\n    assert m.double(2) == 4\n"
    )
    merged, skipped = merge_suites(existing, addition)
    assert skipped == ["test_one"]
    assert _names(merged) == {"test_one", "test_two"}
    assert "assert False" not in merged


def test_merge_does_not_duplicate_an_existing_import():
    existing = "import m\n\ndef test_one():\n    assert m.double(1) == 2\n"
    merged, _ = merge_suites(existing, "import m\n\ndef test_two():\n    assert m.double(2) == 4\n")
    assert merged.count("import m") == 1


def test_count_tests_survives_a_broken_file():
    assert count_tests("def test_(:") == 0
