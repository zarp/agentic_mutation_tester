# pindown

Writes characterization tests for legacy Python code that has none, and grades
them by mutation score rather than coverage.

```bash
pindown pin --file src/billing/pricing.py
```

You get a `pytest` file that passes against the code as it is today, plus an
honest statement at the top of what the suite still cannot detect.

## Who has this problem

The engineer who has just inherited a module nobody has touched in three years,
and has been asked to change it.

Every team has this module and everyone knows which one it is. It is four hundred
to a thousand lines, it has no tests, the person who wrote it has left, and it is
load-bearing. The task is not "understand this code" in the abstract; it is
"change this code without breaking a behavior that somebody, somewhere, depends
on, and which is documented nowhere except in the code itself."

## The bottleneck

You cannot safely change code whose behavior nothing records, so the refactor is
blocked on writing tests first. That is slow work, and it is slow in a
particularly demoralizing way: you are writing tests for logic you do not yet
understand, so every test is a small research project.

The worse problem is that you have no signal for when you are done. Line coverage
is the number everyone reaches for, and it is close to useless here. A test that
calls a function and asserts nothing about the result covers every line it
touches. You can reach ninety percent coverage on a module and still have a suite
that would not notice if `<` became `<=` throughout. Teams either over-invest,
writing tests long past the point of diminishing returns, or they hit the coverage
target and ship on hope. Both are expensive and neither is a decision anyone made
deliberately.

## Why an agent, and why this measurement

Mutation testing gives this problem something rare: a scoring function that is
objective, mechanical, and hard to fool.

The tool makes hundreds of small changes to the module, one at a time — flip a
comparison, swap an operator, replace a return value with `None` — and runs the
suite against each. If the suite still passes, that change went undetected, and
the mutant survives. The score is the fraction detected. A test that asserts
nothing scores zero no matter how many lines it covers, which is exactly the
property coverage lacks.

That makes two things possible. The agent can be graded by something other than
its own opinion of its work. And the surviving-mutant list becomes the agent's
next instruction: not "write more tests", but "here are eleven specific behavior
changes your suite would not catch, and here is the line each one is on."

## What it does

```
module.py
  -> phase 1     write a suite that pins current behavior
  -> filters     drop tests that assert nothing, fail, flake, or need a sibling
  -> campaign    run every mutant; count what the suite catches
  -> phase 2     feed the survivors back; write tests aimed at exactly those
  -> repeat      until the score stops moving
  -> artifact    a pytest file, plus what it still cannot detect
```

The model never judges its own output. Three independent things do: the test
runner decides whether a test passes, the quality filters decide whether it is
allowed to count, and the mutation engine decides whether the suite is any good.

### The quality filters, and why they exist

A generated test can be technically passing and still worthless or actively
harmful. Four kinds get dropped before anything is scored:

| Filter | What it catches | How |
| --- | --- | --- |
| Vacuous | Calls the code, asserts nothing | AST scan for `assert`, `pytest.raises`, `assertX` |
| Contradicting | Asserts behavior the code does not have | Run it; a characterization test that fails is not one |
| Non-deterministic | Depends on set or dict iteration order | Re-run under several `PYTHONHASHSEED` values |
| Order dependent | Only passes after a sibling test ran | Run each test alone in a fresh process |

The last two are the expensive ones in practice. They pass on the machine that
generated them and fail in CI three weeks later, which is how a team learns to
distrust a test suite.

## Evidence

Four arms, the same modules, the same mutants, the same filters, the same
timeouts.

**Human tests (the ceiling).** Each corpus module ships with the tests its own
maintainers wrote. This is the number that makes the result mean something:
"better than a prompt" is a weak claim, "within reach of the project's own test
suite" is not.

**Golden fuzz baseline (free, no model).** Probe every public function with a
fixed pool of arguments, record what comes back, emit those observations as exact
assertions. This is the strongest thing you can build without an LLM, it is fully
deterministic, and anyone can run it without an API key. It is the bar the agent
actually has to clear.

**One-shot prompt baseline.** "Write pytest tests for this module." One call, no
execution, no verification. This is what a competent engineer does today.

