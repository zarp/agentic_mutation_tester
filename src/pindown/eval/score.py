"""Turning records.jsonl into the tables that go in the README.

Nothing in the results is typed by hand. Every number a reader sees is generated
from the log of an actual run, so a claim in the README and the evidence behind
it cannot drift apart.

The headline is the median, not the mean. Module difficulty varies by a factor of
several, and one module where every arm scores badly should not decide the story.
Both are reported.
"""

from __future__ import annotations

import json
import statistics
from dataclasses import dataclass
from pathlib import Path

from pindown.config import REPO_ROOT

ARM_LABEL = {
    "human": "Human tests (ceiling)",
    "golden": "Golden fuzz baseline",
    "baseline": "One-shot prompt baseline",
    "agent": "pindown agent",
}

ARM_ORDER = ["human", "golden", "baseline", "agent"]


@dataclass
class ArmSummary:
    arm: str
    n_modules: int
    median_score: float
    mean_score: float
    min_score: float
    max_score: float
    total_tests: int
    median_tests: float
    total_cost: float
    median_wall_clock: float
    failures: int
    discarded_tests: int

    @property
    def label(self) -> str:
        return ARM_LABEL.get(self.arm, self.arm)


def load_records(run_dir: Path) -> list[dict]:
    path = run_dir / "records.jsonl"
    if not path.exists():
        raise SystemExit(f"No records.jsonl in {run_dir}")
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def summarize(records: list[dict]) -> dict[str, ArmSummary]:
    by_arm: dict[str, list[dict]] = {}
    for record in records:
        by_arm.setdefault(record["arm"], []).append(record)

    summaries: dict[str, ArmSummary] = {}
    for arm, rows in by_arm.items():
        scores = [r["score"] for r in rows]
        discarded = sum(
            len(it.get("discarded", [])) for r in rows for it in r.get("iterations", [])
        )
        summaries[arm] = ArmSummary(
            arm=arm,
            n_modules=len(rows),
            median_score=statistics.median(scores) if scores else 0.0,
            mean_score=statistics.fmean(scores) if scores else 0.0,
            min_score=min(scores) if scores else 0.0,
            max_score=max(scores) if scores else 0.0,
            total_tests=sum(r["n_tests"] for r in rows),
            median_tests=statistics.median([r["n_tests"] for r in rows]) if rows else 0,
            total_cost=sum(r.get("cost_usd", 0.0) for r in rows),
            median_wall_clock=statistics.median([r["wall_clock_s"] for r in rows]) if rows else 0,
            failures=sum(1 for r in rows if r.get("error")),
            discarded_tests=discarded,
        )
    return summaries


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def headline_table(summaries: dict[str, ArmSummary]) -> str:
    arms = [a for a in ARM_ORDER if a in summaries]
    lines = [
        "| Metric | " + " | ".join(summaries[a].label for a in arms) + " |",
        "| --- | " + " | ".join("---" for _ in arms) + " |",
    ]

    def row(name: str, fn) -> str:
        return f"| {name} | " + " | ".join(fn(summaries[a]) for a in arms) + " |"

    lines += [
        row("Median mutation score", lambda s: _pct(s.median_score)),
        row("Mean mutation score", lambda s: _pct(s.mean_score)),
        row("Range", lambda s: f"{_pct(s.min_score)} - {_pct(s.max_score)}"),
        row("Median tests per module", lambda s: f"{s.median_tests:.0f}"),
        row("Median wall clock per module", lambda s: f"{s.median_wall_clock:.0f}s"),
        row("Total model cost", lambda s: f"${s.total_cost:.2f}"),
        row("Modules with no usable suite", lambda s: str(s.failures)),
        row("Generated tests discarded by filters", lambda s: str(s.discarded_tests)),
    ]
    return "\n".join(lines)


def per_module_table(records: list[dict]) -> str:
    by_module: dict[str, dict[str, dict]] = {}
    for record in records:
        by_module.setdefault(record["module_id"], {})[record["arm"]] = record

    arms = [a for a in ARM_ORDER if any(a in v for v in by_module.values())]
    lines = [
        "| Module | Mutants | " + " | ".join(ARM_LABEL[a].split(" (")[0] for a in arms) + " |",
        "| --- | ---: | " + " | ".join("---:" for _ in arms) + " |",
    ]

    for module_id in sorted(by_module):
        row = by_module[module_id]
        total = max((r["total"] for r in row.values()), default=0)
        cells = []
        for arm in arms:
            record = row.get(arm)
            if record is None:
                cells.append("-")
            elif record.get("error"):
                cells.append("failed")
            else:
                cells.append(_pct(record["score"]))
        lines.append(f"| `{module_id}` | {total} | " + " | ".join(cells) + " |")

    return "\n".join(lines)


