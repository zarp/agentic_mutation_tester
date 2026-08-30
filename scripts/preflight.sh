#!/usr/bin/env bash
# Go / no-go before spending money on a full run.
#
# Each check below has failed on a real machine during development. The point is
# to fail in ten seconds with a clear reason rather than forty minutes into an
# evaluation with a stack trace.

set -uo pipefail

PY=.venv/bin/python
PINDOWN=.venv/bin/pindown
FAILED=0

pass() { printf "  ok    %s\n" "$1"; }
fail() { printf "  FAIL  %s\n    %s\n" "$1" "$2"; FAILED=1; }

echo "pindown preflight"
echo

# 1. Interpreter and install.
if [ ! -x "$PY" ]; then
  fail "virtualenv" "No .venv. Run: make setup"
  exit 1
fi
pass "virtualenv at .venv"

if ! "$PY" -c "import pindown" 2>/dev/null; then
  fail "pindown importable" "Run: make setup"
else
  pass "pindown importable ($("$PY" -c 'import platform; print("python "+platform.python_version())'))"
fi

# 2. The mutation engine, which every reported number depends on.
if "$PY" -m pytest tests/test_operators.py -q >/dev/null 2>&1; then
  pass "mutation engine self-tests"
else
  fail "mutation engine self-tests" "Run: .venv/bin/python -m pytest tests/test_operators.py"
fi

# 3. Subprocess execution actually works here. Fails inside some containers and
#    on filesystems mounted noexec.
if "$PY" - <<'EOF' >/dev/null 2>&1
from pindown.runtime.pytest_runner import run_suite
r = run_suite("m", "def f():\n    return 1\n", "import m\n\ndef test_f():\n    assert m.f() == 1\n", 60.0)
raise SystemExit(0 if r.usable else 1)
EOF
then
  pass "sandboxed pytest subprocess"
else
  fail "sandboxed pytest subprocess" "pytest could not run in a temp dir; check TMPDIR is not noexec"
fi

# 4. Corpus present and admitted.
if [ -f corpus/modules/manifest.json ]; then
  N=$("$PY" -c "import json;print(sum(1 for a in json.load(open('corpus/modules/manifest.json')) if a['admitted']))")
  if [ "$N" -ge 10 ]; then
    pass "corpus: $N modules admitted"
  else
    fail "corpus" "only $N modules admitted, expected at least 10. Run: make corpus"
  fi
else
  fail "corpus" "No manifest. Run: make corpus"
fi

# 5. Model access. Checked with one real call, because a key that is present and
#    a key that works are different things, and finding out later is expensive.
if [ "${PINDOWN_STUB_LLM:-0}" = "1" ]; then
  pass "model access skipped (PINDOWN_STUB_LLM=1)"
else
  OUT=$("$PY" - <<'EOF' 2>&1
from pindown.agent.llm import LLM
from pindown.config import ModelConfig
cfg = ModelConfig()
if not cfg.api_key:
    print("NOKEY"); raise SystemExit(0)
try:
    LLM(cfg, max_calls=1).complete("Reply with the single word: ready.", "ready?", "preflight")
    print("OK")
except Exception as exc:
    print(f"ERR {type(exc).__name__}: {str(exc)[:160]}")
EOF
)
  case "$OUT" in
    OK*)    pass "model access ($("$PY" -c 'from pindown.config import ModelConfig; print(ModelConfig().model)'))" ;;
    NOKEY*) fail "model access" "No PINDOWN_API_KEY. Copy .env.example to .env, or set PINDOWN_STUB_LLM=1 for the free arms." ;;
    *)      fail "model access" "$OUT" ;;
  esac
fi

echo
if [ "$FAILED" -eq 0 ]; then
  echo "Ready. Next: make free (no key needed) or make smoke (needs a key)."
else
  echo "Fix the failures above before running an evaluation."
fi
exit "$FAILED"
