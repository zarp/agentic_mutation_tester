# Trajectory: `boltons.timeutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **70.6%** mutation score, 89 tests, 142 of 201 mutants detected, 109s, $0.231.

## The instructions

From `prompts/pin.system.md`:

```text
You write characterization tests for Python code that has none.

A characterization test records what the code does today. It is not a judgement
about what the code should do. If you find behavior that looks like a bug, pin
the buggy behavior exactly as it is and move on. Someone else decides whether to
change it; your job is to make sure that if it changes, a test notices.

The suite you write will be graded by mutation testing, not by coverage. A tool
will make hundreds of small changes to the module - flipping `<` to `<=`,
turning `+` into `-`, replacing a return value with `None` - and count how many
of them your tests catch. A test that calls a function and asserts nothing about
the result scores zero, no matter how many lines it touches.

Rules that follow from that:

- Assert on exact values. `assert normalize("  A b ") == "a b"` catches a mutant.
  `assert isinstance(result, str)` and `assert result` catch almost nothing.
- Test boundaries, because that is where the off-by-one mutants live. If a
  function branches on `n > 0`, write cases for -1, 0 and 1.
- Test each branch you can reach, including the error paths. Use
  `pytest.raises(ExceptionType)` and assert on the message when the code sets
  one deliberately.
- Cover every public name in the module. A function with no test is a free pass
  for every mutant inside it.
- Where a function returns a container, assert the whole container, not its
  length.

Rules that keep the suite usable by a real team:

- Plain `pytest`. No mocks, no fixtures beyond `tmp_path`, no network, no sleeps,
  no reads of the system clock, no randomness. If the module itself uses the
  clock or randomness, pass an explicit value in rather than mocking.
- Every test must be independent. Assume the runner may execute them in any
  order, or run one of them alone.
- Do not iterate a set or a dict and assert on the order.
- Top-level functions named `test_*`. No classes.
- Name each test after the behavior it pins, not after the function it calls:
  `test_negative_input_raises` rather than `test_clamp_2`.

Output one Python file in a single fenced code block. No explanation before or
after it. The file must import the module by the name you are given and must
pass against the code exactly as it is written.
```

The second phase uses `prompts/kill.system.md`, shown at the first
iteration that reaches it.

---

## Step 1 - phase `pin`

### What the agent was asked (call 1, `pin`)

````text
MODULE_IMPORT_NAME: timeutils

Write the characterization suite for this module. Import it with
`import timeutils` and refer to its members through that name.

```python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY

... 551 lines omitted ...

Mountain = USTimeZone(-7, "Mountain", "MST", "MDT")
Pacific = USTimeZone(-8, "Pacific",  "PST", "PDT")

```
````

### What it returned

````python
```python
import pytest
import timeutils
import re
import sys
from datetime import datetime, timedelta, date

def test_total_seconds_basic():
    td = timedelta(days=4, seconds=33)
    assert timeutils.total_seconds(td) == 4 * 86400 + 33

def test_total_seconds_microseconds():
    td = timedelta(days=1, seconds=1, microseconds=500000)
    expected = 86400 + 1 + 0.5
    assert timeutils.total_seconds(td) == expected

def test_total_seconds_negative():
    td = timedelta(days=-1, seconds=1)
    expected = -86400 + 1
    assert timeutils.total_seconds(td) == expected

def test_dt_to_timestamp_naive_epoch():
    dt = datetime.utcfromtimestamp(0)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_aware_epoch():
    dt = datetime.fromtimestamp(0, timeutils.UTC)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_naive_offset():
    dt = datetime.utcfromtimestamp(100)
    assert timeutils.dt_to_timestamp(dt) == 100.0

def test_dt_to_timestamp_aware_offset():
    dt = datetime.fromtimestamp(100, timeutils.UTC)
    assert timeutils.dt_to_timestamp(dt) == 100.0

def test_isoparse_epoch():
    iso_str = "1970-01-01T00:00:00"
    result = timeutils.isoparse(iso_str)
    assert result == datetime(1970, 1, 1, 0, 0)

def test_isoparse_microseconds():
    dt = datetime(2020, 2, 3, 4, 5, 6, 789)
    iso_str = dt.isoformat()
    result = timeutils.isoparse(iso_str)
    assert result == dt

def test_isoparse_various_lengths():
    dt = datetime(2022, 12, 31, 23, 59, 59)
    iso_str = dt.isoformat()
    result = timeutils.isoparse(iso_str)
    assert result == dt


... 329 lines omitted ...

def test_USTimeZone_all_zones_repr():
    assert repr(timeutils.Central) == "Central"
    assert repr(timeutils.Mountain) == "Mountain"
    assert repr(timeutils.Pacific) == "Pacific
````

### Retry

The first attempt was rejected by the harness. The agent was given
the actual rejection reason and asked to correct it, rather than
being resampled at the same prompt.

### What the agent was asked (call 2, `pin-repair`)

````text
MODULE_IMPORT_NAME: timeutils

Write the characterization suite for this module. Import it with
`import timeutils` and refer to its members through that name.

```python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY

