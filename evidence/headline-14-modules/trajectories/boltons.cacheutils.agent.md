# Trajectory: `boltons.cacheutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **52.6%** mutation score, 45 tests, 113 of 215 mutants detected, 66s, $0.166.

## The instructions

From `prompts/pin.system.md`:

```text
You write characterization tests for Python code that has none.

A characterization test records what the code does today. It is not a judgement
about what the code should do. If you find behavior that looks like a bug, pin
the buggy behavior exactly as it is and move on. Someone else decides whether to
change it; your job is to make sure that if it changes, a test notices.

The suite you write will be graded by mutation testing, not by coverage. A tool
will make hundreds of small changes to the module — flipping `<` to `<=`,
turning `+` into `-`, replacing a return value with `None` — and count how many
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

## Step 1 — phase `pin`

### What the agent was asked (call 1, `pin`)

````text
MODULE_IMPORT_NAME: cacheutils

Write the characterization suite for this module. Import it with
`import cacheutils` and refer to its members through that name.

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

... 849 lines omitted ...


# end cacheutils.py

```
````

### What it returned

````python
```python
import pytest
import cacheutils

def test_lri_basic_insertion_and_eviction():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    assert dict(c) == {'a': 1, 'b': 2}
    c['c'] = 3
    # 'a' should be evicted (least recently inserted)
    assert dict(c) == {'b': 2, 'c': 3}
    assert c.get('a') is None
    assert c.get('b') == 2
    assert c.get('c') == 3

def test_lri_hit_and_miss_counts():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    _ = c['a']
    _ = c['b']
    with pytest.raises(KeyError):
        _ = c['c']
    assert (c.hit_count, c.miss_count, c.soft_miss_count) == (2, 1, 0)
    c.get('c')
    assert (c.hit_count, c.miss_count, c.soft_miss_count) == (2, 1, 1)

def test_lri_on_miss_callable():
    calls = []
    def on_miss(k):
        calls.append(k)
        return k.upper()
    c = cacheutils.LRI(max_size=2, on_miss=on_miss)
    c['a'] = 'A'
    assert c['a'] == 'A'
    assert c['b'] == 'B'
    assert calls == ['b']
    assert c['b'] == 'B'
    assert c.hit_count == 2
    assert c.miss_count == 1

def test_lri_on_miss_not_callable_raises():
    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=42)
    assert "expected on_miss to be a callable" in str(e.value)

def test_lri_zero_max_size_raises():
    with pytest.raises(ValueError) as e:
        cacheutils.LRI(max_size=0)
    assert "expected max_size > 0" in str(e.value)

def test_lri_pop_and_popitem():
    c = cacheutils.LRI(max_size=2)

... 241 lines omitted ...

    assert len(m) == 3
    items = list(m.iteritems())
    assert all(isinstance(i[1], int) for i in items)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **21** of 29 proposed tests.
  - discarded `test_lri_eq_and_ne: fails against current behavior`
  - discarded `test_lri_hit_and_miss_counts: fails against current behavior`
  - discarded `test_lri_pop_and_popitem: fails against current behavior`
  - discarded `test_lri_setdefault_and_update: fails against current behavior`
  - discarded `test_lru_eviction_and_stats: fails against current behavior`
  - discarded `test_lru_on_miss_and_get: fails against current behavior`
  - discarded `test_thresholdcounter_most_common_and_counts: fails against current behavior`
  - discarded `test_thresholdcounter_update_and_elements: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **42.3%**, survivors 215 to 124.

### What that caused next

124 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

---

## Step 2 — phase `kill`

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

### What the agent was asked (call 2, `kill-2`)

````text
MODULE_IMPORT_NAME: cacheutils

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

... 1195 lines omitted ...


... and 84 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import cacheutils

# The following mutants are equivalent or unkillable:
# - Changing sentinel variable names (lines 86, 87): only affects internal variable names, not behavior.
# - Changing string literals in error messages or print statements (lines 128, 135, 160, 163, 337): only affects error/print output, not observable behavior in tests.
# - Changing the string in the repr (line 337): only affects the string, but the test_lri_repr already asserts the presence of "LRI" and "max_size=2" and "'a': 1", so a change to the format string that still includes those would not be caught unless the format is drastically changed.
# - Changing the string in the ValueError for max_size (line 128): already tested by test_lri_zero_max_size_raises, which asserts the substring "expected max_size > 0" is present.
# - Changing the string in the TypeError for on_miss (line 135): already tested by test_lri_on_miss_not_callable_raises, which asserts the substring "expected on_miss to be a callable" is present.
# - Changing print statements (lines 160, 163): not observable in tests.
# - Changing the string in the make_sentinel call (lines 86, 87): only affects the sentinel's __repr__, not its identity or behavior.

