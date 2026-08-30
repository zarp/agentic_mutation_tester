.DEFAULT_GOAL := help
PY := .venv/bin/python
PINDOWN := .venv/bin/pindown

.PHONY: help setup preflight corpus test smoke free eval score trajectories demo lint clean

help:
	@echo "Run these in order."
	@echo ""
	@echo "  make setup      create .venv and install pindown            (~1 min)"
	@echo "  make preflight  check the environment before spending money (~2 min)"
	@echo "  make corpus     fetch and validate the 14 corpus modules    (~1 min, needs network)"
	@echo "  make test       run pindown's own test suite                (~10 s)"
	@echo ""
	@echo "  make free       human ceiling + fuzz baseline, no API key   (~15 min)"
	@echo "  make smoke      all four arms on two modules                (~6 min, ~\$$0.20)"
	@echo "  make eval       the headline run: four arms, all modules    (~33 min, ~\$$3)"
	@echo "  make score      regenerate tables from the last run         (instant)"
	@echo "  make trajectories  render readable agent trajectories      (instant)"
	@echo ""
	@echo "  make demo FILE=path/to/module.py    pin one of your own modules"

setup:
	python3 -m venv .venv
	$(PY) -m pip install --quiet --upgrade pip
	$(PY) -m pip install --quiet -e .
	@echo "Done. Copy .env.example to .env and add a key, or export PINDOWN_STUB_LLM=1."

preflight:
	./scripts/preflight.sh

corpus:
	$(PINDOWN) corpus

test:
	$(PY) -m pytest tests/ -q

# Everything below writes to runs/<timestamp>-<tag>/ and updates runs/latest.

free:
	$(PINDOWN) run --arms human,golden --tag free

# Two small modules, not the first two in the corpus. `--limit 2` would pick
# strutils (1311 lines, 400 mutants) and waste most of a smoke budget on one file.
smoke:
	$(PINDOWN) run --arms human,golden,baseline,agent --modules boltons.mathutils,boltons.formatutils --tag smoke

eval:
	$(PINDOWN) run --arms human,golden,baseline,agent --tag headline

score:
	$(PINDOWN) score --run latest

trajectories:
	$(PINDOWN) trajectory --run latest

demo:
	@test -n "$(FILE)" || (echo "usage: make demo FILE=path/to/module.py" && exit 1)
	$(PINDOWN) pin --file $(FILE) --out ./out

lint:
	$(PY) -m ruff check src tests
	$(PY) -m ruff format --check src tests

clean:
	rm -rf runs/* out .pytest_cache .ruff_cache