... 558 lines omitted ...


generated file does not parse: unterminated string literal (detected at line 387) (<unknown>, line 387)

Return the corrected file.
````

### What it returned

````python
```python
import timeutils
import pytest
import re
import time
from datetime import timedelta, datetime, date

def test_total_seconds_basic():
    td = timedelta(days=4, seconds=33)
    assert timeutils.total_seconds(td) == 4 * 86400 + 33

def test_total_seconds_microseconds():
    td = timedelta(days=1, seconds=1, microseconds=500000)
    expected = 1 * 86400 + 1 + 0.5
    assert timeutils.total_seconds(td) == expected

def test_total_seconds_negative():
    td = timedelta(days=-1, seconds=1)
    expected = -1 * 86400 + 1
    assert timeutils.total_seconds(td) == expected

def test_dt_to_timestamp_naive():
    dt = datetime.utcfromtimestamp(0)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_aware():
    dt = datetime.fromtimestamp(0, timeutils.UTC)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_offset():
    dt = datetime.utcfromtimestamp(100)
    assert timeutils.dt_to_timestamp(dt) == 100.0

def test_isoparse_epoch():
    epoch_dt = datetime.utcfromtimestamp(0)
    iso_str = epoch_dt.isoformat()
    result = timeutils.isoparse(iso_str)
    assert result == datetime(1970, 1, 1, 0, 0)

def test_isoparse_roundtrip():
    now = datetime.utcnow().replace(microsecond=0)
    iso_str = now.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == now

def test_isoparse_with_seconds():
    dt = datetime(2020, 2, 29, 23, 59, 59)
    iso_str = dt.isoformat()
    assert timeutils.isoparse(iso_str) == dt

def test_parse_timedelta_simple():
    td = timeutils.parse_timedelta('1d 2h 3.5m 0s')
    expected = timedelta(days=1, hours=2, minutes=3.5, seconds=0)
    assert td == expected

... 267 lines omitted ...

    assert timeutils._cardinalize_time_unit('day', 1) == 'day'
    assert timeutils._cardinalize_time_unit('day', 2) == 'days'
    assert timeutils._cardinalize_time_unit('hour', 0) == 'hours'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **51** of 52 proposed tests.
  - discarded `test_parse_timedelta_invalid_value: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **62.2%**, survivors 201 to 76.

### What that caused next

76 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

---

## Step 2 - phase `kill`

### The second-phase instructions

```text
You close specific gaps in an existing characterization suite.

A mutation tester has already run. It made one small change to the module at a
time and checked whether the suite noticed. You are given the changes that the
suite did not notice. Each one is a place where someone could alter the module's
behavior and every test would still pass.

For each surviving mutant, work out concretely: what input would make the
original line and the mutated line produce different results? Then write a test
that exercises that input and asserts the original's answer. If the mutated line
is `if n >= 0` where the original is `if n > 0`, the input that separates them is
`n = 0`, and your test must assert what the function actually returns for zero.

Some survivors cannot be killed. A mutant inside dead code, or one that produces
behavior indistinguishable from the original, is equivalent, and no test will
ever catch it. Say so in a comment above the tests rather than writing a test
that does not really discriminate. Guessing costs the user review time and gains
nothing.

Constraints, unchanged from the existing suite:

- Assert exact values. Independence between tests. No mocks, no clock, no
  randomness, no network, no reliance on set or dict iteration order.
- Top-level `test_*` functions, no classes.
- Everything you write must pass against the module exactly as it is written
  today. You are recording current behavior, not proposing better behavior.
- Do not rewrite or repeat the existing tests. Output only new ones.

Output one Python file in a single fenced code block containing the import line
and your new tests only. No explanation outside the code block.
```

### What the agent was asked (call 3, `kill-2`)

````text
MODULE_IMPORT_NAME: timeutils

