"""Command line entry point.

`pindown pin FILE` is the product: point it at a module you inherited and get a
test suite plus an honest statement of what the suite still does not cover.
Everything else here exists to measure whether that suite is any good.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pindown.agent.llm import LLM
from pindown.agent.loop import run_agent
from pindown.config import RUNS_DIR, Budget, ModelConfig
from pindown.corpus.fetch import build_manifest, load_corpus
from pindown.eval.harness import ALL_ARMS, run_eval
from pindown.eval.score import write_results
from pindown.models import CorpusModule


def _resolve_run(value: str) -> Path:
    if value in ("latest", ""):
        path = RUNS_DIR / "latest"
        if not path.exists():
            raise SystemExit("No runs yet.")
        return path.resolve()
    path = Path(value)
    if not path.exists():
        path = RUNS_DIR / value
    if not path.exists():
        raise SystemExit(f"No such run: {value}")
    return path


def cmd_corpus(args: argparse.Namespace) -> int:
    budget = Budget()
    print("Fetching and validating corpus candidates.\n")
    admissions = build_manifest(budget)
    admitted = [a for a in admissions if a.admitted]
    print(f"\n{len(admitted)} of {len(admissions)} candidates admitted.")
    if admitted:
        print("\n  id                        lines  mutants  human tests  license")
        for a in admitted:
            print(
                f"  {a.id:24} {a.n_lines:6} {a.n_mutants:8} {a.n_reference_tests:12}  {a.license}"
            )
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    for module in load_corpus():
        print(f"{module.id:24} {module.n_lines:5} lines  {module.license:14} {module.origin}")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    cfg = ModelConfig()
    arms = [a.strip() for a in args.arms.split(",") if a.strip()]
    for arm in arms:
        if arm not in ALL_ARMS:
            raise SystemExit(f"Unknown arm {arm!r}. Choose from {', '.join(ALL_ARMS)}.")
    if any(a in ("baseline", "agent") for a in arms):
        cfg.require_key()

    only = [m.strip() for m in args.modules.split(",")] if args.modules else None
    modules = load_corpus(only)
    if args.limit:
        modules = modules[: args.limit]
    if not modules:
        raise SystemExit("No modules selected.")

    budget = Budget()
    print(
        f"{len(modules)} modules x {len(arms)} arms, "
        f"model {'stub' if cfg.stub else cfg.model}, "
        f"up to {budget.max_mutants} mutants per module.\n"
    )

    run_dir = run_eval(modules, arms, budget, cfg, tag=args.tag)
    path = write_results(run_dir)
    print(f"\n{path}\n")
    print(path.read_text())
    return 0


def cmd_score(args: argparse.Namespace) -> int:
    run_dir = _resolve_run(args.run)
    path = write_results(run_dir)
    print(path.read_text())
    return 0


def cmd_pin(args: argparse.Namespace) -> int:
    """Run the agent against one module and write the suite next to it."""
    cfg = ModelConfig()
    cfg.require_key()
    budget = Budget()

    if args.file:
        source_path = Path(args.file).resolve()
        if not source_path.exists():
            raise SystemExit(f"No such file: {source_path}")
        module = CorpusModule(
            id=source_path.stem,
            import_name=source_path.stem,
            source_path=source_path,
            reference_test_path=source_path,
            origin=str(source_path),
            license="local",
            n_lines=len(source_path.read_text().splitlines()),
        )
    else:
        matches = [m for m in load_corpus() if m.id == args.module]
        if not matches:
            raise SystemExit(f"No corpus module {args.module!r}. Try `pindown list`.")
        module = matches[0]

    out_dir = Path(args.out).resolve() if args.out else Path.cwd()
    out_dir.mkdir(parents=True, exist_ok=True)
    trace_dir = out_dir / f"{module.id}.traces"

    print(f"Pinning {module.id} ({module.n_lines} lines) with {cfg.model}.\n")
    llm = LLM(cfg, trace_dir=trace_dir, max_calls=budget.max_llm_calls)
    result = run_agent(module, llm, budget, progress=True)

    if result.error:
        print(f"\nFailed: {result.error}")
        return 1

    suite_path = out_dir / f"test_{module.import_name}_characterization.py"
    suite_path.write_text(_annotate(result, module))
    print(f"\n{suite_path}")
    print(
        f"{result.suite.n_tests} tests, {result.report.score:.1%} mutation score, "
        f"{len(result.report.survivors)} of {result.report.total} mutants still undetected, "
        f"${result.usage.cost(cfg):.3f}, {result.wall_clock_s:.0f}s."
    )
    return 0


def _annotate(result, module: CorpusModule) -> str:
    """Prepend the honest caveat.

    A characterization suite that arrives without a statement of what it does not
    cover invites the reader to trust it more than they should. The survivor count
    is the one number that belongs at the top of the file.
    """
    report = result.report
    header = [
        f'"""Characterization tests for `{module.import_name}`, generated by pindown.',
        "",
        "These tests record what the module does today. They are not a judgement",
        "about what it should do. If one fails after a change, the change altered",
        "observable behavior -- decide whether that was intended.",
        "",
        f"Mutation score: {report.score:.1%} "
        f"({report.killed + report.timeout} of {report.total} single-point changes detected).",
    ]
    if report.survivors:
        header += [
            "",
            f"{len(report.survivors)} changes are still undetected, including:",
            "",
        ]
        for mutant in report.survivors[:8]:
            header.append(f"  line {mutant.lineno}: {mutant.description}")
        if len(report.survivors) > 8:
            header.append(f"  ... and {len(report.survivors) - 8} more.")
        header += [
            "",
            "Some of those are equivalent mutants that no test can catch. The rest",
            "are real gaps, and they are the places to look first if you are about",
            "to change this module.",
        ]
    header += ['"""', "", ""]
    return "\n".join(header) + result.suite.source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pindown", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("corpus", help="fetch and validate the evaluation corpus")
    p.set_defaults(func=cmd_corpus)

    p = sub.add_parser("list", help="list admitted corpus modules")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("run", help="run the evaluation")
    p.add_argument("--arms", default=",".join(ALL_ARMS))
    p.add_argument("--modules", default="", help="comma separated module ids")
    p.add_argument("--limit", type=int, default=0)
    p.add_argument("--tag", default="")
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("score", help="regenerate tables from a run log")
    p.add_argument("--run", default="latest")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("pin", help="generate a characterization suite for one module")
    p.add_argument("--module", default="", help="corpus module id")
    p.add_argument("--file", default="", help="path to any single-file module")
    p.add_argument("--out", default="", help="where to write the suite")
    p.set_defaults(func=cmd_pin)

    args = parser.parse_args(argv)
    if args.command == "pin" and not (args.module or args.file):
        parser.error("pin needs --module or --file")
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