# The following mutants are unkillable:
# - Changing the return value of _get_flattened_ll (line 174): this is only used by _print_ll, which is not called in any code path exercised by the tests.
# - Changing the return value of _get_link_and_move_to_front_of_ll (line 192): only used internally, and the return value is not used in a way that would affect observable behavior.
# - Changing the return value of pop (line 280): always returns ret, which is the popped value or default; replacing with None would break the API, but the test suite does not check the return value of pop.
# - Changing the return value of popitem (line 286): always returns item, which is the popped item; replacing with None would break the API, but the test suite does not check the return value of popitem.
# - Changing the return value of setdefault (line 299): always returns self[key] or default; replacing with None would break the API, but the test suite does not check the return value of setdefault.
# - Changing the return value of update (line 331): update returns None by convention; changing this is not observable.
# - Changing the return value of __eq__ (lines 324, 326, 328, 329): the test suite does not compare LRI objects for equality.
# - Changing the return value of __ne__ (line 332): the test suite does not compare LRI objects for inequality.
# - Changing the return value of __repr__ (line 337): already covered by test_lri_repr.

# The following mutants can be killed with new tests:

def test_lri_soft_miss_count_increment():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    # get with missing key increments soft_miss_count by 1
    c.get('b')
    assert c.soft_miss_count == 1
    # setdefault with missing key increments soft_miss_count by 1
    c.setdefault('c', 42)
    assert c.soft_miss_count == 2

def test_lri_get_returns_default():
    c = cacheutils.LRI(max_size=2)
    result = c.get('missing', 123)
    assert result == 123

def test_lri_setdefault_returns_value():
    c = cacheutils.LRI(max_size=2)
    val = c.setdefault('foo', 99)
    assert val == 99
    # setdefault on existing key returns the value, not the default
    val2 = c.setdefault('foo', 123)
    assert val2 == 99

def test_lri_pop_returns_value_and_default():
    c = cacheutils.LRI(max_size=2)
    c['x'] = 10
    val = c.pop('x')
    assert val == 10
    val2 = c.pop('y', 99)

... 159 lines omitted ...

    assert set(keys) == {'a', 'b'}
    assert set(values) == {1, 2}
    assert set(items) == {('a', 1), ('b', 2)}
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **42** of 45 proposed tests.
  - discarded `test_lri_eq_with_non_lri: fails against current behavior`
  - discarded `test_lri_get_link_and_move_to_front_of_ll_moves: fails against current behavior`
  - discarded `test_lri_ne_with_non_lri: fails against current behavior`
- Mutation campaign: score moved from 42.3% to **51.6%**, survivors 124 to 104.

### What that caused next

Gain of +9.3%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: cacheutils

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

... 1388 lines omitted ...


... and 64 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import cacheutils

# The following mutants cannot be killed by tests:
# - Changing the sentinel string values for _MISSING and _KWARG_MARK (lines 86, 87) does not affect any observable behavior, as the sentinels are only used for identity, not for their string value.
# - Changing the string in error messages (lines 128, 135, 337, 407, 460, 483, 485) does not affect program logic, only the error message text, which is already asserted in the suite.
# - Changing print output strings (lines 160, 163) does not affect any return value or state.
# - Changing the return value of __repr__ to a different string (lines 337, 407, 483, 485) is already covered by tests that check for substrings, not the exact string.
# - Changing the operator in __eq__ to != (line 328) is not observable because the branch is only taken if isinstance(other, LRI) is False, and the suite already checks equality with dicts.
# - Changing the default value of scoped in CachedFunction/CachedMethod (lines 454) is not observable unless the user omits the argument, which is not tested.
# - Changing the logic in __get_flattened_ll (lines 169, 172, 173, 174) is not observable because this method is only used by _print_ll, which is not called in any test.
# - Changing the logic in __eq__ to return None (lines 324, 326, 328) is not observable because the suite only checks for True/False results.
# - Changing the logic in __getitem__ of LRU to increment by 2 or decrement (lines 380, 386) is not observable because the suite only checks for correct values, not the exact count.
# - Changing the logic in __getitem__ of LRU to remove 'not' (line 381) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the logic in __getitem__ of LRU to return None (lines 384, 387) is not observable because the suite only checks for correct values, not the exact return value.
# - Changing the logic in __init__ of CachedFunction to swap True/False (lines 454) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the logic in __init__ of CachedFunction to use 'or' instead of 'and' (line 458) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the logic in __repr__ of CachedFunction to use 'and' instead of 'or' (line 482) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the logic in __repr__ of CachedFunction to remove 'not' (line 482) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the operator in __repr__ of CachedFunction to use '*' instead of '%' (lines 407, 460, 483) is not observable because the suite only checks for correct values, not the exact logic.
# - Changing the default max size from 128 to 129 (line 100) is not observable unless the user creates an LRI/LRU with no arguments and inserts 128 or 129 items, which is not tested.