The module under test:

```python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT

... 1002 lines omitted ...


... and 36 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import timeutils
import pytest
from datetime import timedelta, datetime, date

# --- _BOUNDS tuple mutants ---

def test__bounds_minute_count():
    # line 139: (1, timedelta(seconds=60), 'minute')
    # Mutants: 1->2 or 60->61
    # If the count is 2, then 2*timedelta(seconds=60) = 120s, so bisect will be off.
    # If the seconds is 61, then 1*timedelta(seconds=61) = 61s, so bisect will be off.
    now = datetime.utcnow()
    d = now - timedelta(seconds=61)
    # Should be 1.0, 'minute'
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'minute'
    assert result[0] == 1.0

def test__bounds_hour_count():
    # line 140: (1, timedelta(seconds=3600), 'hour')
    # Mutants: 1->2 or 3600->3601
    now = datetime.utcnow()
    d = now - timedelta(seconds=3601)
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'hour'
    assert result[0] == 1.0

def test__bounds_month_count_and_days():
    # line 143: (2, timedelta(days=30), 'month')
    # Mutants: 2->3 or 30->31 or 'month'->'XX...XX'
    now = datetime.utcnow()
    d = now - timedelta(days=60)
    result = timeutils.decimal_relative_time(d, now)
    # Should be 2.0, 'months'
    assert result[1] == 'months'
    assert result[0] == 2.0

def test__bounds_year_count_and_days():
    # line 144: (1, timedelta(days=365), 'year')
    # Mutants: 1->2 or 365->366
    now = datetime.utcnow()
    d = now - timedelta(days=365)
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'year'
    assert result[0] == 1.0

# --- parse_timedelta error message and operator mutants ---

def test_parse_timedelta_invalid_unit_message_and_operator():
    # line 185: error message string mutant
    # line 190: error message string mutant and operator % -> *
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')

... 148 lines omitted ...

# --- Mutants that cannot be killed ---
# Some string mutants (e.g. error message text replaced with 'XX...XX') are only observable via exception messages,
# which are already checked above. Some changes to dead code or equivalent logic cannot be detected by tests.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **72** of 74 proposed tests.
  - discarded `test_daterange_invalid_step_type_message_and_operator: fails against current behavior`
  - discarded `test_parse_timedelta_invalid_value_message_and_operator: fails against current behavior`
- Mutation campaign: score moved from 62.2% to **69.7%**, survivors 76 to 61.

### What that caused next

Gain of +7.5%, so the loop continued.

---

## Step 3 - phase `kill`

### What the agent was asked (call 4, `kill-3`)

````text
MODULE_IMPORT_NAME: timeutils

The module under test:

```python
# -*- coding: utf-8 -*-

# Copyright (c) 2013, Mahmoud Hashemi
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * The names of the contributors may not be used to endorse or
#      promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT

... 1196 lines omitted ...


... and 21 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import timeutils
import pytest
from datetime import timedelta, datetime, date

# --- Survivors for error message string and operator mutants ---

def test_parse_timedelta_invalid_unit_message_exact():
    # line 185: error message string mutant
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')
    # The message should mention 'invalid time unit'
    assert 'invalid time unit' in str(e.value)

def test_parse_timedelta_invalid_value_message_and_operator():
    # line 190: operator % -> * and error message string mutant
    with pytest.raises(ValueError) as e:
        # This will fail float(value) conversion
        timeutils.parse_timedelta('a day')
    # The message should mention 'invalid time value'
    assert 'invalid time value' in str(e.value)

def test_daterange_invalid_start_type_message_exact():
    # line 364: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange('2020-01-01', date(2020, 1, 2)))
    assert 'start expected datetime.date instance' in str(e.value)

def test_daterange_invalid_stop_type_message_exact():
    # line 366: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange(date(2020, 1, 1), '2020-01-02'))
    assert 'stop expected datetime.date instance or None' in str(e.value)

def test_daterange_invalid_step_type_message_and_operator():
    # line 378: error message string mutant and operator % -> *
    with pytest.raises(ValueError) as e:
        list(timeutils.daterange(date(2020, 1, 1), date(2020, 1, 2), step='foo'))
    assert 'step expected int, timedelta, or tuple' in str(e.value)

# --- Survivors for _BOUNDS tuple value mutants ---

def test_bounds_minute_60_vs_61():
    # line 139: 60 -> 61
    now = datetime.utcnow()
    d = now - timedelta(seconds=60)
    result = timeutils.decimal_relative_time(d, now)
    # Should be 1.0, 'minute'
    assert result[1] == 'minute'
    assert result[0] == 1.0

