# Results: `20260830-015454-free`

Model `gpt-4.1-2025-04-14` at temperature 0.0, Python 3.12.3, revision `5e9b23d-dirty`. 14 modules, 2 arms.

## Headline

| Metric | Human tests (ceiling) | Golden fuzz baseline |
| --- | --- | --- |
| Median mutation score | 43.9% | 5.0% |
| Mean mutation score | 41.1% | 8.4% |
| Range | 5.0% - 75.9% | 0.0% - 33.9% |
| Median tests per module | 5 | 26 |
| Median wall clock per module | 7s | 7s |
| Total model cost | $0.00 | $0.00 |
| Modules with no usable suite | 0 | 1 |
| Generated tests discarded by filters | 0 | 2 |

## Per module

| Module | Mutants | Human tests | Golden fuzz baseline |
| --- | ---: | ---: | ---: |
| `boltons.cacheutils` | 215 | 54.4% | 0.5% |
| `boltons.dictutils` | 231 | 58.4% | 2.6% |
| `boltons.formatutils` | 98 | 39.8% | 11.2% |
| `boltons.funcutils` | 360 | 5.0% | 13.9% |
| `boltons.listutils` | 136 | 45.6% | failed |
| `boltons.mathutils` | 116 | 75.9% | 6.0% |
| `boltons.namedutils` | 121 | 48.8% | 0.0% |
| `boltons.setutils` | 400 | 44.8% | 0.8% |
| `boltons.statsutils` | 327 | 15.0% | 33.9% |
| `boltons.strutils` | 400 | 14.0% | 20.5% |
| `boltons.tableutils` | 181 | 43.1% | 2.8% |
| `boltons.timeutils` | 201 | 18.9% | 4.0% |
| `semver` | 400 | 70.5% | 8.0% |
| `xmltodict` | 147 | 40.8% | 12.9% |

## What the quality filters rejected

| Reason a test was discarded | golden |
| --- | ---: |
| fails against current behavior | 2 |
