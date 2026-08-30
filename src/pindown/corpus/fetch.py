"""Fetching and validating the corpus.

Fetching is separated from validating on purpose. The registry is a list of
candidates, not a list of guarantees, and the validator is what turns one into
the other. A module is admitted only if it imports standalone, its human test
suite passes standalone, and it produces enough mutants for a score to mean
anything. Everything that fails is reported with the reason rather than dropped
quietly, because the exclusions are part of what a reader needs to judge the
corpus.
"""

from __future__ import annotations

import ast
import json
import sys
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

from pindown.config import MODULES_DIR, Budget
from pindown.corpus.registry import CANDIDATES, ModuleSpec
from pindown.models import CorpusModule
from pindown.mutation.operators import build_mutants
from pindown.runtime.pytest_runner import run_suite

MANIFEST = MODULES_DIR / "manifest.json"
MIN_MUTANTS = 40
MAX_MODULE_LINES = 1400


@dataclass
class Admission:
    id: str
    admitted: bool
    reason: str
    n_lines: int = 0
    n_mutants: int = 0
    n_reference_tests: int = 0
    license: str = ""
    origin: str = ""
    note: str = ""


def _download(url: str, timeout: float = 30.0) -> str | None:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError):
        return None


def module_dir(spec: ModuleSpec) -> Path:
    return MODULES_DIR / spec.id


def fetch_one(spec: ModuleSpec, force: bool = False) -> tuple[Path, str] | None:
    """Download one candidate. Returns its directory, or None with a reason logged."""
    target = module_dir(spec)
    module_file = target / f"{spec.import_name}.py"
    test_file = target / "reference_test.py"

    if module_file.exists() and test_file.exists() and not force:
        return target, "cached"

    source = _download(spec.raw_url(spec.module_path))
    if source is None:
        return None
    tests = _download(spec.raw_url(spec.test_path))
    if tests is None:
        return None

    for old, new in spec.rewrites:
        tests = tests.replace(old, new)
        source = source.replace(old, new)

    target.mkdir(parents=True, exist_ok=True)
    module_file.write_text(source)
    test_file.write_text(tests)
    (target / "PROVENANCE.txt").write_text(
        f"module:  {spec.origin}\n"
        f"tests:   https://github.com/{spec.repo}/blob/{spec.ref}/{spec.test_path}\n"
        f"license: {spec.license}\n"
        f"ref:     {spec.ref}\n"
        "\n"
        "Fetched by pindown. The only edit applied is the import rewrite listed in\n"
        "the registry, which lets the module run standalone.\n"
    )
    return target, "downloaded"


def _unguarded_import_roots(node: ast.AST, guarded: bool = False) -> set[str]:
    """Root packages imported outside a `try` block.

    An import inside `try`/`except ImportError` is a compatibility shim. Half of
    the useful single-file modules on PyPI still carry a Python 2 fallback that
    never executes on a modern interpreter, and rejecting those would throw away
    good corpus material for a dependency that is never actually imported.
    """
    roots: set[str] = set()

    if isinstance(node, ast.Import) and not guarded:
        roots |= {alias.name.split(".")[0] for alias in node.names}
    elif isinstance(node, ast.ImportFrom) and not guarded and node.level == 0 and node.module:
        roots.add(node.module.split(".")[0])

    for child in ast.iter_child_nodes(node):
        roots |= _unguarded_import_roots(child, guarded or isinstance(node, ast.Try))

    return roots


def _stdlib_only(source: str, allow: set[str] | None = None) -> tuple[bool, str]:
    """Reject anything that needs a package installed.

    A module that needs a dependency needs an environment, and an environment per
    module is what makes this kind of evaluation impossible to reproduce.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return False, f"does not parse: {exc}"

    permitted = sys.stdlib_module_names | (allow or set())
    external = sorted(r for r in _unguarded_import_roots(tree) if r not in permitted)
    if external:
        return False, f"imports outside the standard library: {', '.join(external)}"
    return True, ""


def validate_one(spec: ModuleSpec, budget: Budget) -> Admission:
    fetched = fetch_one(spec)
    if fetched is None:
        return Admission(spec.id, False, "could not download module or tests")

    target, _ = fetched
    source = (target / f"{spec.import_name}.py").read_text()
    tests = (target / "reference_test.py").read_text()

    n_lines = len(source.splitlines())
    if n_lines > MAX_MODULE_LINES:
        return Admission(spec.id, False, f"module is {n_lines} lines, over the cap", n_lines=n_lines)

    ok, reason = _stdlib_only(source)
    if not ok:
        return Admission(spec.id, False, reason, n_lines=n_lines)

    ok, reason = _stdlib_only(tests, allow={"pytest", spec.import_name})
    if not ok:
        return Admission(spec.id, False, f"reference tests {reason}", n_lines=n_lines)

    mutants = build_mutants(source, limit=budget.max_mutants)
    if len(mutants) < MIN_MUTANTS:
        return Admission(
            spec.id,
            False,
            f"only {len(mutants)} mutants, too few for a stable score",
            n_lines=n_lines,
            n_mutants=len(mutants),
        )

    result = run_suite(spec.import_name, source, tests, timeout_s=120.0)
    if not result.usable:
        detail = "does not import" if result.collection_error else f"{result.failed} failing"
        return Admission(
            spec.id,
            False,
            f"reference suite {detail} when run standalone",
            n_lines=n_lines,
            n_mutants=len(mutants),
        )

    return Admission(
        spec.id,
        True,
        "ok",
        n_lines=n_lines,
        n_mutants=len(mutants),
        n_reference_tests=result.collected,
        license=spec.license,
        origin=spec.origin,
        note=spec.note,
    )


def build_manifest(budget: Budget, verbose: bool = True) -> list[Admission]:
    MODULES_DIR.mkdir(parents=True, exist_ok=True)
    admissions: list[Admission] = []
    for spec in CANDIDATES:
        admission = validate_one(spec, budget)
        admissions.append(admission)
        if verbose:
            mark = "admitted" if admission.admitted else "rejected"
            print(f"  {mark:9} {spec.id:24} {admission.reason}", flush=True)

    MANIFEST.write_text(json.dumps([asdict(a) for a in admissions], indent=2))
    return admissions


def load_corpus(only: list[str] | None = None) -> list[CorpusModule]:
    """The admitted modules, in manifest order."""
    if not MANIFEST.exists():
        raise SystemExit("No corpus manifest. Run `make corpus` first.")

    admissions = json.loads(MANIFEST.read_text())
    modules: list[CorpusModule] = []
    for entry in admissions:
        if not entry["admitted"]:
            continue
        if only and entry["id"] not in only:
            continue
        spec = next(s for s in CANDIDATES if s.id == entry["id"])
        target = module_dir(spec)
        modules.append(
            CorpusModule(
                id=spec.id,
                import_name=spec.import_name,
                source_path=target / f"{spec.import_name}.py",
                reference_test_path=target / "reference_test.py",
                origin=spec.origin,
                license=spec.license,
                n_lines=entry["n_lines"],
            )
        )
    return modules
