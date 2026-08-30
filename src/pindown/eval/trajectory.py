"""Rendering a run into a trajectory a person can actually read.

A directory of prompt/response JSON is not a trajectory. What matters is the
interleaving: what the agent was told, what it produced, what the harness said
about it, and what that feedback caused it to do next. Splitting those across
four files makes the one interesting question -- did the survivor list actually
change the model's behavior -- impossible to answer by reading.

So this stitches the trace files, the iteration records and the campaign results
back into one document per module per arm, in the order things happened.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from pindown.config import PROMPTS_DIR

MAX_CODE_LINES = 60
MAX_PROMPT_LINES = 40


def _fence(text: str, limit: int, language: str = "python") -> str:
    """Fence a block, long enough to survive fences inside it.

    A prompt contains the module source in its own triple-backtick block, so
    wrapping it in three backticks silently truncates the document at the first
    inner fence. The outer fence has to be longer than anything it contains.
    """
    lines = text.rstrip().splitlines()
    if len(lines) > limit:
        head = lines[: limit - 6]
        tail = lines[-4:]
        body = head + ["", f"... {len(lines) - limit + 2} lines omitted ...", ""] + tail
    else:
        body = lines

    joined = "\n".join(body)
    longest = max((len(m) for m in re.findall(r"`+", joined)), default=0)
    fence = "`" * max(3, longest + 1)
    return f"{fence}{language}\n{joined}\n{fence}"


def _load_traces(run_dir: Path, module_id: str, arm: str) -> dict[str, dict]:
    trace_dir = run_dir / "traces" / module_id / arm
    if not trace_dir.exists():
        return {}
    traces: dict[str, dict] = {}
    for path in sorted(trace_dir.glob("*.json")):
        data = json.loads(path.read_text())
        traces[data["purpose"]] = data
    return traces


def _purpose_for(iteration: dict) -> list[str]:
    """Which trace files belong to this iteration."""
    phase = iteration["phase"]
    if phase == "pin":
        return ["pin", "pin-repair"]
    if phase == "kill":
        return [f"kill-{iteration['n']}"]
    if phase == "baseline":
        return ["baseline"]
    return []


def _survivor_lines(run_dir: Path, module_id: str, arm: str, limit: int = 10) -> list[str]:
    path = run_dir / "suites" / f"{module_id}.{arm}.survivors.txt"
    if not path.exists():
        return []
    lines = [line for line in path.read_text().splitlines() if line.strip()]
    shown = lines[:limit]
    if len(lines) > limit:
        shown.append(f"... and {len(lines) - limit} more")
    return shown


def render(run_dir: Path, record: dict) -> str:
    module_id = record["module_id"]
    arm = record["arm"]
    config = json.loads((run_dir / "config.json").read_text())
    traces = _load_traces(run_dir, module_id, arm)

    out: list[str] = [
        f"# Trajectory: `{module_id}`, {arm} arm",
        "",
        f"Run `{run_dir.name}` | model `{config['model']}` at temperature "
        f"{config['temperature']} | Python {config['python']} | revision "
        f"`{config['git_revision']}`",
        "",
        f"Final: **{record['score']:.1%}** mutation score, {record['n_tests']} tests, "
        f"{record['killed'] + record['timeout']} of {record['total']} mutants detected, "
        f"{record['wall_clock_s']:.0f}s, ${record.get('cost_usd', 0):.3f}.",
        "",
    ]

    if record.get("error"):
        out += [f"> This arm did not produce a usable suite: `{record['error']}`", ""]

    # The instructions are part of the trajectory. A reader cannot judge what the
    # agent did without seeing what it was told to do.
    if arm in ("agent", "baseline"):
        prompt_file = "pin.system.md" if arm == "agent" else "baseline.system.md"
        out += [
            "## The instructions",
            "",
            f"From `prompts/{prompt_file}`:",
            "",
            _fence((PROMPTS_DIR / prompt_file).read_text(), 200, "text"),
            "",
        ]
        if arm == "agent":
            out += [
                "The second phase uses `prompts/kill.system.md`, shown at the first",
                "iteration that reaches it.",
                "",
            ]

    for iteration in record.get("iterations", []):
        n = iteration["n"]
        phase = iteration["phase"]
        out += ["---", "", f"## Step {n} — phase `{phase}`", ""]

        for purpose in _purpose_for(iteration):
            trace = traces.get(purpose)
            if trace is None:
                continue

            if purpose == "pin-repair":
                out += [
                    "### Retry",
                    "",
                    "The first attempt was rejected by the harness. The agent was given",
                    "the actual rejection reason and asked to correct it, rather than",
                    "being resampled at the same prompt.",
                    "",
                ]
            if purpose.startswith("kill-") and n == 2:
                out += [
                    "### The second-phase instructions",
                    "",
                    _fence((PROMPTS_DIR / "kill.system.md").read_text(), 200, "text"),
                    "",
                ]

            out += [
                f"### What the agent was asked (call {trace['call']}, `{purpose}`)",
                "",
                _fence(trace["user"], MAX_PROMPT_LINES, "text"),
                "",
                "### What it returned",
                "",
                _fence(trace["response"], MAX_CODE_LINES),
                "",
            ]

        out += ["### What the harness did with it", ""]
        kept = iteration["tests_kept"]
        proposed = iteration["tests_proposed"]
        out.append("- Suite ran and passed against the unmodified module.")
        out.append(f"- Quality filters: kept **{kept}** of {proposed} proposed tests.")
        for entry in iteration.get("discarded", []):
            out.append(f"  - discarded `{entry}`")
        out.append(
            f"- Mutation campaign: score moved from {iteration['score_before']:.1%} "
            f"to **{iteration['score_after']:.1%}**, survivors "
            f"{iteration['survivors_before']} to {iteration['survivors_after']}."
        )
        if iteration.get("note"):
            out.append(f"- Note: {iteration['note']}")
        out.append("")

        gain = iteration["score_after"] - iteration["score_before"]
        out += ["### What that caused next", ""]
        if phase == "pin":
            out.append(
                f"{iteration['survivors_after']} mutants went undetected. That list, "
                "not a request for more tests, becomes the next prompt."
            )
        elif gain <= 0:
            out.append(
                f"No gain ({gain:+.1%}). One flat iteration counted toward the plateau "
                "budget; two in a row stop the loop."
            )
        else:
            out.append(f"Gain of {gain:+.1%}, so the loop continued.")
        out.append("")

    survivors = _survivor_lines(run_dir, module_id, arm)
    if survivors:
        out += [
            "---",
            "",
            "## What the finished suite still cannot detect",
            "",
            "These are reported to the user at the top of the generated file. Some are",
            "equivalent mutants that no test can catch; the rest are real gaps.",
            "",
            _fence("\n".join(survivors), 40, "text"),
            "",
        ]

    suite_path = run_dir / "suites" / f"{module_id}.{arm}.py"
    if suite_path.exists():
        out += [
            "---",
            "",
            "## The delivered suite",
            "",
            _fence(suite_path.read_text(), 80),
            "",
        ]

    return "\n".join(out)


def export(run_dir: Path, out_dir: Path, module: str = "", arm: str = "") -> list[Path]:
    records = [
        json.loads(line)
        for line in (run_dir / "records.jsonl").read_text().splitlines()
        if line.strip()
    ]
    selected = [
        r
        for r in records
        if (not module or r["module_id"] == module) and (not arm or r["arm"] == arm)
    ]
    if not selected:
        raise SystemExit("No matching records in that run.")

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for record in selected:
        safe = re.sub(r"[^A-Za-z0-9._-]", "_", f"{record['module_id']}.{record['arm']}")
        path = out_dir / f"{safe}.md"
        path.write_text(render(run_dir, record))
        written.append(path)
    return written
