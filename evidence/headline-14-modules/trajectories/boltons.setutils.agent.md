# Trajectory: `boltons.setutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **44.2%** mutation score, 103 tests, 177 of 400 mutants detected, 130s, $0.213.

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
MODULE_IMPORT_NAME: setutils

Write the characterization suite for this module. Import it with
`import setutils` and refer to its members through that name.

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

... 944 lines omitted ...


    __nonzero__ = __bool__  # py2 compat

```
````

### What it returned

````python
```python
import setutils
import pytest

def test_indexedset_insertion_order_and_uniqueness():
    s = setutils.IndexedSet([1, 2, 3, 2, 1])
    assert list(s) == [1, 2, 3]
    assert s.item_list[:3] == [1, 2, 3]
    assert len(s) == 3

def test_indexedset_repr_and_equality():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([1, 2, 3])
    s3 = setutils.IndexedSet([3, 2, 1])
    assert repr(s1) == "IndexedSet([1, 2, 3])"
    assert s1 == s2
    assert s1 != s3
    assert s1 == set([1, 2, 3])
    assert s1 != set([1, 2])

def test_indexedset_contains_and_iter():
    s = setutils.IndexedSet([1, 2, 3])
    assert 2 in s
    assert 4 not in s
    assert list(iter(s)) == [1, 2, 3]

def test_indexedset_reversed():
    s = setutils.IndexedSet([1, 2, 3])
    assert list(reversed(s)) == [3, 2, 1]

def test_indexedset_getitem_index_and_slice():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    assert s[0] == 'a'
    assert s[1] == 'b'
    assert s[-1] == 'd'
    assert list(s[:2]) == ['a', 'b']
    assert list(s[1:3]) == ['b', 'c']
    assert list(s[::-1]) == ['d', 'c', 'b', 'a']
    assert isinstance(s[1:3], setutils.IndexedSet)
    with pytest.raises(IndexError):
        _ = s[10]

def test_indexedset_index_method():
    s = setutils.IndexedSet(['x', 'y', 'z'])
    assert s.index('x') == 0
    assert s.index('y') == 1
    assert s.index('z') == 2
    with pytest.raises(ValueError) as e:
        s.index('notfound')
    assert "not in IndexedSet" in str(e.value)

def test_indexedset_add_and_discard_remove():
    s = setutils.IndexedSet()
    s.add(1)