**The agent.** Everything above.

The baseline suites go through the same quality filters as the agent's. Skipping
them would flatter the agent, because an unfiltered one-shot suite quite often
fails to import at all, and scoring that as zero would measure the harness rather
than the approach.

## The corpus

Fourteen single-file, standard-library-only modules from real open source
projects, each with the test suite its maintainers wrote.

Most come from [boltons](https://github.com/mahmoud/boltons) (BSD-3-Clause),
which is unusually well suited: a large collection of genuinely independent
single-file utility modules under one license, each with a maintained `pytest`
suite. `semver` (BSD-3-Clause) and `xmltodict` (MIT) are included so the result
does not describe one project's house style.

Nothing is committed. `make corpus` fetches each module from a pinned tag and
then validates it: single file, no third-party imports, its own test suite passes
standalone, and it generates enough mutants for a score to be stable. Candidates
that fail are reported with the reason rather than dropped quietly, because the
exclusions are part of what a reader needs in order to judge the corpus. Three of
seventeen candidates are currently rejected — two for being over the line cap,
one for producing too few mutants.

The single-file, stdlib-only constraint is load-bearing and it is a real
limitation. It is what keeps a mutation campaign to a few hundred subprocess runs
instead of a container per mutant, which is the difference between an evaluation
that finishes during a hackathon and one that does not. It also means nothing here
tells you how the approach behaves on a module with a database behind it.

## Results

Generated by `make score` from `runs/latest/records.jsonl`. Numbers here are never
typed by hand.

<!-- RESULTS -->
*Not yet run. This section stays empty rather than aspirational until a real
evaluation exists; `make score` writes it from the run log.*
<!-- /RESULTS -->

Report, in this order: median mutation score per arm against the human ceiling,
the per-module table including the modules where every arm does badly, where the
agent's score came from iteration by iteration, and the full taxonomy of what the
quality filters rejected. The taxonomy is the part that transfers to other
projects, and a list of what does not work is more useful than a headline number.

## Reproducing this

Tested on Ubuntu 24.04 with Python 3.12.3. No Docker, no GPU, no external
services beyond one model endpoint.

```bash
make setup                    # venv + install                        ~1 min
make corpus                   # fetch and validate 14 modules         ~1 min, needs network
make test                     # pindown's own test suite              ~10 s
make preflight                # go / no-go before spending anything   ~30 s
```

Then either arm. The free path needs no API key at all:

```bash
make free                     # human ceiling + fuzz baseline         ~20 min, $0
```

The full comparison needs a model:

```bash
cp .env.example .env          # add PINDOWN_API_KEY, pin an exact model version
make smoke                    # all four arms, 2 modules              ~6 min,  ~$0.20
make eval                     # all four arms, 14 modules             ~90 min, ~$4
make score                    # regenerate the tables from the log
```

Costs are for `gpt-4.1-2025-04-14` at published prices and are computed from
logged token counts, not estimated. Temperature is 0 and the model version is
pinned; set `PINDOWN_MODEL` to compare others.

Every run writes to `runs/<timestamp>-<tag>/`:

```
config.json      git revision, python version, model, every budget value
records.jsonl    one row per module per arm
traces/          every prompt and every response, per module per arm
suites/          every generated suite, and its surviving-mutant list
results.md       the tables above
metrics.json     the aggregates
```

To use it on your own code:

```bash
pindown pin --file path/to/your_module.py --out ./out
```

The module must be importable on its own and must not need third-party packages.
That is a real constraint and it is the first thing to fix if this were to go
further.

### If you have no API key

`PINDOWN_STUB_LLM=1` runs the entire pipeline against a canned response. It
exercises the mutation engine, the quality filters, the merge logic, the loop and
the scoring for free, and it is what the tests and `make preflight` use. It is not
a baseline — the canned suite is deliberately weak. `make free` is the free arm
that means something.

## Improvement changelog

Each entry is one experiment, what it was for, what the evidence said, and what
happened to it. Entries marked *removed* were tried and taken out; those are the
ones with the most in them.

| Stage | What was tried and why | Evidence | Decision |
| --- | --- | --- | --- |
| Baseline | One prompt, "write pytest tests for this module", scored by mutation testing | *pending headline run* | Established the starting point |
| Corpus | Rejected candidates automatically rather than curating by hand: single file, stdlib only, own suite passes standalone, enough mutants | 14 of 17 candidates admitted; the 3 rejections are recorded in `corpus/modules/manifest.json` | Kept. The first hand-picked list had two modules whose own tests did not pass standalone, which would have made the ceiling meaningless |
| Corpus | First import check rejected any non-stdlib import anywhere in the file | 0 of 17 candidates admitted | Revised. Imports inside `try`/`except ImportError` are Python 2 compatibility shims that never execute; counting them threw away the entire corpus |
| Iteration 1 | Feed the surviving-mutant list back to the model as the next objective, instead of asking for more tests | *pending headline run* | |
| Iteration 2 | Quality filters: drop tests that assert nothing, contradict current behavior, flake across hash seeds, or need a sibling test | *pending headline run* | |
| Iteration 3 | Plateau termination instead of a fixed iteration count | *pending headline run* | |
| Final | | *pending headline run* | |

## The main failure mode

*To be written from the headline run rather than guessed at. The candidate, based
on the stub and free runs so far, is that the survivor list contains equivalent
mutants — changes that genuinely cannot be detected because they do not alter
behavior — and the agent cannot always tell those apart from real gaps, so it
spends its last iterations writing tests that discriminate nothing. The prompt
tells it to say so instead of guessing; whether it does is measurable, and the
discard taxonomy will show it.*

## Hot take

*To be written from the headline run.* The claim under test: LLM-written tests
reliably reach high line coverage and low mutation score, because a model
optimizes for the appearance of thoroughness — one test per function, every
branch touched — while the thing that catches regressions is asserting exact
values at boundaries. If that holds, every coverage-gated CI pipeline is
measuring the wrong thing, and the fix is not a better prompt but a scoring
function the model cannot satisfy by writing more.

## Layout

```
src/pindown/
  models.py              shared vocabulary; every stage speaks in these
  config.py              budgets, provenance, and every non-termination risk
  cli.py                 pin / run / score / corpus
  mutation/
    operators.py         AST mutation operators; deterministic ids
    engine.py            the grader: run every mutant, count detections
  runtime/
    pytest_runner.py     subprocess execution with hard timeouts
    quality.py           the four filters
  agent/
    llm.py               model access with mandatory tracing and a stub mode
    loop.py              phase 1, phase 2, plateau termination
    merge.py             folding new tests in without silently shadowing old ones
  baseline/
    golden.py            the model-free fuzz-and-freeze baseline
  corpus/
    registry.py          candidates, pinned by tag, with licenses
    fetch.py             download and admit; rejections are reported
  eval/
    harness.py           the referee
    score.py             tables, generated from the log
prompts/                 the instructions that shape each agent, as files
tests/                   pindown's own tests; the mutation engine matters most
scripts/preflight.sh     go / no-go
```

## Scope

Characterization only. This deliberately does not fix bugs, improve the code, or
judge whether current behavior is correct. Pinning behavior and changing behavior
are different jobs and conflating them would make the artifact impossible to
trust: the whole value of a characterization suite is that it describes what is
there now.

## Prior work and licenses

Mutation testing is decades old; `mutmut` and `cosmic-ray` are the established
Python tools. The engine here is purpose-built rather than wrapping one of them,
for determinism — stable mutant ids across runs, so survivor sets from two arms
are directly comparable — and because driving those tools programmatically at this
granularity fights their design. `tests/test_operators.py` is what makes that
choice defensible, and swapping in an external engine behind the same interface
would be a reasonable cross-check.

The contribution is the loop: survivor-driven iteration, the four quality filters,
a model-free baseline strong enough to be worth beating, and a human ceiling in
every comparison.

Corpus modules are fetched at setup time and are not redistributed here. Each
carries its origin, tag and license in `corpus/modules/<id>/PROVENANCE.txt`:
boltons BSD-3-Clause, semver BSD-3-Clause, xmltodict MIT. `pindown` itself is
MIT.
