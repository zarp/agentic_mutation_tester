# Reproduction guide

Written for someone starting from a clean machine with nothing installed but
Python and git. No Docker, no GPU, no database, no accounts beyond one model
endpoint - and the first half of this guide needs no account at all.

## What you need

| | |
| --- | --- |
| OS | Linux or macOS. Developed on Ubuntu 24.04, kernel 6.18, x86_64 |
| Python | 3.11 or newer. Developed on 3.12.3 |
| Disk | ~150 MB: 840 KB of corpus, the rest is the virtualenv |
| Network | Only for `make setup` and `make corpus`. Everything after that is local, except calls to the model endpoint |
| Cores | Any. The mutation campaign uses `cpu_count - 1` workers, so more cores make it proportionally faster |
| Accounts | None for the free path. One OpenAI-compatible endpoint for the full comparison |

macOS note: the child-process watchdog uses `SIGALRM` and `setitimer`, which are
POSIX. It works on macOS and Linux and will not work on Windows without WSL.

Pinned versions, from the environment the results were produced in:

```
openai==3.6.0        pytest==8.3.3        python-dotenv==1.0.1
httpx==0.28.1        pydantic==2.13.5     Python 3.12.3 (GCC 13.3.0)
```

`openai` is pinned to 3.x deliberately. Version 1.51 breaks against
`httpx>=0.28` with `Client.__init__() got an unexpected keyword argument
'proxies'`, which is worth knowing if you pin differently.

## Step 1 - Setup

```bash
git clone <this repo> && cd pindown
make setup
```

Creates `.venv` and installs the package. Takes about a minute. Expect:

```
Done. Copy .env.example to .env and add a key, or export PINDOWN_STUB_LLM=1.
```

## Step 2 - Fetch the corpus

```bash
make corpus
```

Downloads 17 candidate modules and their upstream test suites from pinned git
tags, then admits the ones that pass validation. Needs network. About a minute.

Nothing is committed to this repository, so this step is required. Expect
exactly this, and treat any difference as a problem worth understanding:

```
  admitted  boltons.strutils         ok
  admitted  boltons.mathutils        ok
  admitted  boltons.listutils        ok
  admitted  boltons.dictutils        ok
  admitted  boltons.setutils         ok
  admitted  boltons.formatutils      ok
  admitted  boltons.timeutils        ok
  admitted  boltons.cacheutils       ok
  rejected  boltons.iterutils        module is 1603 lines, over the cap
  rejected  boltons.queueutils       only 30 mutants, too few for a stable score
  admitted  boltons.statsutils       ok
  admitted  boltons.tableutils       ok
  admitted  boltons.funcutils        ok
  admitted  boltons.namedutils       ok
  rejected  boltons.urlutils         module is 1596 lines, over the cap
  admitted  semver                   ok
  admitted  xmltodict                ok

14 of 17 candidates admitted.
```

The three rejections are expected and are part of the result. Each admitted
module lands in `corpus/modules/<id>/` with the module, its upstream test suite,
and a `PROVENANCE.txt` recording the source URL, tag and license.

## Step 3 - Check the environment before spending anything

```bash
make test        # pindown's own suite: 45 tests, ~10 s
make preflight   # ~30 s
```

`make preflight` is the go/no-go. Every check in it has failed on a real machine
during development, which is why it exists.

```
  ok    virtualenv at .venv
  ok    pindown importable (python 3.12.3)
  ok    mutation engine self-tests
  ok    sandboxed pytest subprocess
  ok    corpus: 14 modules admitted
  ok    model access (gpt-4.1-2025-04-14)
```

Without a key, run `PINDOWN_STUB_LLM=1 make preflight`; the last check is skipped
and everything else still applies.

## Step 4a - The free path, no API key

```bash
make free
```

Runs the two arms that need no model: the human ceiling (each project's own test
suite) and the model-free fuzz baseline. About five minutes of wall clock on
eight cores, and it costs nothing.

This is the fastest way to confirm the whole machine works, because it exercises
the mutation engine, the sandbox, the quality filters, the scoring and the
report, and it produces two of the four headline numbers.

Expected result. The exact figures are deterministic given the same corpus tags
and Python version, because temperature does not enter into either arm:

| Metric | Human tests | Golden fuzz baseline |
| --- | --- | --- |
| Median mutation score | 43.9% | 5.0% |
| Mean mutation score | 41.1% | 8.4% |
| Range | 5.0% – 75.9% | 0.0% – 33.9% |

If your medians land within a point or two of these, the harness is working. A
large deviation usually means a corpus module resolved to a different tag.

## Step 4b - The full comparison, needs a model

```bash
cp .env.example .env
$EDITOR .env          # set PINDOWN_API_KEY, and pin an exact PINDOWN_MODEL
make smoke            # 4 arms, 2 modules,  ~6 min,  ~$0.20
make eval             # 4 arms, 14 modules, ~33 min, ~$3
```