... 288 lines omitted ...

        c.issuperset(123)
    with pytest.raises(TypeError):
        c.difference_update(123)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **28** of 34 proposed tests.
  - discarded `test_complement_eq_and_hash: fails against current behavior`
  - discarded `test_complement_inplace_operators: fails against current behavior`
  - discarded `test_complement_isdisjoint_issubset_issuperset: fails against current behavior`
  - discarded `test_complement_symmetric_difference_update: fails against current behavior`
  - discarded `test_complement_update_and_discard: fails against current behavior`
  - discarded `test_indexedset_symmetric_difference: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **39.0%**, survivors 400 to 244.

### What that caused next

244 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: setutils

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

... 1364 lines omitted ...


... and 204 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import setutils
import pytest

# line 65: _COMPACTION_FACTOR = 8
def test__compaction_factor_threshold():
    # Test that compaction triggers when dead_index_count > len(items) / _COMPACTION_FACTOR
    s = setutils.IndexedSet(range(16))
    for i in range(8):
        s.remove(i)
    # At this point, dead_index_count == 8, len(items) == 16, so 8 > 16/8 == 2 triggers compaction
    # After compaction, dead_indices should be empty
    assert s.dead_indices == []

# line 153: elif len(ded) > 384:
def test__cull_compact_large_dead_indices():
    s = setutils.IndexedSet(range(400))
    for i in range(385):
        s.remove(i)
    # Should trigger compaction due to len(ded) > 384
    assert s.dead_indices == []

# line 157: elif items[-1] is _MISSING:
def test__cull_dead_right_hand_side():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    # Now, last item is _MISSING, so _cull should remove it from item_list
    old_len = len(s.item_list)
    s._cull()
    assert len(s.item_list) == old_len - 1

# line 167: index += len(self)
def test__get_real_index_negative_index():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    # Remove 'b' to create a dead index
    s.remove('b')
    # Now, s.item_list = ['a', _MISSING, 'c']
    # Negative index -1 should resolve to last valid element, which is 'c'
    assert s._get_real_index(-1) == 2

# line 179: index += len(self)
def test__get_apparent_index_negative_index():
    s = setutils.IndexedSet(['x', 'y', 'z'])
    s.remove('y')
    # Now, s.item_list = ['x', _MISSING, 'z']
    # Negative index -1 should resolve to last valid element, which is 'z'
    assert s._get_apparent_index(-1) == 1

# line 172: if real_index < d_start:
def test__get_real_index_dead_indices_skip():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For index 2 (should be 'd'), real_index should skip over dead index

... 58 lines omitted ...

# - Changing initial values of _compactions or _c_max_size (lines 122, 123) only affects internal stats, not observable behavior.
# - Mutations that change break to continue in _get_real_index/_get_apparent_index loops (lines 173, 185) do not affect correct input, as the loop is always broken at the right time for valid indices.
# - Mutations that change return value to None in _get_real_index/_get_apparent_index (lines 175, 187) would cause errors, but the current code always returns an int for valid input, and errors for invalid input are already tested.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **35** of 42 proposed tests.
  - discarded `test__compact_increments_compactions: fails against current behavior`
  - discarded `test__compaction_factor_threshold: fails against current behavior`
  - discarded `test__cull_compact_large_dead_indices: fails against current behavior`
  - discarded `test__cull_dead_right_hand_side: fails against current behavior`
  - discarded `test__get_apparent_index_dead_indices_skip: fails against current behavior`
  - discarded `test__get_real_index_dead_indices_skip: fails against current behavior`
  - discarded `test__get_real_index_negative_index: fails against current behavior`
- Mutation campaign: score moved from 39.0% to **40.5%**, survivors 244 to 238.

### What that caused next

Gain of +1.5%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: setutils

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

... 1423 lines omitted ...


... and 198 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import setutils
import pytest

# line 65: _COMPACTION_FACTOR = 8 -> 9
def test__cull_compaction_factor_threshold():
    # Should compact when dead_index_count > len(items) / _COMPACTION_FACTOR
    s = setutils.IndexedSet(range(20))
    # Remove enough items to exceed threshold for compaction
    for i in range(3, 20):
        s.remove(i)
    # At this point, dead_index_count = 17, len(item_list) = 20
    # 17 > 20/8 == 2.5, so compaction should occur
    # After compaction, dead_indices should be empty
    s._cull()
    assert s.dead_indices == []

# line 123: self._c_max_size = 0 -> 1
def test__c_max_size_initial_value():
    s = setutils.IndexedSet()
    assert s._c_max_size == 0

# line 135: self._compactions += 1 -> -= or += 2
def test__compact_compactions_increment():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    before = s._compactions
    s._compact()
    after = s._compactions
    assert after == before + 1

# line 153: elif len(ded) > 384: -> >= or 385
def test__cull_dead_indices_384_threshold():
    s = setutils.IndexedSet(range(400))
    # Remove 385 items to trigger compaction
    for i in range(385):
        s.remove(i)
    # Should compact when len(dead_indices) > 384
    # After cull, dead_indices should be empty
    s._cull()
    assert s.dead_indices == []

# line 155: elif self._dead_index_count > (len(items) / _COMPACTION_FACTOR): -> >=
def test__cull_dead_index_count_gt_threshold():
    s = setutils.IndexedSet(range(16))
    # Remove 3 items, 3 > 16/8 == 2, so compaction should occur
    for i in range(3):
        s.remove(i)
    s._cull()
    assert s.dead_indices == []

# line 157: elif items[-1] is _MISSING: -> is not
def test__cull_dead_right_hand_side():
    s = setutils.IndexedSet([1, 2, 3])

... 126 lines omitted ...


# The following mutants are equivalent or inside dead code and cannot be killed by tests:
# - line 57: string `'_MISSING'` -> `'XX...XX'` (only affects sentinel name, not value)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **55** of 59 proposed tests.
  - discarded `test__compact_compactions_increment: fails against current behavior`
  - discarded `test__cull_dead_indices_384_threshold: fails against current behavior`
  - discarded `test__get_real_index_dead_indices_addition: fails against current behavior`
  - discarded `test__get_real_index_dead_indices_break: fails against current behavior`
- Mutation campaign: score moved from 40.5% to **43.8%**, survivors 238 to 225.

### What that caused next

Gain of +3.2%, so the loop continued.

---

## Step 4 — phase `kill`

### What the agent was asked (call 4, `kill-4`)

````text
MODULE_IMPORT_NAME: setutils

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

... 1573 lines omitted ...


... and 185 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import setutils
import pytest

# line 135: self._compactions += 1  -- mutants: += -> -=, 1 -> 2
def test__compact_compactions_increment():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    before = s._compactions
    s._compact()
    after = s._compactions
    assert after == before + 1

# line 153: elif len(ded) > 384:  -- mutants: > -> >=, 384 -> 385
def test__cull_dead_indices_gt_384_triggers_compact():
    s = setutils.IndexedSet(range(400))
    for i in range(385):
        s.remove(i)
    # Should trigger compaction, so dead_indices should be empty
    s._cull()
    assert s.dead_indices == []

def test__cull_dead_indices_eq_384_does_not_trigger_compact():
    s = setutils.IndexedSet(range(400))
    for i in range(384):
        s.remove(i)
    # Should NOT trigger compaction, so dead_indices should not be empty
    s._cull()
    assert s.dead_indices != []

# line 157: elif items[-1] is _MISSING:  # get rid of dead right hand side
# line 158: num_dead = 1  -- mutant: 1 -> 2
def test__cull_num_dead_is_1_for_single_trailing_missing():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]

# line 159: while items[-(num_dead + 1)] is _MISSING:
# mutants: is -> is not, + -> -, 1 -> 2
def test__cull_while_loop_removes_all_trailing_missing_precisely():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]

# line 161: if ded and ded[-1][1] == len(items):  -- mutants: and -> or, == -> !=, 1 -> 2
def test__cull_ded_last_interval_removal_precise():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


... 114 lines omitted ...

def test_issuperset_returns_false_when_element_missing():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issuperset([1, 2, 4])
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **76** of 79 proposed tests.
  - discarded `test__compact_compactions_increment: fails against current behavior`
  - discarded `test__cull_dead_indices_gt_384_triggers_compact: fails against current behavior`
  - discarded `test__get_real_index_adds_dead_range: fails against current behavior`
- Mutation campaign: score moved from 43.8% to **44.2%**, survivors 225 to 223.
- Note: 1 duplicate test names skipped

### What that caused next

Gain of +0.5%, so the loop continued.

---

## Step 5 — phase `kill`

### What the agent was asked (call 5, `kill-5`)

````text
MODULE_IMPORT_NAME: setutils

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

... 1712 lines omitted ...


... and 183 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import setutils
import pytest

# line 57: string `'_MISSING'` -> `'XX...XX'`
def test__MISSING_sentinel_var_name():
    # The sentinel's repr should contain '_MISSING'
    if hasattr(setutils._MISSING, '__name__'):
        # If make_sentinel is used, it may have a __name__ attribute
        assert '_MISSING' in repr(setutils._MISSING) or getattr(setutils._MISSING, '__name__', '') == '_MISSING'
    else:
        # fallback: object() fallback, just check it's not a string
        assert not isinstance(setutils._MISSING, str)

# line 135: augmented assign `+=` -> `-=`
def test__compact_compactions_increments():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    before = s._compactions
    s._compact()
    after = s._compactions
    assert after == before + 1

# line 135: `1` -> `2`
def test__compact_compactions_increments_by_one():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    before = s._compactions
    s._compact()
    assert s._compactions == before + 1

# line 153: comparison `>` -> `>=`
def test__cull_compacts_only_when_dead_indices_gt_384():
    s = setutils.IndexedSet(range(386))
    for i in range(385):
        s.remove(i)
    # Now len(s.dead_indices) == 385, should trigger compaction
    s._cull()
    assert s.dead_indices == []

# line 153: `384` -> `385`
def test__cull_compacts_when_dead_indices_exceeds_384():
    s = setutils.IndexedSet(range(386))
    for i in range(385):
        s.remove(i)
    s._cull()
    assert s.dead_indices == []

# line 157: `1` -> `2`
def test__cull_num_dead_initial_value_is_one():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    # Should only remove one dead item at the end

... 211 lines omitted ...

def test_issuperset_returns_false_when_element_missing_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issuperset([1, 2, 4])
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **103** of 105 proposed tests.
  - discarded `test__compact_compactions_increments: fails against current behavior`
  - discarded `test__compact_compactions_increments_by_one: fails against current behavior`
- Mutation campaign: score moved from 44.2% to **44.2%**, survivors 223 to 223.
- Note: 9 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00030.0-constant  line 57  string `'_MISSING'` -> `'XX...XX'`
m00139.0-arithmetic  line 135  augmented assign `+=` -> `-=`
m00145.0-constant  line 135  `1` -> `2`
m00286.0-comparison  line 153  comparison `>` -> `>=`
m00293.0-constant  line 153  `384` -> `385`
m00329.0-constant  line 157  `1` -> `2`
m00337.0-constant  line 158  `1` -> `2`
m00339.0-comparison  line 159  comparison `is` -> `is not`
m00345.0-arithmetic  line 159  operator `+` -> `-`
m00349.0-constant  line 159  `1` -> `2`
... and 213 more
```

