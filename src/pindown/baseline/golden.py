"""A model-free baseline: call the code and freeze whatever it returns.

This is the strongest thing you can build without an LLM. Probe every public
function with a fixed pool of arguments, record what comes back, and emit those
observations as assertions. It is real characterization testing, it is
completely deterministic, and it costs nothing to run.

It exists for two reasons. It gives someone with no API key a meaningful arm to
compare against, and it sets the bar the agent actually has to clear. Beating a
prompt is easy; beating exhaustive small-input fuzzing with exact assertions is
the claim worth making.

Where it fails is instructive, and it is the reason the agent is not obsolete:
it only reaches functions whose arguments happen to be in the pool, it never
constructs a class, and it cannot find the one input that separates `>` from
`>=` unless that input is already in the pool.
"""

from __future__ import annotations

import ast
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from pindown.config import Budget
from pindown.models import CorpusModule, IterationRecord, MutationReport, TestSuite
from pindown.mutation.engine import run_campaign
from pindown.mutation.operators import build_mutants

MAX_PASSING_PER_FN = 10
MAX_RAISING_PER_FN = 4

PROBE = '''
import contextlib
import importlib
import inspect
import io
import json
import os
import signal
import sys

# Results go to a file, never to stdout. A probed function is free to print --
# semver's CLI helpers dump an argparse usage message the moment they are called
# -- and anything on stdout would corrupt the payload.
OUT_PATH = "probe_out.json"
MAX_REPR = 200

POOL = [0, 1, -1, 2, 10, "", "a", "abc", "  a b  ", [], [1, 2, 3], (), True, False,
        None, 0.5, -1.5, {}, {"a": 1}, set()]

MAX_PASSING = __MAX_PASSING__
MAX_RAISING = __MAX_RAISING__


class CallTimeout(Exception):
    pass


def _alarm(signum, frame):
    raise CallTimeout()


signal.signal(signal.SIGALRM, _alarm)

mod = importlib.import_module("__MODULE_NAME__")
records = []

for name in sorted(dir(mod)):
    if name.startswith("_"):
        continue
    obj = getattr(mod, name)
    if inspect.isclass(obj) or not callable(obj):
        continue
    if getattr(obj, "__module__", None) != mod.__name__:
        continue
    try:
        sig = inspect.signature(obj)
    except (ValueError, TypeError):
        continue

    positional = [
        p for p in sig.parameters.values()
        if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]
    required = [p for p in positional if p.default is p.empty]
    arity = len(required)

    if arity == 0:
        candidates = [()]
    elif arity == 1:
        candidates = [(v,) for v in POOL]
    elif arity == 2:
        candidates = [(a, b) for a in POOL for b in POOL]
    else:
        continue

    passing = 0
    raising = 0
    for args in candidates:
        if passing >= MAX_PASSING and raising >= MAX_RAISING:
            break

        # Capture the arguments before the call. A function that mutates what it
        # is given -- exec_ populating a globals dict, say -- would otherwise be
        # recorded with the mutated value, producing an assertion that is both
        # enormous and wrong.
        args_repr = repr(args)
        if len(args_repr) > MAX_REPR:
            continue

        signal.setitimer(signal.ITIMER_REAL, 1.0)
        try:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                value = obj(*args)
        except CallTimeout:
            signal.setitimer(signal.ITIMER_REAL, 0)
            break
        except (Exception, SystemExit) as exc:
            signal.setitimer(signal.ITIMER_REAL, 0)
            if raising < MAX_RAISING:
                records.append({
                    "fn": name, "args": args_repr, "raises": type(exc).__name__,
                })
                raising += 1
            continue
        signal.setitimer(signal.ITIMER_REAL, 0)

        if passing >= MAX_PASSING:
            continue
        # Only keep values whose repr round-trips, so the generated assertion is
        # a literal rather than something depending on an address or on ordering.
        try:
            rendered = repr(value)
            if len(rendered) > MAX_REPR or eval(rendered) != value:
                continue
        except Exception:
            continue
        if rendered != rendered.strip() or "object at 0x" in rendered:
            continue
        if isinstance(value, float) and value != value:
            continue
        records.append({"fn": name, "args": args_repr, "value": rendered})
        passing += 1

with open(OUT_PATH, "w") as handle:
    json.dump(records, handle)
'''


