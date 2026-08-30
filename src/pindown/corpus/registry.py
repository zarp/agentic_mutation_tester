"""What the corpus is, and why it is shaped this way.

Every module here must satisfy four constraints, and the validator enforces all
four rather than trusting this list:

Single file, standard library only. The harness runs a module and a test file
alone in a temp directory. That keeps a mutation campaign to a few hundred
subprocess runs instead of a container per mutant, which is the difference
between an evaluation that finishes in a hackathon and one that does not.

A real human-written test suite. This is the ceiling. Without it the comparison
is agent-versus-prompt, which tells you which prompt is better but not whether
either is good enough to use.

Real code from a real project. Code written for the benchmark would be code
written to be easy to test.

A permissive license, recorded per module and reproduced with the fetched source.

Most of the corpus comes from boltons, which is unusually well suited: a large
collection of genuinely independent single-file utility modules, one BSD license,
and a maintained pytest suite for each. The remaining modules come from elsewhere
so the result does not describe one project's house style.
"""

from __future__ import annotations

from dataclasses import dataclass, field

BOLTONS_REF = "23.1.1"
BOLTONS_LICENSE = "BSD-3-Clause"

# boltons tests import through the package. The harness runs the module standalone,
# so the import form has to be rewritten. Nothing else about the tests is touched.
BOLTONS_REWRITES: tuple[tuple[str, str], ...] = (
    ("from boltons.", "from "),
    ("from boltons import ", "import "),
    ("import boltons.", "import "),
)


@dataclass(frozen=True)
class ModuleSpec:
    id: str
    import_name: str
    repo: str
    ref: str
    module_path: str
    test_path: str
    license: str
    note: str = ""
    rewrites: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    @property
    def origin(self) -> str:
        return f"https://github.com/{self.repo}/blob/{self.ref}/{self.module_path}"

    def raw_url(self, path: str) -> str:
        return f"https://raw.githubusercontent.com/{self.repo}/{self.ref}/{path}"


def _boltons(name: str, note: str = "") -> ModuleSpec:
    return ModuleSpec(
        id=f"boltons.{name}",
        import_name=name,
        repo="mahmoud/boltons",
        ref=BOLTONS_REF,
        module_path=f"boltons/{name}.py",
        test_path=f"tests/test_{name}.py",
        license=BOLTONS_LICENSE,
        note=note,
        rewrites=BOLTONS_REWRITES,
    )


CANDIDATES: list[ModuleSpec] = [
    _boltons("strutils", "string helpers; lots of branchy formatting logic"),
    _boltons("mathutils", "small and numeric; every mutant is reachable"),
    _boltons("listutils", "index arithmetic, which is where off-by-one mutants live"),
    _boltons("dictutils", "stateful container with an involved delete path"),
    _boltons("setutils", "container arithmetic over two backing structures"),
    _boltons("formatutils", "parses format strings; heavy on string constants"),
    _boltons("timeutils", "date arithmetic without touching the wall clock"),
    _boltons("cacheutils", "eviction policies, where behavior depends on ordering"),
    _boltons("iterutils", "the largest module here; a deliberate hard case"),
    _boltons("queueutils", "priority queues built on heapq"),
    _boltons("statsutils", "numeric summaries with several edge cases at n=0 and n=1"),
    _boltons("tableutils", "html and text rendering; long string constants"),
    _boltons("funcutils", "introspection-heavy, so many mutants are unreachable"),
    _boltons("namedutils", "code generation via exec, which resists testing"),
    _boltons("urlutils", "parsing with a large percent-encoding table"),
    ModuleSpec(
        id="semver",
        import_name="semver",
        repo="python-semver/python-semver",
        ref="2.13.0",
        module_path="semver.py",
        test_path="test_semver.py",
        license="BSD-3-Clause",
        note="version comparison; dense with boundary comparisons",
    ),
    ModuleSpec(
        id="xmltodict",
        import_name="xmltodict",
        repo="martinblech/xmltodict",
        ref="v0.13.0",
        module_path="xmltodict.py",
        test_path="tests/test_xmltodict.py",
        license="MIT",
        note="SAX callbacks and nested state; different shape to the rest",
    ),
]

BY_ID = {spec.id: spec for spec in CANDIDATES}