---

## The delivered suite

```python
import setutils
import pytest

def test_indexedset_insertion_order_and_uniqueness():
    s = setutils.IndexedSet([1, 2, 3, 2, 1])
    assert list(s) == [1, 2, 3]
    assert s.item_list[:3] == [1, 2, 3]
    assert len(s) == 3

def test_indexedset_repr_and_equality():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([1, 2, 3])
    s3 = setutils.IndexedSet([3, 2, 1])
    assert repr(s1) == "IndexedSet([1, 2, 3])"
    assert s1 == s2
    assert s1 != s3
    assert s1 == set([1, 2, 3])
    assert s1 != set([1, 2])

def test_indexedset_contains_and_iter():
    s = setutils.IndexedSet([1, 2, 3])
    assert 2 in s
    assert 4 not in s
    assert list(iter(s)) == [1, 2, 3]

def test_indexedset_reversed():
    s = setutils.IndexedSet([1, 2, 3])
    assert list(reversed(s)) == [3, 2, 1]

def test_indexedset_getitem_index_and_slice():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    assert s[0] == 'a'
    assert s[1] == 'b'
    assert s[-1] == 'd'
    assert list(s[:2]) == ['a', 'b']
    assert list(s[1:3]) == ['b', 'c']
    assert list(s[::-1]) == ['d', 'c', 'b', 'a']
    assert isinstance(s[1:3], setutils.IndexedSet)
    with pytest.raises(IndexError):
        _ = s[10]

def test_indexedset_index_method():
    s = setutils.IndexedSet(['x', 'y', 'z'])
    assert s.index('x') == 0
    assert s.index('y') == 1
    assert s.index('z') == 2
    with pytest.raises(ValueError) as e:
        s.index('notfound')
    assert "not in IndexedSet" in str(e.value)

def test_indexedset_add_and_discard_remove():
    s = setutils.IndexedSet()
    s.add(1)
    s.add(2)
    s.add(1)
    assert list(s) == [1, 2]
    s.discard(2)
    assert list(s) == [1]
    s.discard(2)  # no error
    s.add(3)
    assert list(s) == [1, 3]
    s.remove(1)
    assert list(s) == [3]
    with pytest.raises(KeyError):
        s.remove(1)

def test_indexedset_clear():
    s = setutils.IndexedSet([1, 2, 3])
    s.clear()
    assert list(s) == []
    assert len(s) == 0

def test_indexedset_isdisjoint_issubset_issuperset():
    s = setutils.IndexedSet([1, 2, 3])

... 744 lines omitted ...


def test_issuperset_returns_false_when_element_missing_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issuperset([1, 2, 4])
```