def iteration_table(records: list[dict]) -> str:
    """Where the agent's score came from, iteration by iteration.

    This is the table that shows whether the survivor-driven second phase is
    doing real work or whether phase one was the whole story.
    """
    rows = [r for r in records if r["arm"] == "agent" and r.get("iterations")]
    if not rows:
        return ""

    by_iteration: dict[int, list[float]] = {}
    for record in rows:
        for it in record["iterations"]:
            by_iteration.setdefault(it["n"], []).append(it["score_after"])

    lines = [
        "| Iteration | Modules still improving | Median score after |",
        "| --- | ---: | ---: |",
    ]
    for n in sorted(by_iteration):
        scores = by_iteration[n]
        lines.append(f"| {n} | {len(scores)} | {_pct(statistics.median(scores))} |")
    return "\n".join(lines)


def discard_taxonomy(records: list[dict]) -> str:
    """What the quality filters threw away, grouped by reason.

    A taxonomy of rejected tests says more about a model's failure modes than the
    headline score does, and it is the part that transfers to other projects.
    """
    counts: dict[str, dict[str, int]] = {}
    for record in records:
        arm = record["arm"]
        for it in record.get("iterations", []):
            for entry in it.get("discarded", []):
                reason = entry.split(": ", 1)[-1] if ": " in entry else entry
                reason = reason[:70]
                counts.setdefault(reason, {}).setdefault(arm, 0)
                counts[reason][arm] += 1

    if not counts:
        return ""

    arms = [a for a in ARM_ORDER if any(a in v for v in counts.values())]
    lines = [
        "| Reason a test was discarded | " + " | ".join(arms) + " |",
        "| --- | " + " | ".join("---:" for _ in arms) + " |",
    ]
    for reason in sorted(counts, key=lambda r: -sum(counts[r].values())):
        cells = [str(counts[reason].get(a, 0)) for a in arms]
        lines.append(f"| {reason} | " + " | ".join(cells) + " |")
    return "\n".join(lines)


def render(run_dir: Path) -> str:
    records = load_records(run_dir)
    summaries = summarize(records)
    config = json.loads((run_dir / "config.json").read_text())

    parts = [
        f"# Results: `{run_dir.name}`",
        "",
        f"Model `{config['model']}` at temperature {config['temperature']}, "
        f"Python {config['python']}, revision `{config['git_revision']}`. "
        f"{len(config['modules'])} modules, {len(config['arms'])} arms.",
        "",
        "## Headline",
        "",
        headline_table(summaries),
        "",
        "## Per module",
        "",
        per_module_table(records),
    ]

    iterations = iteration_table(records)
    if iterations:
        parts += ["", "## Where the agent's score came from", "", iterations]

    taxonomy = discard_taxonomy(records)
    if taxonomy:
        parts += ["", "## What the quality filters rejected", "", taxonomy]

    return "\n".join(parts) + "\n"


README_START = "<!-- RESULTS -->"
README_END = "<!-- /RESULTS -->"


def update_readme(run_dir: Path, readme: Path) -> bool:
    """Write the current results into the README between the markers.

    The README claims its numbers are never typed by hand. This is what makes
    that true: the only way a figure gets in there is by coming out of a run log.
    """
    if not readme.exists():
        return False
    text = readme.read_text()
    if README_START not in text or README_END not in text:
        return False

    records = load_records(run_dir)
    summaries = summarize(records)
    config = json.loads((run_dir / "config.json").read_text())

    body = "\n".join(
        [
            README_START,
            "",
            f"From `runs/{run_dir.name}/`: model `{config['model']}` at temperature "
            f"{config['temperature']}, {len(config['modules'])} modules, "
            f"{len(config['arms'])} arms, Python {config['python']}, "
            f"revision `{config['git_revision']}`.",
            "",
            headline_table(summaries),
            "",
            per_module_table(records),
            "",
            README_END,
        ]
    )

    head, _, rest = text.partition(README_START)
    _, _, tail = rest.partition(README_END)
    readme.write_text(head + body + tail)
    return True


def write_results(run_dir: Path) -> Path:
    text = render(run_dir)
    path = run_dir / "results.md"
    path.write_text(text)

    records = load_records(run_dir)
    summaries = summarize(records)
    (run_dir / "metrics.json").write_text(
        json.dumps({arm: vars(s) for arm, s in summaries.items()}, indent=2)
    )

    update_readme(run_dir, REPO_ROOT / "README.md")
    return path