Run `make smoke` first, always. It is the same code path as `make eval` over two
modules, so it catches a bad key, a wrong model name or a changed response format
for twenty cents instead of four dollars.

Expected smoke result on `boltons.mathutils` and `boltons.formatutils`:

| Metric | Human | Golden | One-shot | Agent |
| --- | ---: | ---: | ---: | ---: |
| Median mutation score | 57.8% | 8.6% | 43.5% | 91.3% |

`mathutils` should reach 100% on the agent arm; `formatutils` should land near
83%. If both arms fail with a quota or auth error, fix the key before running
`make eval`.

Expected headline result after `make eval` completes (~33 minutes, ~$3 on
`gpt-4.1-2025-04-14`):

| Metric | Human | Golden | One-shot | Agent |
| --- | ---: | ---: | ---: | ---: |
| Median mutation score | 43.9% | 5.0% | 54.8% | 62.7% |
| Mean mutation score | 41.0% | 8.4% | 52.3% | 57.5% |
| Total model cost | $0 | $0 | ~$0.52 | ~$2.60 |
| Modules with no usable suite | 0 | 1 | 1 | 2 |

The agent should beat the human ceiling on most modules but fail on `semver`
(parse error on a 1259-line module) and `dictutils`. That is expected and
documented in the README changelog - do not treat it as a broken run.

To compare exactly without re-spending API credits, use the committed run in
`evidence/headline-14-modules/` (records, suites, traces, and trajectories).

Costs are computed from logged token counts at published `gpt-4.1-2025-04-14`
prices, not estimated. Set `PINDOWN_INPUT_PRICE` and `PINDOWN_OUTPUT_PRICE` if you
point at a different model, or the reported cost will be wrong.

Any OpenAI-compatible endpoint works:

```bash
PINDOWN_BASE_URL=https://openrouter.ai/api/v1
PINDOWN_MODEL=anthropic/claude-sonnet-4
```

## Step 5 - Read the results

```bash
make score                                    # regenerate every table
make trajectories                             # readable agent trajectories
pindown trajectory --run latest --arm agent   # same, with optional filters
```

`make score` rewrites `runs/latest/results.md`, `runs/latest/metrics.json`, and
the results block inside `README.md`. No number in the README is typed by hand;
the only way one gets there is by coming out of a run log.

Each run directory contains:

```
config.json      git revision, python version, model, temperature, every budget
records.jsonl    one row per module per arm, the raw result
suites/          every generated test file, and its surviving-mutant list
traces/          every prompt and every response, per module per arm
trajectories/    the above stitched into one readable document per arm
crashes/         full tracebacks, if any arm crashed
results.md       the tables
```

## Step 6 (Optional / Extra) - Run it on any other code you want to test

```bash
pindown pin --file path/to/your_module.py --out ./out
```

Writes `out/test_<module>_characterization.py`, with a header stating the
mutation score achieved and listing what the suite still cannot detect.

The module must import on its own and must not require third-party packages.

## Determinism, and where it stops

Deterministic: mutant generation and ids, mutant selection under a cap, the human
arm, the fuzz baseline, and every filter decision except where a genuinely
non-deterministic test is involved - which is the point of that filter.

Not deterministic: the model arms. Temperature is 0 and the model version is
pinned. However providers do not guarantee identical outputs
across calls. Expect the agent's per-module score to move by a few points between
runs. If you need to compare exactly, compare against the committed run in
`evidence/headline-14-modules/` rather than re-running.

Mutation scores are also sensitive to `PINDOWN_MAX_MUTANTS` (default 400). A
module with more sites than the cap is sampled by a fixed stride, so the sample is
stable across runs and arms but changes if you change the cap. Do not compare
numbers produced under different caps.

## Troubleshooting

**`No corpus manifest. Run make corpus first.`** - Step 2 has not been run, or it
failed partway. Re-run it; downloads are cached per module.

**A corpus module is rejected that the guide says should be admitted.** - The
upstream tag moved, or GitHub was unreachable. `corpus/modules/manifest.json`
records the reason for every rejection.

**`Client.__init__() got an unexpected keyword argument 'proxies'`** - `openai`
1.x against `httpx` 0.28+. `pip install -U openai`.

**A run reports `Modules with no usable suite`.** - Expected in small numbers, and
it is a result rather than an error. `runs/latest/crashes/` has the traceback if
an arm crashed rather than merely failing to produce a suite.

**The campaign hangs.** - It should not, each child arms its own watchdog and the
parent has a backstop. If it does, lower `PINDOWN_PYTEST_TIMEOUT_S` and open an
issue with the module id.

**`make free` takes far longer than five minutes.** - Fewer cores. Set
`PINDOWN_MUTATION_WORKERS` higher if the machine can take it, or lower
`PINDOWN_MAX_MUTANTS` to 150 for a faster, coarser run.
