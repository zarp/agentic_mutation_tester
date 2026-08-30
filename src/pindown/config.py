"""Budgets, provenance and every knob that decides whether a run terminates.

Anything that could make a run hang, cost unbounded money, or differ between two
machines lives here rather than being scattered through the pipeline.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(REPO_ROOT / ".env")


def _int(name: str, default: int) -> int:
    return int(os.environ.get(name, default))


def _float(name: str, default: float) -> float:
    return float(os.environ.get(name, default))


@dataclass(frozen=True)
class Budget:
    """Termination guarantees.

    The loop stops on whichever of these binds first. `plateau_patience` is the
    interesting one: the agent stops when mutation score stops improving rather
    than at a fixed iteration count, because modules differ enormously in how
    much room there is.
    """

    max_iterations: int = _int("PINDOWN_MAX_ITERATIONS", 6)
    plateau_patience: int = _int("PINDOWN_PLATEAU_PATIENCE", 2)
    min_gain: float = _float("PINDOWN_MIN_GAIN", 0.01)
    max_wall_clock_s: float = _float("PINDOWN_MAX_WALL_CLOCK_S", 900.0)
    max_llm_calls: int = _int("PINDOWN_MAX_LLM_CALLS", 20)

    # Per-subprocess limits. A generated test can loop forever; this is the only
    # thing standing between the harness and a hung run.
    pytest_timeout_s: float = _float("PINDOWN_PYTEST_TIMEOUT_S", 30.0)
    mutant_timeout_multiplier: float = _float("PINDOWN_MUTANT_TIMEOUT_MULT", 4.0)
    mutant_timeout_floor_s: float = _float("PINDOWN_MUTANT_TIMEOUT_FLOOR_S", 5.0)

    # Flake detection. Three runs is enough to catch clock, ordering and hash
    # seed dependence, which is the overwhelming majority of what models emit.
    flake_reruns: int = _int("PINDOWN_FLAKE_RERUNS", 3)

    # Cap on mutants per module, applied by deterministic stride sampling so the
    # same subset is chosen on every run and every arm.
    max_mutants: int = _int("PINDOWN_MAX_MUTANTS", 400)

    mutation_workers: int = _int("PINDOWN_MUTATION_WORKERS", max(2, (os.cpu_count() or 4) - 1))


@dataclass(frozen=True)
class ModelConfig:
    api_key: str = field(default_factory=lambda: os.environ.get("PINDOWN_API_KEY", ""))
    base_url: str = field(
        default_factory=lambda: os.environ.get("PINDOWN_BASE_URL", "https://api.openai.com/v1")
    )
    model: str = field(default_factory=lambda: os.environ.get("PINDOWN_MODEL", "gpt-4.1-2025-04-14"))
    temperature: float = _float("PINDOWN_TEMPERATURE", 0.0)
    max_output_tokens: int = _int("PINDOWN_MAX_OUTPUT_TOKENS", 4096)
    stub: bool = field(default_factory=lambda: os.environ.get("PINDOWN_STUB_LLM", "0") == "1")

    # Published per-million-token prices, used only to report an approximate cost.
    # Override when you point at a different model.
    input_price_per_mtok: float = _float("PINDOWN_INPUT_PRICE", 2.00)
    output_price_per_mtok: float = _float("PINDOWN_OUTPUT_PRICE", 8.00)

    def require_key(self) -> None:
        if self.stub:
            return
        if not self.api_key:
            raise SystemExit(
                "No PINDOWN_API_KEY. Copy .env.example to .env and add a key, "
                "or set PINDOWN_STUB_LLM=1 to run the pipeline without a model."
            )


def git_revision() -> str:
    """Recorded in every run so a result can be tied back to the code that made it."""
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        rev = out.stdout.strip()
        dirty = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        ).stdout.strip()
        return f"{rev}{'-dirty' if dirty else ''}" if rev else "unknown"
    except Exception:
        return "unknown"


CORPUS_DIR = REPO_ROOT / "corpus"
MODULES_DIR = CORPUS_DIR / "modules"
RUNS_DIR = REPO_ROOT / "runs"
PROMPTS_DIR = REPO_ROOT / "prompts"
