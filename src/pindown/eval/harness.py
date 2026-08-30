"""The referee.

Each arm produces a test suite. The harness grades all of them with the same
mutant set, the same timeouts and the same quality filters, and writes one row
per module per arm. Nothing here knows how a suite was produced, which is the
point: the agent gets no advantage from being the thing under test.
"""

from __future__ import annotations

import json
import platform
import time
import traceback
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from pindown.agent.llm import LLM
from pindown.agent.loop import ArmResult, run_agent, run_llm_baseline
from pindown.baseline.golden import run_golden_baseline
from pindown.config import RUNS_DIR, Budget, ModelConfig, git_revision
from pindown.models import Arm, CorpusModule, IterationRecord, ModuleOutcome, TestSuite
from pindown.mutation.engine import run_campaign
from pindown.mutation.operators import build_mutants
from pindown.runtime.pytest_runner import run_suite
from pindown.runtime.quality import count_tests

ALL_ARMS = ["human", "golden", "baseline", "agent"]


def new_run_dir(tag: str = "") -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    name = f"{stamp}-{tag}" if tag else stamp
    path = RUNS_DIR / name
    (path / "traces").mkdir(parents=True, exist_ok=True)
    (path / "suites").mkdir(parents=True, exist_ok=True)
    latest = RUNS_DIR / "latest"
    if latest.is_symlink() or latest.exists():
        latest.unlink()
    latest.symlink_to(path.name)
    return path


def write_provenance(run_dir: Path, budget: Budget, cfg: ModelConfig, modules: list[CorpusModule], arms: list[str]) -> None:
    (run_dir / "config.json").write_text(
        json.dumps(
            {
                "started_utc": datetime.now(UTC).isoformat(),
                "git_revision": git_revision(),
                "python": platform.python_version(),
                "platform": platform.platform(),
                "model": "stub" if cfg.stub else cfg.model,
                "temperature": cfg.temperature,
                "arms": arms,
                "modules": [m.id for m in modules],
                "budget": asdict(budget),
            },
            indent=2,
        )
    )


def run_human_arm(module: CorpusModule, budget: Budget) -> ArmResult:
    """The project's own tests, graded exactly as written.

    These are not filtered. The filters exist to catch a model's bad habits, and
    applying them to the human suite would be measuring a different thing --
    besides, the corpus validator already established that this suite passes.
    """
    started = time.monotonic()
    source = module.source
    tests = module.reference_test_path.read_text()
    mutants = build_mutants(source, limit=budget.max_mutants)

    timing = run_suite(module.import_name, source, tests, timeout_s=budget.pytest_timeout_s * 4)
    report = run_campaign(
        module.id,
        module.import_name,
        source,
        tests,
        "human",
        budget,
        timing.duration_s,
        mutants,
    )
    return ArmResult(
        suite=TestSuite(module.id, "human", tests, count_tests(tests)),
        report=report,
        iterations=[
            IterationRecord(
                n=1,
                phase="human",
                tests_proposed=count_tests(tests),
                tests_kept=count_tests(tests),
                discarded=[],
                score_before=0.0,
                score_after=report.score,
                survivors_before=len(mutants),
                survivors_after=len(report.survivors),
                duration_s=time.monotonic() - started,
            )
        ],
        wall_clock_s=time.monotonic() - started,
        suite_runtime_s=timing.duration_s,
    )


def run_one(
    module: CorpusModule,
    arm: str,
    budget: Budget,
    cfg: ModelConfig,
    run_dir: Path,
    progress: bool = True,
) -> ModuleOutcome:
    if progress:
        print(f"[{module.id}] {arm}", flush=True)

    trace_dir = run_dir / "traces" / module.id / arm
    suites_dir = run_dir / "suites"

    if arm == Arm.HUMAN:
        result = run_human_arm(module, budget)
        (suites_dir / f"{module.id}.human.py").write_text(result.suite.source)
    elif arm == "golden":
        result = run_golden_baseline(module, budget, artifact_dir=suites_dir)
    elif arm == Arm.BASELINE:
        llm = LLM(cfg, trace_dir=trace_dir, max_calls=2)
        result = run_llm_baseline(module, llm, budget, artifact_dir=suites_dir)
    elif arm == Arm.AGENT:
        llm = LLM(cfg, trace_dir=trace_dir, max_calls=budget.max_llm_calls)
        result = run_agent(module, llm, budget, artifact_dir=suites_dir, progress=progress)
    else:
        raise ValueError(f"unknown arm: {arm}")

    outcome = ModuleOutcome(
        module_id=module.id,
        arm=arm,
        score=result.report.score,
        killed=result.report.killed,
        survived=result.report.survived,
        timeout=result.report.timeout,
        total=result.report.total,
        n_tests=result.suite.n_tests,
        suite_runtime_s=round(result.suite_runtime_s, 3),
        wall_clock_s=round(result.wall_clock_s, 2),
        prompt_tokens=result.usage.prompt_tokens,
        completion_tokens=result.usage.completion_tokens,
        cost_usd=round(result.usage.cost(cfg), 4),
        iterations=result.iterations,
        error=result.error,
    )

    if progress:
        detail = f"score {outcome.score:.1%}  tests {outcome.n_tests}  {outcome.wall_clock_s:.0f}s"
        if outcome.error:
            detail += f"  ERROR: {outcome.error[:80]}"
        print(f"  -> {detail}", flush=True)

    return outcome


def run_eval(
    modules: list[CorpusModule],
    arms: list[str],
    budget: Budget,
    cfg: ModelConfig,
    tag: str = "",
    progress: bool = True,
) -> Path:
    run_dir = new_run_dir(tag)
    write_provenance(run_dir, budget, cfg, modules, arms)
    records = run_dir / "records.jsonl"

    with records.open("w") as handle:
        for module in modules:
            for arm in arms:
                try:
                    outcome = run_one(module, arm, budget, cfg, run_dir, progress)
                except Exception as exc:  # a crashed arm is a result, not a stopped run
                    crash_log = run_dir / "crashes" / f"{module.id}.{arm}.txt"
                    crash_log.parent.mkdir(parents=True, exist_ok=True)
                    crash_log.write_text(traceback.format_exc())
                    outcome = ModuleOutcome(
                        module_id=module.id,
                        arm=arm,
                        score=0.0,
                        killed=0,
                        survived=0,
                        timeout=0,
                        total=0,
                        n_tests=0,
                        suite_runtime_s=0.0,
                        wall_clock_s=0.0,
                        error=f"{type(exc).__name__}: {exc}",
                    )
                    if progress:
                        print(f"  -> crashed: {outcome.error}", flush=True)
                handle.write(outcome.to_json() + "\n")
                handle.flush()

    return run_dir
