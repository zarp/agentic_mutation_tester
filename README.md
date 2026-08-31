# pindown

Agentic mutation tester - writes characterization tests for legacy Python code that has none, and grades
them by mutation score rather than test coverage.

Usage example:
```bash
pindown pin --file path/to/your_module.py
```

You get a `pytest` file that passes against the code as it is today, plus an
honest statement at the top of what the suite still cannot detect.

## Target audience

An engineer who has just inherited a module nobody has touched in three years,
and has been asked to change it. It is several hundred lines long, it has no tests, the person who wrote it has left, and it does something important. Their task is to change this code without breaking a behavior that somebody, somewhere, depends on, and which is documented nowhere except in the code itself.

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

The tool makes hundreds of small changes to the module, one at a time - flip a
comparison, swap an operator, replace a return value with `None` - and runs the
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

## The corpus

The intended targets (at least for the current implementation) are single-file, stdlib-only Python modules. It is what keeps a mutation campaign to a few hundred subprocess runs instead of a container per mutant.

We will be using fourteen single-file, standard-library-only modules from real open source
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
seventeen candidates are currently rejected - two for being over the line cap,
one for producing too few mutants.

## What is being compared for each module in the corpus

Four arms, the same mutants, the same filters, the same
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

**The agent.** The full loop: write characterization tests, run mutation testing, feed the surviving mutants back as the next prompt, repeat until the score plateaus.

The baseline suites go through the same quality filters as the agent's. Skipping
them would flatter the agent, because an unfiltered one-shot suite quite often
fails to import at all, and scoring that as zero would measure the harness rather
than the approach.

## Results

Generated by `make score` from `runs/latest/records.jsonl`. Numbers here are never
typed by hand.

<!-- RESULTS -->

From `runs/20260830-055632-headline/`: model `gpt-4.1-2025-04-14` at temperature 0.0, 14 modules, 4 arms, Python 3.12.3, revision (commit SHA) `b193251-dirty`.

| Metric | Human tests (ceiling) | Golden fuzz baseline | One-shot prompt baseline | pindown agent |
| --- | --- | --- | --- | --- |
| Median mutation score | 43.9% | 5.0% | 54.8% | 62.7% |
| Mean mutation score | 41.0% | 8.4% | 52.3% | 57.5% |
| Range | 5.0% - 75.9% | 0.0% - 33.9% | 0.0% - 88.8% | 0.0% - 100.0% |
| Median tests per module | 5 | 26 | 35 | 70 |
| Median wall clock per module | 7s | 7s | 25s | 97s |
| Total model cost | $0.00 | $0.00 | $0.52 | $2.60 |
| Modules with no usable suite | 0 | 1 | 1 | 2 |
| Generated tests discarded by filters | 0 | 2 | 57 | 188 |

| Module | Mutants | Human tests | Golden fuzz baseline | One-shot prompt baseline | pindown agent |
| --- | ---: | ---: | ---: | ---: | ---: |
| `boltons.cacheutils` | 215 | 54.4% | 0.5% | 55.8% | 52.6% |
| `boltons.dictutils` | 231 | 58.4% | 2.6% | 63.2% | failed |
| `boltons.formatutils` | 98 | 39.8% | 11.2% | failed | 86.7% |
| `boltons.funcutils` | 360 | 5.0% | 13.9% | 36.4% | 44.7% |
| `boltons.listutils` | 136 | 44.9% | failed | 52.9% | 76.5% |
| `boltons.mathutils` | 116 | 75.9% | 6.0% | 88.8% | 100.0% |
| `boltons.namedutils` | 121 | 48.8% | 0.0% | 76.0% | 72.7% |
| `boltons.setutils` | 400 | 44.8% | 0.8% | 36.8% | 44.2% |
| `boltons.statsutils` | 327 | 15.0% | 33.9% | 49.5% | 63.0% |
| `boltons.strutils` | 400 | 14.0% | 20.5% | 33.8% | 54.0% |
| `boltons.tableutils` | 181 | 43.1% | 2.8% | 56.9% | 62.4% |
| `boltons.timeutils` | 201 | 18.9% | 4.0% | 67.7% | 70.6% |
| `semver` | 400 | 70.5% | 8.0% | 60.2% | failed |
| `xmltodict` | 147 | 40.8% | 12.9% | 53.7% | 76.9% |

<!-- /RESULTS -->

Report, in this order: median mutation score per arm against the human ceiling,
the per-module table including the modules where every arm does badly, where the
agent's score came from iteration by iteration, and the full taxonomy of what the
quality filters rejected. The taxonomy is the part that transfers to other
projects, and a list of what does not work is more useful than a headline number.

## Reproducing this

Short version below. [REPRODUCE.md](REPRODUCE.md) is the full guide, written for
a clean machine: exact expected output at each step, pinned versions, runtime and
cost, what is deterministic and what is not, and the failures worth knowing about
in advance.

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
make eval                     # all four arms, 14 modules             ~33 min, ~$3
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

The module must be importable on its own and must not need third-party packages (removing this constraint could be a good TODO item).

### If you have no API key

`PINDOWN_STUB_LLM=1` runs the entire pipeline against a canned response. It
exercises the mutation engine, the quality filters, the merge logic, the loop and
the scoring for free, and it is what the tests and `make preflight` use. It is not
a baseline - the canned suite is deliberately weak. `make free` is the free arm
that means something.

## Improvement changelog

Each entry is one experiment, what it was for, what the evidence said, and what
happened to it. Entries marked *removed* were tried and taken out; those are the
ones with the most in them.

