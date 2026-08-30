"""Tests for subprocess execution.

The timeout tests are here because of a real failure: a mutant turned a loop
condition into one that never terminates, the suite hung, and the parent's
attempt to kill it raised PermissionError under a sandbox that denies signals.
That took down an entire campaign. The child now stops itself, and these tests
pin that behavior so it cannot regress.
"""

from __future__ import annotations

from pindown.runtime.pytest_runner import run_suite, suite_detects

MODULE = "def double(n):\n    return n * 2\n"
GOOD_SUITE = "import m\n\ndef test_double():\n    assert m.double(2) == 4\n"


def test_passing_suite_is_usable():
    result = run_suite("m", MODULE, GOOD_SUITE, timeout_s=30.0)
    assert result.usable
    assert result.collected == 1
    assert result.passed == 1


def test_failing_test_is_reported_by_name():
    suite = GOOD_SUITE + "\n\ndef test_wrong():\n    assert m.double(2) == 5\n"
    result = run_suite("m", MODULE, suite, timeout_s=30.0)
    assert not result.ok
    assert result.failed_tests == ["test_wrong"]


def test_import_error_is_a_collection_error_not_a_failure():
    result = run_suite("m", MODULE, "import does_not_exist\n\ndef test_x():\n    pass\n", 30.0)
    assert result.collection_error
    assert not result.usable


def test_a_hanging_test_times_out_instead_of_hanging_the_harness():
    suite = "import m\n\ndef test_forever():\n    while True:\n        pass\n"
    result = run_suite("m", MODULE, suite, timeout_s=3.0)
    assert not result.usable
    assert "TIMEOUT" in result.stdout


def test_a_hanging_mutant_counts_as_detected():
    # A mutant that hangs the suite changed observable behavior, so the suite
    # caught it. Counting it as survived would reward infinite loops.
    hanging_module = "def double(n):\n    while n:\n        n = n\n    return n * 2\n"
    detected, timed_out = suite_detects("m", hanging_module, GOOD_SUITE, timeout_s=3.0)
    assert detected
    assert timed_out


def test_an_undetected_mutant_survives():
    # `n * 2` becomes `n ** 2`, and 2 ** 2 == 2 * 2, so this test cannot tell.
    detected, timed_out = suite_detects("m", "def double(n):\n    return n ** 2\n", GOOD_SUITE, 30.0)
    assert not detected
    assert not timed_out


def test_a_detected_mutant_is_killed():
    detected, timed_out = suite_detects("m", "def double(n):\n    return n * 3\n", GOOD_SUITE, 30.0)
    assert detected
    assert not timed_out


def test_hash_seed_changes_between_runs_when_asked():
    # Pins the mechanism the flake filter depends on: the same suite must be able
    # to see different iteration orders across runs.
    suite = (
        "import m\n\n"
        "def test_seed_visible():\n"
        "    import os\n"
        "    assert os.environ['PYTHONHASHSEED'] == '7'\n"
    )
    assert run_suite("m", MODULE, suite, timeout_s=30.0, hash_seed=7).usable
    assert not run_suite("m", MODULE, suite, timeout_s=30.0, hash_seed=1).usable


def test_running_a_single_test_by_node_id():
    suite = GOOD_SUITE + "\n\ndef test_broken():\n    assert False\n"
    assert run_suite("m", MODULE, suite, timeout_s=30.0, node_id="test_double").usable
    assert not run_suite("m", MODULE, suite, timeout_s=30.0, node_id="test_broken").usable