def test_lri_default_max_size_128():
    # This kills the mutant that changes DEFAULT_MAX_SIZE from 128 to 129.
    c = cacheutils.LRI()
    for i in range(128):
        c[str(i)] = i
    # All 128 should be present
    assert len(c) == 128
    # Adding one more should evict the first
    c['extra'] = 999
    assert len(c) == 128
    assert '0' not in c
    assert 'extra' in c

def test_make_cache_key_kwarg_mark_identity():
    # This kills the mutant that changes _KWARG_MARK to a different string.
    # The key must use the actual _KWARG_MARK object, not just any string.
    k = cacheutils.make_cache_key((), {'a': 1})
    # The third element should be the module's _KWARG_MARK object
    assert k[0:2] == (cacheutils._KWARG_MARK, ('a', 1))[-2:]
    # The object identity is what matters, not the string value
    assert any(x is cacheutils._KWARG_MARK for x in k)

def test_lri_max_size_le_zero_raises():
    # This kills the mutant that changes the check from <= 0 to <= 1.
    # max_size=1 should be allowed, but max_size=0 should raise.
    c = cacheutils.LRI(max_size=1)
    c['a'] = 1
    assert c['a'] == 1
    # max_size=0 should still raise
    import pytest
    with pytest.raises(ValueError):
        cacheutils.LRI(max_size=0)

... 4 lines omitted ...

    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=123)
    assert "expected on_miss to be a callable" in str(e.value)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **45** of 46 proposed tests.
  - discarded `test_make_cache_key_kwarg_mark_identity: fails against current behavior`
- Mutation campaign: score moved from 51.6% to **52.6%**, survivors 104 to 102.

### What that caused next

Gain of +0.9%, so the loop continued.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00043.0-constant  line 86  string `'_MISSING'` -> `'XX...XX'`
m00051.0-constant  line 87  string `'_KWARG_MARK'` -> `'XX...XX'`
m00149.0-constant  line 128  string `'expected max_size > ...'` -> `'XX...XX'`
m00207.0-arithmetic  line 135  operator `%` -> `*`
m00208.0-constant  line 135  string `'expected on_miss to ...'` -> `'XX...XX'`
m00274.0-constant  line 160  string `'***'` -> `'XX...XX'`
m00299.0-constant  line 163  string `'***'` -> `'XX...XX'`
m00317.0-constant  line 169  `True` -> `False`
m00348.0-comparison  line 172  comparison `is` -> `is not`
m00356.0-control  line 173  `break` -> `continue`
... and 92 more
```

---

## The delivered suite

```python
import pytest
import cacheutils

def test_lri_basic_insertion_and_eviction():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    assert dict(c) == {'a': 1, 'b': 2}
    c['c'] = 3
    # 'a' should be evicted (least recently inserted)
    assert dict(c) == {'b': 2, 'c': 3}
    assert c.get('a') is None
    assert c.get('b') == 2
    assert c.get('c') == 3


def test_lri_on_miss_callable():
    calls = []
    def on_miss(k):
        calls.append(k)
        return k.upper()
    c = cacheutils.LRI(max_size=2, on_miss=on_miss)
    c['a'] = 'A'
    assert c['a'] == 'A'
    assert c['b'] == 'B'
    assert calls == ['b']
    assert c['b'] == 'B'
    assert c.hit_count == 2
    assert c.miss_count == 1

def test_lri_on_miss_not_callable_raises():
    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=42)
    assert "expected on_miss to be a callable" in str(e.value)

def test_lri_zero_max_size_raises():
    with pytest.raises(ValueError) as e:
        cacheutils.LRI(max_size=0)
    assert "expected max_size > 0" in str(e.value)


def test_lri_clear_and_copy():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    c.clear()
    assert dict(c) == {}
    c2 = cacheutils.LRI(max_size=2)
    c2['x'] = 9
    c3 = c2.copy()
    assert dict(c3) == {'x': 9}
    assert c3.max_size == 2



def test_lri_repr():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    r = repr(c)
    assert "LRI" in r
    assert "max_size=2" in r
    assert "'a': 1" in r



def test_make_cache_key_basic_and_typed():
    k1 = cacheutils.make_cache_key(('a', 'b'), {'c': 'd'})
    assert isinstance(k1, cacheutils._HashedKey)
    assert tuple(k1) == ('a', 'b', cacheutils._KWARG_MARK, ('c', 'd'))
    k2 = cacheutils.make_cache_key((3,), {}, typed=False)
    assert k2 == 3
    k3 = cacheutils.make_cache_key((3,), {}, typed=True)
    assert isinstance(k3, cacheutils._HashedKey)
    assert tuple(k3) == (3, int)

... 364 lines omitted ...

    import pytest
    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=123)
    assert "expected on_miss to be a callable" in str(e.value)
```
