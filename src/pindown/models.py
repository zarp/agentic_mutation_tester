"""Shared types.

Every stage of the pipeline speaks in these. Keeping the vocabulary in one place
is what lets the eval harness treat the human suite, the baseline suite and the
agent suite as three instances of exactly the same thing.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path


class Arm(str, Enum):
    """Who wrote the test suite being measured."""

    HUMAN = "human"
    BASELINE = "baseline"
    AGENT = "agent"


@dataclass(frozen=True)
class CorpusModule:
    """A single-file, stdlib-only module under test.

    `reference_test_path` is the project's own test file. It is the ceiling we
    measure against and it is never shown to any agent.
    """

    id: str
    import_name: str
    source_path: Path
    reference_test_path: Path
    origin: str
    license: str
    n_lines: int = 0

    @property
    def source(self) -> str:
        return self.source_path.read_text()


class Outcome(str, Enum):
    KILLED = "killed"
    SURVIVED = "survived"
    TIMEOUT = "timeout"


@dataclass(frozen=True)
class Mutant:
    """One single-point change to the module under test.

    `id` is stable across runs because it is derived from the deterministic node
    index rather than from generation order, so survivor sets from two different
    runs can be compared directly.
    """

    id: str
    operator: str
    lineno: int
    description: str
    original_line: str
    source: str = field(repr=False, default="")

    def brief(self) -> str:
        """One-line rendering for a prompt. Deliberately omits the full source."""
        return f"line {self.lineno}: {self.description}\n    {self.original_line.strip()}"


@dataclass
class MutantResult:
    mutant_id: str
    outcome: Outcome
    duration_s: float


@dataclass
class MutationReport:
    module_id: str
    arm: str
    killed: int
    survived: int
    timeout: int
    survivors: list[Mutant] = field(default_factory=list, repr=False)
    results: list[MutantResult] = field(default_factory=list, repr=False)
    duration_s: float = 0.0

    @property
    def total(self) -> int:
        return self.killed + self.survived + self.timeout

    @property
    def score(self) -> float:
        """Fraction of mutants detected.

        A timeout counts as killed: the mutant changed observable behavior enough
        to hang the suite, which is a detection. Equivalent mutants are not
        excluded, because identifying them is undecidable in general -- but they
        depress every arm's score by the same amount, so the comparison holds.
        """
        if self.total == 0:
            return 0.0
        return (self.killed + self.timeout) / self.total

    def summary(self) -> str:
        return (
            f"{self.module_id} [{self.arm}] "
            f"score={self.score:.1%} killed={self.killed} survived={self.survived} "
            f"timeout={self.timeout}"
        )


@dataclass
class PytestResult:
    """Structured outcome of running one test file against one module version."""

    ok: bool
    collected: int
    passed: int
    failed: int
    errors: int
    duration_s: float
    stdout: str = field(repr=False, default="")
    failed_tests: list[str] = field(default_factory=list)
    collection_error: bool = False

    @property
    def usable(self) -> bool:
        """True when the file collected cleanly and every test passed.

        A characterization suite that does not pass against current behavior is
        not describing current behavior, so it is not usable at all.
        """
        return self.ok and not self.collection_error and self.collected > 0


@dataclass
class TestSuite:
    module_id: str
    arm: str
    source: str
    n_tests: int = 0
    discarded: list[str] = field(default_factory=list)


@dataclass
class IterationRecord:
    """One turn of the agent loop, kept so the trajectory can be replayed."""

    n: int
    phase: str
    tests_proposed: int
    tests_kept: int
    discarded: list[str]
    score_before: float
    score_after: float
    survivors_before: int
    survivors_after: int
    duration_s: float
    note: str = ""


@dataclass
class ModuleOutcome:
    """Everything one arm produced for one module. This is a row in records.jsonl."""

    module_id: str
    arm: str
    score: float
    killed: int
    survived: int
    timeout: int
    total: int
    n_tests: int
    suite_runtime_s: float
    wall_clock_s: float
    prompt_tokens: int = 0
    completion_tokens: int = 0
    cost_usd: float = 0.0
    iterations: list[IterationRecord] = field(default_factory=list)
    error: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)