| Stage | What was tried and why | Evidence | Decision |
| --- | --- | --- | --- |
| Corpus | Admit candidates by automated check rather than by hand: single file, stdlib only, own suite passes standalone, enough mutants to be stable | 14 of 17 admitted; the 3 rejections and their reasons are in `corpus/modules/manifest.json` | Kept. Two of the original hand-picked candidates turned out to have test suites that do not pass standalone, which would have made the ceiling meaningless without anyone noticing |
| Corpus | First import check rejected any non-stdlib import anywhere in the file | 0 of 17 admitted | Revised. Imports inside `try`/`except ImportError` are Python 2 shims that never execute on 3.12; counting them threw away the entire corpus |
| Ceiling | Added the project's own tests as a fourth arm, rather than comparing agent against prompt alone | Human median 43.9%, range 5.0% to 75.9% across 14 modules | Kept, and it reframed the target. A human ceiling of 44% means "beat the humans" is the wrong goal; the interesting question is how close an agent gets for how much money |
| Baseline | Added a model-free fuzz-and-freeze baseline so the free path means something and the agent has a real bar to clear | Golden median 5.0%, mean 8.4%; but it beats the human suite on 3 of 14 modules | Kept. On `funcutils` it scores 13.9% against the humans' 5.0%, and on `statsutils` 33.9% against 15.0%. |
| Harness | First full corpus run lost two modules to `PermissionError` | `listutils` and `dictutils` recorded 0 mutants | Fixed. A mutant made the suite hang; the parent's attempt to kill it was denied by the sandbox, and the timeout handler took the campaign down with it. The child now arms its own `SIGALRM` watchdog, which needs no privileges |
| Harness | Fuzz baseline produced an unparseable file on `namedutils` and nothing at all on `semver` | 3 of 14 modules scored 0.0% for harness reasons rather than real ones | Fixed. Argument reprs were captured after the call, so a function that mutates its arguments recorded the mutated value; and `semver`'s CLI helpers print an argparse usage message that corrupted the JSON payload. Results now go to a file and each generated test is validated on its own |
| Iteration 1 | Feed the surviving-mutant list back as the next objective, instead of asking for more tests | Median agent score rose from 57.5% after phase 1 to 66.8% after iteration 3 across 12 successful modules; `mathutils` reached 100%, `listutils` 76.5% where the fuzz baseline failed entirely | Kept. This is the main contribution: the survivor list is a better instruction than "write more tests" |
| Iteration 2 | Quality filters: drop tests that assert nothing, contradict current behavior, flake across hash seeds, or need a sibling test | 188 agent tests discarded, 182 for contradicting current behavior; without filters the one-shot baseline would look worse than it is and the agent would ship suites that fail on the code they claim to describe | Kept. The discard taxonomy is as informative as the headline score |
| Iteration 3 | Plateau termination instead of a fixed iteration count | Several modules stopped improving after 2 flat iterations (`namedutils`, `funcutils`); others used all 6 (`mathutils`, `xmltodict`) | Kept |
| Final | Combined the changes that worked | Agent median 62.7% vs human ceiling 43.9%, one-shot 54.8%, golden 5.0%; $2.60 for 14 modules; 12 of 14 produced usable agent suites | The measured improvement is real but not universal: agent failed on `semver` (1259-line module, parse error after repair) and `dictutils` (1138 lines), and lost to the one-shot prompt on `mathutils` before iteration closed the gap |

### What the free arms already show

Two results are in and neither needed a model.

The human ceiling is much lower than the framing usually assumes. Across fourteen
modules the projects' own test suites detect a median of 43.9% of single-point
behavior changes, and on `funcutils` the figure is 5.0%. These are maintained
libraries with real users. Whatever an agent scores has to be read against that,
not against 100%.

Fuzzing every public function with a
fixed pool of arguments and freezing the results beats the human suite outright on
three of fourteen modules. It fails badly wherever behavior lives behind a class
constructor, which is most real code - `listutils` produces no usable suite at all
because everything in it hangs off `BarrelList`. That is the specific gap an agent
has to fill, and it is a more precise statement of the task than "write tests".

## The main failure mode

The agent's most expensive mistake is not a bad test idea but a test that
contradicts current behavior. Across the headline run, **182 of 188** discarded
agent tests failed because they asserted the wrong value, not because they
asserted nothing. The model often writes what the code *should* do rather than
what it *does*, and the quality filter catches that - but only after a full
pytest run per candidate. On large modules (`semver`, 1259 lines) even the repair
turn could not produce a parseable file, and the whole arm failed.

The second failure mode is plateauing on introspection-heavy code. `funcutils`
(1133 lines, heavy use of `inspect` and `exec`) topped out at 44.7% despite six
iterations, barely above the human suite's 5.0% but far below what simpler modules
reached. The survivor list helps most where behavior is reachable through plain
function calls with concrete inputs.

## Hot take

Coverage is the wrong gate and this run proves it with numbers. The one-shot
prompt baseline produced **35 median tests** and scored **54.8%** on mutation
testing - already above the human ceiling of **43.9%** - while discarding only
57 bad tests. Line coverage would have called that success. Mutation testing
called 56 of its tests wrong about the behavior they claimed to pin.

The agent's value is not "write more tests" but "write tests aimed at specific
undetected behavior changes, then stop when the score stops moving." That loop
cost five times more ($2.60 vs $0.52) and bought **8 percentage points** on the
median (62.7% vs 54.8%), with wins on hard cases the prompt could not handle at
all (`formatutils`, `listutils`). Whether that trade is worth it depends on the
module - and that is exactly the kind of question mutation score lets you ask
without guessing.

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
for determinism - stable mutant ids across runs, so survivor sets from two arms
are directly comparable - and because driving those tools programmatically at this
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
