"""Model access, with tracing that cannot be skipped.

Every call is written to the run's trace directory before the caller sees the
response. An agent trajectory you cannot read is not evidence, and a trace you
have to remember to enable is a trace you will not have when you need it.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from pindown.config import ModelConfig

CODE_FENCE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


@dataclass
class Usage:
    prompt_tokens: int = 0
    completion_tokens: int = 0
    calls: int = 0

    def add(self, prompt: int, completion: int) -> None:
        self.prompt_tokens += prompt
        self.completion_tokens += completion
        self.calls += 1

    def cost(self, cfg: ModelConfig) -> float:
        return (
            self.prompt_tokens * cfg.input_price_per_mtok
            + self.completion_tokens * cfg.output_price_per_mtok
        ) / 1_000_000


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class LLM:
    cfg: ModelConfig
    trace_dir: Path | None = None
    max_calls: int = 20
    max_retries: int = 4
    usage: Usage = field(default_factory=Usage)
    _client: object | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.trace_dir is not None:
            self.trace_dir.mkdir(parents=True, exist_ok=True)

    def _get_client(self):
        if self._client is None:
            from openai import OpenAI

            self._client = OpenAI(api_key=self.cfg.api_key, base_url=self.cfg.base_url)
        return self._client

    def complete(self, system: str, user: str, purpose: str) -> str:
        if self.usage.calls >= self.max_calls:
            raise BudgetExceeded(f"hit the {self.max_calls} call ceiling")

        started = time.monotonic()
        if self.cfg.stub:
            text = _stub_response(user)
            prompt_tokens = len(system + user) // 4
            completion_tokens = len(text) // 4
        else:
            text, prompt_tokens, completion_tokens = self._call_with_retry(system, user)

        self.usage.add(prompt_tokens, completion_tokens)
        self._trace(purpose, system, user, text, time.monotonic() - started)
        return text

    def _call_with_retry(self, system: str, user: str) -> tuple[str, int, int]:
        """Retry transient failures, fail fast on everything else.

        Rate limits and gateway errors are worth waiting out; a bad key or an
        exhausted quota is not, and retrying those just turns a clear error into
        a slow one. An evaluation that silently drops a module because of a
        thirty-second blip is a worse outcome than one that takes a minute longer.
        """
        from openai import APIConnectionError, APIStatusError, RateLimitError

        client = self._get_client()
        delay = 2.0
        last: Exception | None = None

        for attempt in range(self.max_retries):
            try:
                response = client.chat.completions.create(  # type: ignore[union-attr]
                    model=self.cfg.model,
                    temperature=self.cfg.temperature,
                    max_tokens=self.cfg.max_output_tokens,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
            except RateLimitError as exc:
                if "insufficient_quota" in str(exc) or "credit" in str(exc).lower():
                    raise
                last = exc
            except APIConnectionError as exc:
                last = exc
            except APIStatusError as exc:
                if exc.status_code < 500:
                    raise
                last = exc
            else:
                text = response.choices[0].message.content or ""
                usage = response.usage
                return (
                    text,
                    usage.prompt_tokens if usage else 0,
                    usage.completion_tokens if usage else 0,
                )

            if attempt < self.max_retries - 1:
                time.sleep(delay)
                delay *= 2

        raise RuntimeError(f"model call failed after {self.max_retries} attempts: {last}")

    def _trace(self, purpose: str, system: str, user: str, response: str, duration: float) -> None:
        if self.trace_dir is None:
            return
        n = self.usage.calls
        path = self.trace_dir / f"{n:03d}-{purpose}.json"
        path.write_text(
            json.dumps(
                {
                    "call": n,
                    "purpose": purpose,
                    "model": "stub" if self.cfg.stub else self.cfg.model,
                    "temperature": self.cfg.temperature,
                    "duration_s": round(duration, 2),
                    "system": system,
                    "user": user,
                    "response": response,
                },
                indent=2,
            )
        )


def extract_code(text: str) -> str:
    """Pull Python out of a model response.

    Models fence code inconsistently, and a response that is already bare code is
    common enough to be worth handling rather than failing on.
    """
    blocks = CODE_FENCE.findall(text)
    if blocks:
        return "\n\n".join(b.strip() for b in blocks)
    stripped = text.strip()
    if stripped.startswith(("import ", "from ", "def ", "#")):
        return stripped
    return stripped


_STUB_MARKER = "# generated by the stub model"


def _stub_response(user: str) -> str:
    """A canned reply so the whole pipeline runs with no API key.

    It deliberately produces a weak suite: one real assertion and one vacuous
    test, so a stub run still exercises the quality filters and still shows a
    non-trivial survivor list. It is a smoke test for the plumbing, not a
    baseline -- `pindown run --arm golden` is the free baseline that means
    something.
    """
    match = re.search(r"MODULE_IMPORT_NAME:\s*(\w+)", user)
    module = match.group(1) if match else "module_under_test"
    return f"""```python
{_STUB_MARKER}
import {module}


def test_module_imports():
    assert {module} is not None


def test_smoke_touches_public_names():
    names = [n for n in dir({module}) if not n.startswith("_")]
    assert isinstance(names, list)
```"""
