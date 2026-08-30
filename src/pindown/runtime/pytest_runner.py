"""Running a candidate suite against a version of the module under test.

Generated test code is untrusted: it can loop forever, write files, or import
anything. Every execution here goes through a subprocess with a hard timeout, in
a throwaway directory, with plugin autoloading disabled so a plugin installed on
the host cannot change the result. That last part is a reproducibility measure
as much as a safety one.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from pindown.models import PytestResult

TEST_FILENAME = "test_pinned.py"

# Exit code the child uses when its own watchdog fires. Chosen to avoid pytest's
# documented codes (0-5).
TIMEOUT_EXIT_CODE = 99

# A mutant can easily produce an infinite loop, so a hard time limit is not
# optional. Relying on the parent to kill the child turns out to be fragile:
# under a seccomp sandbox `os.kill` can be denied, and then the timeout handler
# raises PermissionError and takes the whole campaign down with it.
#
# Arming a timer inside the child instead needs no privileges at all. The child
# stops itself, the parent just reads the exit code, and the parent-side timeout
# stays as a backstop for the case where the child is too broken to run its own
# handler.
CONFTEST = """
import os
import signal


def _timeout(signum, frame):
    os._exit(__EXIT_CODE__)


signal.signal(signal.SIGALRM, _timeout)
signal.setitimer(signal.ITIMER_REAL, __TIMEOUT__)
"""


def _env(hash_seed: int | None) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # A fixed seed makes the mutation campaign reproducible. The flake filter
    # deliberately varies it, which is how dict and set ordering dependence in a
    # generated test gets caught before it reaches the user.
    if hash_seed is not None:
        env["PYTHONHASHSEED"] = str(hash_seed)
    env.pop("PYTHONPATH", None)
    return env


def _write_workspace(
    root: Path,
    module_name: str,
    module_source: str,
    test_source: str,
    self_timeout_s: float,
) -> None:
    (root / f"{module_name}.py").write_text(module_source)
    (root / TEST_FILENAME).write_text(test_source)
    (root / "conftest.py").write_text(
        CONFTEST.replace("__EXIT_CODE__", str(TIMEOUT_EXIT_CODE)).replace(
            "__TIMEOUT__", f"{self_timeout_s:.2f}"
        )
    )


def _run(cmd: list[str], root: Path, env: dict[str, str], timeout_s: float):
    """Run a child, tolerating a sandbox that will not let us signal it.

    Returns (returncode, output, timed_out). The child's own watchdog should fire
    first; this only has to survive the case where it did not.
    """
    proc = subprocess.Popen(
        cmd, cwd=root, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        out, err = proc.communicate(timeout=timeout_s)
    except subprocess.TimeoutExpired:
        for attempt in (proc.kill, proc.terminate):
            try:
                attempt()
                break
            except (PermissionError, ProcessLookupError, OSError):
                continue
        try:
            out, err = proc.communicate(timeout=10)
        except Exception:
            out, err = "", ""
        return TIMEOUT_EXIT_CODE, (out or "") + (err or ""), True

    timed_out = proc.returncode == TIMEOUT_EXIT_CODE
    return proc.returncode, (out or "") + (err or ""), timed_out


def run_suite(
    module_name: str,
    module_source: str,
    test_source: str,
    timeout_s: float,
    hash_seed: int | None = 0,
    node_id: str | None = None,
) -> PytestResult:
    """Run the suite and return per-test detail.

    `node_id` restricts the run to a single test, which is how the isolation
    check finds tests that only pass because an earlier test ran first.
    """
    start = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="pindown-") as tmp:
        root = Path(tmp)
        _write_workspace(root, module_name, module_source, test_source, timeout_s)
        xml_path = root / "report.xml"
        target = f"{TEST_FILENAME}::{node_id}" if node_id else TEST_FILENAME
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            target,
            "-q",
            "--no-header",
            "--tb=short",
            "-p",
            "no:cacheprovider",
            f"--junit-xml={xml_path}",
        ]
        returncode, output, timed_out = _run(cmd, root, _env(hash_seed), timeout_s + 10.0)
        duration = time.monotonic() - start

        if timed_out:
            return PytestResult(
                ok=False,
                collected=0,
                passed=0,
                failed=0,
                errors=0,
                duration_s=duration,
                stdout=f"TIMEOUT after {timeout_s}s\n{output[-500:]}",
                collection_error=False,
            )

        return _parse(returncode, output, xml_path, duration)


def _parse(returncode: int, stdout: str, xml_path: Path, duration: float) -> PytestResult:
    if not xml_path.exists():
        # pytest died before it could write a report: a syntax error in the
        # generated file, or an exception at import time.
        return PytestResult(
            ok=False,
            collected=0,
            passed=0,
            failed=0,
            errors=1,
            duration_s=duration,
            stdout=stdout,
            collection_error=True,
        )

    root = ET.parse(xml_path).getroot()
    suite = root.find("testsuite") if root.tag == "testsuites" else root
    if suite is None:
        return PytestResult(
            ok=False,
            collected=0,
            passed=0,
            failed=0,
            errors=1,
            duration_s=duration,
            stdout=stdout,
            collection_error=True,
        )

    collected = int(suite.get("tests", 0))
    failures = int(suite.get("failures", 0))
    errors = int(suite.get("errors", 0))
    skipped = int(suite.get("skipped", 0))
    passed = collected - failures - errors - skipped

    # A collection error is not a failing test, and the difference matters: a
    # failing test can be pruned, an import error cannot. pytest reports it as a
    # synthetic testcase with an empty classname named after the file, so it
    # arrives looking like an ordinary failure unless you check for that.
    stem = TEST_FILENAME.removesuffix(".py")
    failed_tests: list[str] = []
    collection_error = collected == 0 and errors > 0

    for case in suite.iter("testcase"):
        error = case.find("error")
        if error is None and case.find("failure") is None:
            continue
        name = case.get("name") or ""
        if error is not None and (not case.get("classname") or name == stem):
            collection_error = True
            continue
        if name:
            failed_tests.append(name)

    return PytestResult(
        ok=returncode == 0,
        collected=collected,
        passed=passed,
        failed=failures,
        errors=errors,
        duration_s=duration,
        stdout=stdout,
        failed_tests=failed_tests,
        collection_error=collection_error,
    )


def suite_detects(
    module_name: str,
    mutated_source: str,
    test_source: str,
    timeout_s: float,
) -> tuple[bool, bool]:
    """Fast path for the mutation campaign: does this suite notice this mutant?

    Returns (detected, timed_out). Stops at the first failure and skips the XML
    report, because the only thing that matters is the exit code. Over a few
    hundred mutants this is roughly twice as fast as the detailed path.
    """
    with tempfile.TemporaryDirectory(prefix="pindown-mut-") as tmp:
        root = Path(tmp)
        _write_workspace(root, module_name, mutated_source, test_source, timeout_s)
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            TEST_FILENAME,
            "-x",
            "-q",
            "--no-header",
            "--tb=no",
            "-p",
            "no:cacheprovider",
        ]
        returncode, _, timed_out = _run(cmd, root, _env(0), timeout_s + 10.0)
        if timed_out:
            # The mutant made the suite hang. That is a detection: behavior
            # changed observably. Counting it as survived would reward suites
            # that trigger infinite loops.
            return True, True
        return returncode != 0, False
