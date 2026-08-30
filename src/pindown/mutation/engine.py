"""The grader.

Given a module and a test suite, run every mutant and count how many the suite
notices. This is the only judge in the system. No model, including the one that
wrote the tests, ever gets an opinion on whether the tests are good.
"""

from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor

from pindown.config import Budget
from pindown.models import Mutant, MutantResult, MutationReport, Outcome
from pindown.mutation.operators import build_mutants
from pindown.runtime.pytest_runner import suite_detects


def run_campaign(
    module_id: str,
    module_name: str,
    module_source: str,
    test_source: str,
    arm: str,
    budget: Budget,
    baseline_duration_s: float,
    mutants: list[Mutant] | None = None,
    progress: bool = False,
) -> MutationReport:
    """Run every mutant against `test_source`.

    `baseline_duration_s` is how long the suite takes on the unmutated module.
    The per-mutant timeout is a multiple of that, so a slow suite is not punished
    with spurious timeouts and a fast suite is not left waiting on an infinite
    loop for thirty seconds.
    """
    started = time.monotonic()
    if mutants is None:
        mutants = build_mutants(module_source, limit=budget.max_mutants)

    report = MutationReport(module_id=module_id, arm=arm, killed=0, survived=0, timeout=0)

    if not mutants:
        return report

    if not test_source.strip():
        report.survived = len(mutants)
        report.survivors = list(mutants)
        report.results = [MutantResult(m.id, Outcome.SURVIVED, 0.0) for m in mutants]
        report.duration_s = time.monotonic() - started
        return report

    timeout_s = max(budget.mutant_timeout_floor_s, baseline_duration_s * budget.mutant_timeout_multiplier)

    def check(mutant: Mutant) -> tuple[Mutant, Outcome, float]:
        t0 = time.monotonic()
        detected, timed_out = suite_detects(module_name, mutant.source, test_source, timeout_s)
        elapsed = time.monotonic() - t0
        if timed_out:
            return mutant, Outcome.TIMEOUT, elapsed
        return mutant, Outcome.KILLED if detected else Outcome.SURVIVED, elapsed

    with ThreadPoolExecutor(max_workers=budget.mutation_workers) as pool:
        for i, (mutant, outcome, elapsed) in enumerate(pool.map(check, mutants), start=1):
            report.results.append(MutantResult(mutant.id, outcome, elapsed))
            if outcome is Outcome.KILLED:
                report.killed += 1
            elif outcome is Outcome.TIMEOUT:
                report.timeout += 1
            else:
                report.survived += 1
                report.survivors.append(mutant)
            if progress and i % 50 == 0:
                print(f"    {i}/{len(mutants)} mutants", flush=True)

    # Deterministic survivor ordering, so two runs produce comparable prompts.
    report.survivors.sort(key=lambda m: (m.lineno, m.id))
    report.duration_s = time.monotonic() - started
    return report


def survivor_digest(survivors: list[Mutant], limit: int = 40) -> str:
    """Render survivors as an agent-readable work list.

    Grouping by line keeps the prompt short and makes the shape of the gap
    obvious: twelve survivors on one function reads very differently from twelve
    survivors scattered across the file.
    """
    if not survivors:
        return "None. Every mutant is detected."

    shown = survivors[:limit]
    lines = [m.brief() for m in shown]
    if len(survivors) > limit:
        lines.append(f"... and {len(survivors) - limit} more survivors not shown.")
    return "\n\n".join(lines)