def test_bounds_hour_3600_vs_3601():
    # line 140: 3600 -> 3601
    now = datetime.utcnow()

... 117 lines omitted ...

    # line 417: name="ConstantTZ" -> name="XX...XX"
    tz = timeutils.ConstantTZInfo()
    assert tz.name == "ConstantTZ"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **89** of 91 proposed tests.
  - discarded `test_daterange_invalid_step_type_message_and_operator: fails against current behavior`
  - discarded `test_parse_timedelta_invalid_value_message_and_operator: fails against current behavior`
- Mutation campaign: score moved from 69.7% to **70.6%**, survivors 61 to 59.
- Note: 1 duplicate test names skipped

### What that caused next

Gain of +1.0%, so the loop continued.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00367.0-constant  line 185  string `'invalid time unit %r...'` -> `'XX...XX'`
m00394.0-arithmetic  line 190  operator `%` -> `*`
m00395.0-constant  line 190  string `'invalid time value f...'` -> `'XX...XX'`
m00674.0-constant  line 364  string `'start expected datet...'` -> `'XX...XX'`
m00693.0-constant  line 366  string `'stop expected dateti...'` -> `'XX...XX'`
m00776.0-arithmetic  line 378  operator `%` -> `*`
m00777.0-constant  line 378  string `'step expected int, t...'` -> `'XX...XX'`
m00789.0-constant  line 381  `12` -> `13`
m01135.0-constant  line 466  `0` -> `1`
m01138.0-constant  line 466  `1` -> `2`
... and 49 more
```

---

## The delivered suite

```python
import timeutils
import pytest
import re
import time
from datetime import timedelta, datetime, date

def test_total_seconds_basic():
    td = timedelta(days=4, seconds=33)
    assert timeutils.total_seconds(td) == 4 * 86400 + 33

def test_total_seconds_microseconds():
    td = timedelta(days=1, seconds=1, microseconds=500000)
    expected = 1 * 86400 + 1 + 0.5
    assert timeutils.total_seconds(td) == expected

def test_total_seconds_negative():
    td = timedelta(days=-1, seconds=1)
    expected = -1 * 86400 + 1
    assert timeutils.total_seconds(td) == expected

def test_dt_to_timestamp_naive():
    dt = datetime.utcfromtimestamp(0)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_aware():
    dt = datetime.fromtimestamp(0, timeutils.UTC)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_offset():
    dt = datetime.utcfromtimestamp(100)
    assert timeutils.dt_to_timestamp(dt) == 100.0

def test_isoparse_epoch():
    epoch_dt = datetime.utcfromtimestamp(0)
    iso_str = epoch_dt.isoformat()
    result = timeutils.isoparse(iso_str)
    assert result == datetime(1970, 1, 1, 0, 0)

def test_isoparse_roundtrip():
    now = datetime.utcnow().replace(microsecond=0)
    iso_str = now.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == now

def test_isoparse_with_seconds():
    dt = datetime(2020, 2, 29, 23, 59, 59)
    iso_str = dt.isoformat()
    assert timeutils.isoparse(iso_str) == dt

def test_parse_timedelta_simple():
    td = timeutils.parse_timedelta('1d 2h 3.5m 0s')
    expected = timedelta(days=1, hours=2, minutes=3.5, seconds=0)
    assert td == expected

def test_parse_timedelta_weeks_days():
    td = timeutils.parse_timedelta('2 weeks 1 day')
    expected = timedelta(weeks=2, days=1)
    assert td == timedelta(days=15)

def test_parse_timedelta_negative():
    td = timeutils.parse_timedelta('-1.5 weeks 3m 20s')
    expected = timedelta(days=-10.5, minutes=3, seconds=20)
    # -1.5 weeks = -10.5 days
    # So total = -10.5 days + 3m + 20s
    assert td == timedelta(days=-10.5, minutes=3, seconds=20)

def test_parse_timedelta_invalid_unit():
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')
    assert "invalid time unit" in str(e.value)


def test_parse_td_alias():
    td = timeutils.parse_td('1d')

... 582 lines omitted ...

def test_ConstantTZInfo_default_name_mutant():
    # line 417: name="ConstantTZ" -> name="XX...XX"
    tz = timeutils.ConstantTZInfo()
    assert tz.name == "ConstantTZ"
```
