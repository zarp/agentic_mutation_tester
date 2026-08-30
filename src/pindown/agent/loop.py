"""The agent.

Phase one writes a suite that pins current behavior. Phase two reads the list of
mutants that suite failed to catch and writes tests aimed at exactly those. The
loop stops when the score stops moving.

The design claim being tested is narrow and checkable: the surviving-mutant list
is a better instruction than any wording of "write more tests", because it is
specific, machine-generated, and states the gap in terms of a concrete behavior
difference the model can reason about.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from pindown.agent.llm import LLM, BudgetExceeded, Usage, extract_code
from pindown.agent.merge import merge_suites
from pindown.config import PROMPTS_DIR, Budget
from pindown.models import CorpusModule, IterationRecord, MutationReport, TestSuite
from pindown.mutation.engine import run_campaign, survivor_digest
from pindown.mutation.operators import build_mutants
from pindown.runtime.quality import count_tests, filter_suite


@dataclass
class ArmResult:
    suite: TestSuite
    report: MutationReport
    iterations: list[IterationRecord] = field(default_factory=list)
    usage: Usage = field(default_factory=Usage)
    wall_clock_s: float = 0.0
    suite_runtime_s: float = 0.0
    error: str | None = None


def render(name: str, **fields: str) -> str:
    text = (PROMPTS_DIR / name).read_text()
    for key, value in fields.items():
        text = text.replace("{{" + key + "}}", value)
    return text


def _empty_report(module_id: str, arm: str, n_mutants: int) -> MutationReport:
    return MutationReport(module_id=module_id, arm=arm, killed=0, survived=n_mutants, timeout=0)


def run_agent(
    module: CorpusModule,
    llm: LLM,
    budget: Budget,
    artifact_dir: Path | None = None,
    progress: bool = False,
) -> ArmResult:
    started = time.monotonic()
    mutants = build_mutants(module.source, limit=budget.max_mutants)
    source = module.source
    name = module.import_name

    def say(msg: str) -> None:
        if progress:
            print(f"  {msg}", flush=True)

    # Phase one: pin current behavior.
    t0 = time.monotonic()
    try:
        reply = llm.complete(
            system=(PROMPTS_DIR / "pin.system.md").read_text(),
            user=render("pin.user.md", MODULE_NAME=name, MODULE_SOURCE=source),
            purpose="pin",
        )
    except BudgetExceeded as exc:
        return ArmResult(
            suite=TestSuite(module.id, "agent", ""),
            report=_empty_report(module.id, "agent", len(mutants)),
            usage=llm.usage,
            wall_clock_s=time.monotonic() - started,
            error=str(exc),
        )

    proposed = extract_code(reply)
    outcome = filter_suite(name, source, proposed, budget)

    # One repair turn. A file that will not import is usually a small, obvious
    # mistake, and giving the model the actual error fixes it far more often than
    # resampling does.
    if outcome.fatal and llm.usage.calls < budget.max_llm_calls:
        say(f"phase 1 rejected ({outcome.fatal[:80]}); one repair turn")
        repair = llm.complete(
            system=(PROMPTS_DIR / "pin.system.md").read_text(),
            user=(
                render("pin.user.md", MODULE_NAME=name, MODULE_SOURCE=source)
                + f"\n\nYour previous attempt was rejected:\n\n{outcome.fatal[:1500]}\n\n"
                "Return the corrected file."
            ),
            purpose="pin-repair",
        )
        proposed = extract_code(repair)
        outcome = filter_suite(name, source, proposed, budget)

    if outcome.fatal:
        return ArmResult(
            suite=TestSuite(module.id, "agent", "", discarded=outcome.discarded),
            report=_empty_report(module.id, "agent", len(mutants)),
            usage=llm.usage,
            wall_clock_s=time.monotonic() - started,
            error=outcome.fatal,
        )

    suite_runtime = outcome.final_result.duration_s if outcome.final_result else 1.0
    report = run_campaign(
        module.id, name, source, outcome.source, "agent", budget, suite_runtime, mutants, progress
    )
    say(f"phase 1: {outcome.n_tests} tests kept, {report.score:.1%} mutation score")

    iterations = [
        IterationRecord(
            n=1,
            phase="pin",
            tests_proposed=outcome.n_tests + len(outcome.discarded),
            tests_kept=outcome.n_tests,
            discarded=outcome.discarded,
            score_before=0.0,
            score_after=report.score,
            survivors_before=len(mutants),
            survivors_after=len(report.survivors),
            duration_s=time.monotonic() - t0,
        )
    ]

    current_source = outcome.source
    stagnant = 0

    # Phase two: aim at the survivors, until the score stops moving.
    for n in range(2, budget.max_iterations + 1):
        if not report.survivors:
            say("no survivors left")
            break
        if time.monotonic() - started > budget.max_wall_clock_s:
            say("wall clock budget reached")
            break
        if llm.usage.calls >= budget.max_llm_calls:
            say("call budget reached")
            break
        if stagnant >= budget.plateau_patience:
            say(f"score plateaued after {stagnant} flat iterations")
            break

        t0 = time.monotonic()
        score_before = report.score
        survivors_before = len(report.survivors)

        try:
            reply = llm.complete(
                system=(PROMPTS_DIR / "kill.system.md").read_text(),
                user=render(
                    "kill.user.md",
                    MODULE_NAME=name,
                    MODULE_SOURCE=source,
                    TEST_SOURCE=current_source,
                    SURVIVORS=survivor_digest(report.survivors),
                    N_SURVIVORS=str(len(report.survivors)),
                    KILLED=str(report.killed + report.timeout),
                    TOTAL=str(report.total),
                ),
                purpose=f"kill-{n}",
            )
        except BudgetExceeded:
            break

        addition = extract_code(reply)
        merged, duplicates = merge_suites(current_source, addition)
        if merged == current_source:
            say(f"iteration {n}: nothing new proposed")
            stagnant += 1
            continue

        checked = filter_suite(name, source, merged, budget)
        if checked.fatal:
            # Keep the suite we already had. A rejected batch is a normal outcome,
            # not a run-ending error.
            say(f"iteration {n}: batch rejected ({checked.fatal[:70]})")
            iterations.append(
                IterationRecord(
                    n=n,
                    phase="kill",
                    tests_proposed=0,
                    tests_kept=0,
                    discarded=[checked.fatal],
                    score_before=score_before,
                    score_after=score_before,
                    survivors_before=survivors_before,
                    survivors_after=survivors_before,
                    duration_s=time.monotonic() - t0,
                    note="batch rejected, previous suite retained",
                )
            )
            stagnant += 1
            continue

        suite_runtime = checked.final_result.duration_s if checked.final_result else suite_runtime
        new_report = run_campaign(
            module.id, name, source, checked.source, "agent", budget, suite_runtime, mutants, progress
        )

        gain = new_report.score - score_before
        note = ""
        if duplicates:
            note = f"{len(duplicates)} duplicate test names skipped"

        iterations.append(
            IterationRecord(
                n=n,
                phase="kill",
                tests_proposed=checked.n_tests + len(checked.discarded),
                tests_kept=checked.n_tests,
                discarded=checked.discarded,
                score_before=score_before,
                score_after=new_report.score,
                survivors_before=survivors_before,
                survivors_after=len(new_report.survivors),
                duration_s=time.monotonic() - t0,
                note=note,
            )
        )

        say(
            f"iteration {n}: {new_report.score:.1%} mutation score "
            f"({gain:+.1%}), {len(new_report.survivors)} survivors"
        )

        current_source = checked.source
        report = new_report
        stagnant = stagnant + 1 if gain < budget.min_gain else 0

    suite = TestSuite(
        module_id=module.id,
        arm="agent",
        source=current_source,
        n_tests=count_tests(current_source),
        discarded=[d for it in iterations for d in it.discarded],
    )
    result = ArmResult(
        suite=suite,
        report=report,
        iterations=iterations,
        usage=llm.usage,
        wall_clock_s=time.monotonic() - started,
        suite_runtime_s=suite_runtime,
    )
    if artifact_dir is not None:
        _write_artifacts(artifact_dir, module, result)
    return result


def run_llm_baseline(
    module: CorpusModule,
    llm: LLM,
    budget: Budget,
    artifact_dir: Path | None = None,
) -> ArmResult:
    """One prompt, one response, no execution and no verification.

    This is the reasonable thing a competent engineer does today when they need
    tests for a module they inherited, so it is the honest baseline.

    The generated suite still passes through the quality filters before it is
    graded. Skipping them would flatter the agent: an unfiltered baseline often
    fails to import at all, and scoring that as zero would measure the harness
    rather than the approach.
    """
    started = time.monotonic()
    mutants = build_mutants(module.source, limit=budget.max_mutants)
    name = module.import_name
    source = module.source

    try:
        reply = llm.complete(
            system=(PROMPTS_DIR / "baseline.system.md").read_text(),
            user=render("baseline.user.md", MODULE_NAME=name, MODULE_SOURCE=source),
            purpose="baseline",
        )
    except BudgetExceeded as exc:
        return ArmResult(
            suite=TestSuite(module.id, "baseline", ""),
            report=_empty_report(module.id, "baseline", len(mutants)),
            usage=llm.usage,
            wall_clock_s=time.monotonic() - started,
            error=str(exc),
        )

    outcome = filter_suite(name, source, extract_code(reply), budget)
    if outcome.fatal:
        return ArmResult(
            suite=TestSuite(module.id, "baseline", "", discarded=outcome.discarded),
            report=_empty_report(module.id, "baseline", len(mutants)),
            usage=llm.usage,
            wall_clock_s=time.monotonic() - started,
            error=outcome.fatal,
        )

    suite_runtime = outcome.final_result.duration_s if outcome.final_result else 1.0
    report = run_campaign(
        module.id, name, source, outcome.source, "baseline", budget, suite_runtime, mutants
    )
    result = ArmResult(
        suite=TestSuite(module.id, "baseline", outcome.source, outcome.n_tests, outcome.discarded),
        report=report,
        iterations=[
            IterationRecord(
                n=1,
                phase="baseline",
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
        usage=llm.usage,
        wall_clock_s=time.monotonic() - started,
        suite_runtime_s=suite_runtime,
    )
    if artifact_dir is not None:
        _write_artifacts(artifact_dir, module, result)
    return result


def _write_artifacts(artifact_dir: Path, module: CorpusModule, result: ArmResult) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / f"{module.id}.{result.suite.arm}.py").write_text(result.suite.source)
    survivors = "\n".join(f"{m.id}  line {m.lineno}  {m.description}" for m in result.report.survivors)
    (artifact_dir / f"{module.id}.{result.suite.arm}.survivors.txt").write_text(survivors)
