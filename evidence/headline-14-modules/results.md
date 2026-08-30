# Results: `20260830-055632-headline`

Model `gpt-4.1-2025-04-14` at temperature 0.0, Python 3.12.3, revision `b193251-dirty`. 14 modules, 4 arms.

## Headline

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

## Per module

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

## Where the agent's score came from

| Iteration | Modules still improving | Median score after |
| --- | ---: | ---: |
| 1 | 12 | 57.5% |
| 2 | 12 | 61.9% |
| 3 | 12 | 66.8% |
| 4 | 8 | 62.7% |
| 5 | 7 | 62.4% |
| 6 | 4 | 65.2% |

## What the quality filters rejected

| Reason a test was discarded | golden | baseline | agent |
| --- | ---: | ---: | ---: |
| fails against current behavior | 2 | 56 | 182 |
| asserts nothing | 0 | 1 | 6 |
