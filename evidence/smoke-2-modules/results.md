# Results: `20260830-022152-smoke`

Model `gpt-4.1-2025-04-14` at temperature 0.0, Python 3.12.3, revision `b193251-dirty`. 2 modules, 4 arms.

## Headline

| Metric | Human tests (ceiling) | Golden fuzz baseline | One-shot prompt baseline | pindown agent |
| --- | --- | --- | --- | --- |
| Median mutation score | 57.8% | 8.6% | 43.5% | 91.3% |
| Mean mutation score | 57.8% | 8.6% | 43.5% | 91.3% |
| Range | 39.8% - 75.9% | 6.0% - 11.2% | 0.0% - 87.1% | 82.7% - 100.0% |
| Median tests per module | 8 | 36 | 20 | 62 |
| Median wall clock per module | 2s | 6s | 14s | 68s |
| Total model cost | $0.00 | $0.00 | $0.05 | $0.19 |
| Modules with no usable suite | 0 | 0 | 1 | 0 |
| Generated tests discarded by filters | 0 | 0 | 5 | 8 |

## Per module

| Module | Mutants | Human tests | Golden fuzz baseline | One-shot prompt baseline | pindown agent |
| --- | ---: | ---: | ---: | ---: | ---: |
| `boltons.formatutils` | 98 | 39.8% | 11.2% | failed | 82.7% |
| `boltons.mathutils` | 116 | 75.9% | 6.0% | 87.1% | 100.0% |

## Where the agent's score came from

| Iteration | Modules still improving | Median score after |
| --- | ---: | ---: |
| 1 | 2 | 81.4% |
| 2 | 2 | 88.3% |
| 3 | 2 | 88.3% |
| 4 | 2 | 90.9% |
| 5 | 1 | 99.1% |
| 6 | 1 | 100.0% |

## What the quality filters rejected

| Reason a test was discarded | baseline | agent |
| --- | ---: | ---: |
| fails against current behavior | 5 | 8 |