def probe(module_name: str, module_source: str, timeout_s: float = 60.0) -> list[dict]:
    with tempfile.TemporaryDirectory(prefix="pindown-probe-") as tmp:
        root = Path(tmp)
        (root / f"{module_name}.py").write_text(module_source)
        script = (
            PROBE.replace("__MODULE_NAME__", module_name)
            .replace("__MAX_PASSING__", str(MAX_PASSING_PER_FN))
            .replace("__MAX_RAISING__", str(MAX_RAISING_PER_FN))
        )
        (root / "_probe.py").write_text(script)
        try:
            subprocess.run(
                [sys.executable, "_probe.py"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
        except subprocess.TimeoutExpired:
            return []

        out_path = root / "probe_out.json"
        if not out_path.exists():
            return []
        try:
            return json.loads(out_path.read_text())
        except json.JSONDecodeError:
            return []


def render_suite(module_name: str, records: list[dict]) -> str:
    if not records:
        return ""

    lines = [
        "# Generated by pindown's model-free baseline.",
        "# Every assertion below is an observation: the function was called with",
        "# these arguments and this is what it returned today.",
        "import pytest",
        "",
        f"import {module_name}",
        "",
    ]

    counters: dict[str, int] = {}
    emitted = 0
    for record in records:
        fn = record["fn"]
        counters[fn] = counters.get(fn, 0) + 1
        n = counters[fn]
        args = record["args"]
        # repr of a 1-tuple is "(x,)"; strip the wrapping parens for the call.
        call_args = args[1:-1].rstrip(",") if args.startswith("(") else args

        if "raises" in record:
            block = [
                f"def test_golden_{fn}_{n}_raises():",
                f"    with pytest.raises({record['raises']}):",
                f"        {module_name}.{fn}({call_args})",
            ]
        else:
            block = [
                f"def test_golden_{fn}_{n}():",
                f"    assert {module_name}.{fn}({call_args}) == {record['value']}",
            ]

        # Validate each test on its own. One unrenderable repr should cost one
        # test, not the entire file -- which is what happened the first time.
        try:
            ast.parse("\n".join(block))
        except SyntaxError:
            continue

        lines += block + ["", ""]
        emitted += 1

    if not emitted:
        return ""
    return "\n".join(lines).rstrip() + "\n"


def run_golden_baseline(module: CorpusModule, budget: Budget, artifact_dir: Path | None = None):
    from pindown.agent.loop import ArmResult, _write_artifacts
    from pindown.runtime.quality import filter_suite

    started = time.monotonic()
    mutants = build_mutants(module.source, limit=budget.max_mutants)
    name = module.import_name
    source = module.source

    records = probe(name, source)
    proposed = render_suite(name, records)

    if not proposed.strip():
        return ArmResult(
            suite=TestSuite(module.id, "golden", ""),
            report=MutationReport(module.id, "golden", killed=0, survived=len(mutants), timeout=0),
            wall_clock_s=time.monotonic() - started,
            error="probe produced no round-trippable observations",
        )

    outcome = filter_suite(name, source, proposed, budget)
    if outcome.fatal:
        return ArmResult(
            suite=TestSuite(module.id, "golden", "", discarded=outcome.discarded),
            report=MutationReport(module.id, "golden", killed=0, survived=len(mutants), timeout=0),
            wall_clock_s=time.monotonic() - started,
            error=outcome.fatal,
        )

    suite_runtime = outcome.final_result.duration_s if outcome.final_result else 1.0
    report = run_campaign(
        module.id, name, source, outcome.source, "golden", budget, suite_runtime, mutants
    )
    result = ArmResult(
        suite=TestSuite(module.id, "golden", outcome.source, outcome.n_tests, outcome.discarded),
        report=report,
        iterations=[
            IterationRecord(
                n=1,
                phase="golden",
                tests_proposed=outcome.n_tests + len(outcome.discarded),
                tests_kept=outcome.n_tests,
                discarded=outcome.discarded,
                score_before=0.0,
                score_after=report.score,
                survivors_before=len(mutants),
                survivors_after=len(report.survivors),
                duration_s=time.monotonic() - started,
            )
        ],
        wall_clock_s=time.monotonic() - started,
        suite_runtime_s=suite_runtime,
    )
    if artifact_dir is not None:
        _write_artifacts(artifact_dir, module, result)
    return result


__all__ = ["probe", "render_suite", "run_golden_baseline"]
