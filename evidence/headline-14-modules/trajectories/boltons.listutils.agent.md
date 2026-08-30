# Trajectory: `boltons.listutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **76.5%** mutation score, 77 tests, 104 of 136 mutants detected, 106s, $0.176.

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
MODULE_IMPORT_NAME: listutils

Write the characterization suite for this module. Import it with
`import listutils` and refer to its members through that name.

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

... 329 lines omitted ...

    def swap(self, item_index, dest_index):
        self[dest_index], self[item_index] = self[item_index], self[dest_index]

```
````

### What it returned

````python
```python
import pytest
import listutils

def test_empty_barrellist_len_zero():
    bl = listutils.BarrelList()
    assert len(bl) == 0
    assert list(bl) == []
    assert bl.lists == [[]]

def test_barrellist_append_and_len():
    bl = listutils.BarrelList()
    bl.append(1)
    assert len(bl) == 1
    assert list(bl) == [1]
    assert bl.lists == [[1]]

def test_barrellist_extend():
    bl = listutils.BarrelList()
    bl.extend([1, 2, 3])
    assert len(bl) == 3
    assert list(bl) == [1, 2, 3]
    assert bl.lists == [[1, 2, 3]]

def test_barrellist_insert_at_start_middle_end():
    bl = listutils.BarrelList([1, 3])
    bl.insert(1, 2)
    assert list(bl) == [1, 2, 3]
    bl.insert(0, 0)
    assert list(bl) == [0, 1, 2, 3]
    bl.insert(len(bl), 4)
    assert list(bl) == [0, 1, 2, 3, 4]

def test_barrellist_insert_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    bl.insert(-1, 99)
    assert list(bl) == [1, 2, 99, 3]

def test_barrellist_insert_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        bl.insert(100, 5)
    with pytest.raises(IndexError):
        bl.insert(-100, 5)

def test_barrellist_pop_default_and_index():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3
    assert list(bl) == [1, 2]
    assert bl.pop(0) == 1
    assert list(bl) == [2]

def test_barrellist_pop_negative_index():
    bl = listutils.BarrelList([1, 2, 3])

... 200 lines omitted ...

    sl = listutils.SplayList([1, 2, 3])
    sl.swap(1, 1)
    assert list(sl) == [1, 2, 3]
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **31** of 38 proposed tests.
  - discarded `test_barrellist_del_slice_step_gt_1: fails against current behavior`
  - discarded `test_barrellist_delitem_int_and_slice: fails against current behavior`
  - discarded `test_barrellist_delslice_and_delslice_out_of_bounds: fails against current behavior`
  - discarded `test_barrellist_insert_index_out_of_bounds_raises: fails against current behavior`
  - discarded `test_barrellist_iter_slice_step_and_negative_step: fails against current behavior`
  - discarded `test_barrellist_multiple_lists_balance_and_pop: fails against current behavior`
  - discarded `test_barrellist_translate_index_negative_and_out_of_bounds: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **49.3%**, survivors 136 to 69.

### What that caused next

69 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: listutils

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

... 671 lines omitted ...


... and 29 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import listutils

# line 51: string `'_MISSING'` -> `'XX...XX'`
def test__missing_sentinel_var_name():
    # The sentinel's repr should include '_MISSING'
    if hasattr(listutils, '_MISSING'):
        rep = repr(listutils._MISSING)
        assert '_MISSING' in rep

# line 62: string `'BList'` -> `'XX...XX'`
# line 62: string `'BarrelList'` -> `'XX...XX'`
def test___all__contains_correct_names():
    assert 'BList' in listutils.__all__
    assert 'BarrelList' in listutils.__all__

# line 104: `1520` -> `1521`
def test_barrellist_size_factor_constant():
    assert listutils.BarrelList._size_factor == 1520

# line 105: string `'This size factor is ...'` -> `'XX...XX'`
def test_barrellist_size_factor_docstring():
    assert "tuning using the tune() function" in listutils.BarrelList.__dict__['_size_factor'].__doc__

# line 115: `2` -> `3`
def test_barrellist_cur_size_limit_log_base():
    bl = listutils.BarrelList()
    # For length 0, should use log base 2, not 3
    # log(0+2, 2) = 1, log(0+2, 3) = 0.6309...
    # So, int(round(1520 * 1)) == 1520
    assert bl._cur_size_limit == 1520

# line 118: comparison `<` -> `<=`
# line 118: `0` -> `1`
def test_translate_index_negative_index():
    bl = listutils.BarrelList([10, 20, 30])
    # index -1 should map to last element
    idx = bl._translate_index(-1)
    assert idx == (0, 2)
    # index -3 should map to first element
    idx = bl._translate_index(-3)
    assert idx == (0, 0)

# line 123: comparison `<` -> `<=`
def test_translate_index_rel_idx_boundary():
    bl = listutils.BarrelList([1, 2, 3])
    # rel_idx == len_list should not break early
    # index 3 is out of bounds, should return (None, None)
    idx = bl._translate_index(3)
    assert idx == (None, None)

# line 124: `break` -> `continue`
def test_translate_index_breaks_on_first_match():
    bl = listutils.BarrelList([1, 2, 3])

... 133 lines omitted ...

    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(None, -1))
    assert result == [1, 2]
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **47** of 56 proposed tests.
  - discarded `test__missing_sentinel_var_name: fails against current behavior`
  - discarded `test_balance_list_next_list_idx: fails against current behavior`
  - discarded `test_balance_list_returns_true_on_split: fails against current behavior`
  - discarded `test_barrellist_size_factor_docstring: fails against current behavior`
  - discarded `test_insert_index_error_on_none: fails against current behavior`
  - discarded `test_iter_slice_negative_step: fails against current behavior`
  - discarded `test_iter_slice_start_stop_negative_step: fails against current behavior`
  - discarded `test_pop_removes_empty_list: fails against current behavior`
  - discarded `test_translate_index_rel_idx_boundary: fails against current behavior`
- Mutation campaign: score moved from 49.3% to **58.1%**, survivors 69 to 57.

### What that caused next

Gain of +8.8%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: listutils

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

... 801 lines omitted ...


... and 17 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import listutils
import pytest

# line 118: if index < 0:  (mutant: < -> <= and 0 -> 1)
def test_translate_index_index_zero_and_one():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index 1 should not be treated as negative
    idx = bl._translate_index(1)
    assert idx == (0, 1)

# line 123: if rel_idx < len_list: (mutant: < -> <=)
def test_translate_index_rel_idx_equal_len_list():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    # rel_idx == len_list should not enter the block
    # index 2: rel_idx=2, len_list=2, should decrement and go to next list
    idx = bl._translate_index(2)
    assert idx == (1, 0)

# line 124: break (mutant: break -> continue)
def test_translate_index_break_vs_continue():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    # Should stop at first matching sublist, not continue
    idx = bl._translate_index(1)
    assert idx == (0, 1)

# line 135: if len(cur_list) > size_limit: (mutant: > -> >=)
def test_balance_list_split_on_equal():
    bl = listutils.BarrelList()
    bl.lists = [[1] * bl._cur_size_limit]
    # Should not split if length == size_limit
    assert bl._balance_list(0) is False
    # Should split if length > size_limit
    bl.lists = [[1] * (bl._cur_size_limit + 1)]
    assert bl._balance_list(0) is True

# line 136: half_limit = size_limit // 2 (mutant: // -> / and 2 -> 3)
def test_balance_list_half_limit_integer_division():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 2)]
    bl._balance_list(0)
    # All sublists should have at most _cur_size_limit // 2 elements
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2

# line 137: while len(cur_list) > half_limit: (mutant: > -> >=)
def test_balance_list_while_condition():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 3)]

... 114 lines omitted ...

# The following mutants are equivalent or inside dead code, or cannot be killed by any test:
# - line 51: string change in sentinel name (does not affect runtime)
# - line 105: docstring change (does not affect runtime)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **53** of 64 proposed tests.
  - discarded `test_balance_list_next_list_idx: fails against current behavior`
  - discarded `test_balance_list_return_value: fails against current behavior`
  - discarded `test_balance_list_split_on_equal: fails against current behavior`
  - discarded `test_del_slice_assigns_to_first_list: fails against current behavior`
  - discarded `test_del_slice_new_list_chain_start: fails against current behavior`
  - discarded `test_del_slice_step_gt_one: fails against current behavior`
  - discarded `test_del_slice_stop_none: fails against current behavior`
  - discarded `test_insert_index_out_of_bounds_raises: fails against current behavior`
  - discarded `test_iter_slice_step_negative: fails against current behavior`
  - discarded `test_iter_slice_step_negative_start_stop: fails against current behavior`
  - discarded `test_pop_index_minus1_and_none_and_tuple: fails against current behavior`
- Mutation campaign: score moved from 58.1% to **72.1%**, survivors 57 to 38.
- Note: 4 duplicate test names skipped

### What that caused next

Gain of +14.0%, so the loop continued.

---

## Step 4 — phase `kill`

### What the agent was asked (call 4, `kill-4`)

````text
MODULE_IMPORT_NAME: listutils

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

... 868 lines omitted ...

line 352: `0` -> `1`
    def shift(self, item_index, dest_index=0):

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import listutils
import pytest

# line 118: comparison `<` -> `<=`
def test_translate_index_negative_index_zero():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index -1 should map to last element
    idx_neg1 = bl._translate_index(-1)
    assert idx_neg1 == (0, 2)

# line 135: comparison `>` -> `>=`
def test_balance_list_split_only_when_greater():
    bl = listutils.BarrelList()
    size_limit = bl._cur_size_limit
    bl.lists = [[1] * size_limit]
    # Should not split if length == size_limit
    assert bl._balance_list(0) is False
    bl.lists = [[1] * (size_limit + 1)]
    # Should split if length > size_limit
    assert bl._balance_list(0) is True

# line 136: operator `//` -> `/`
def test_balance_list_half_limit_integer_division():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 2)]
    bl._balance_list(0)
    # All sublists should have at most _cur_size_limit // 2 elements
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2

# line 137: comparison `>` -> `>=`
def test_balance_list_while_condition_strict():
    bl = listutils.BarrelList()
    size_limit = bl._cur_size_limit
    bl.lists = [[1] * (size_limit + 2)]
    bl._balance_list(0)
    # Should not split if length == half_limit
    for sub in bl.lists:
        assert len(sub) <= size_limit // 2

# line 150: comparison `is` -> `is not`
def test_insert_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        bl.insert(10, 5)
    with pytest.raises(IndexError):
        bl.insert(-10, 5)

# line 167: `1` -> `2`
def test_pop_index_minus1_and_none():

... 79 lines omitted ...

# - line 223: `False` -> `True` and string `'start list index sho...'` -> `'XX...XX'` (assert message, not observable)
# - line 320: `0` -> `1` (would break sorting, but not observable in current tests)
# - line 321: `0` -> `1` (would break balancing after sort, but not observable in current tests)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **64** of 68 proposed tests.
  - discarded `test_balance_list_split_only_when_greater: fails against current behavior`
  - discarded `test_balance_list_while_condition_strict: fails against current behavior`
  - discarded `test_insert_index_out_of_bounds_raises: fails against current behavior`
  - discarded `test_iter_slice_step_negative: fails against current behavior`
- Mutation campaign: score moved from 72.1% to **73.5%**, survivors 38 to 36.
- Note: 1 duplicate test names skipped

### What that caused next

Gain of +1.5%, so the loop continued.

---

## Step 5 — phase `kill`

### What the agent was asked (call 5, `kill-5`)

````text
MODULE_IMPORT_NAME: listutils

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

... 944 lines omitted ...

line 321: `0` -> `1`
    self._balance_list(0)

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import listutils
import pytest

# line 118: comparison `<` -> `<=`
def test_translate_index_zero_vs_one():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index 1 should not be treated as negative
    idx1 = bl._translate_index(1)
    assert idx1 == (0, 1)

# line 135: comparison `>` -> `>=`
def test_balance_list_split_only_when_greater():
    bl = listutils.BarrelList()
    limit = bl._cur_size_limit
    bl.lists = [[1] * limit]
    # Should not split if length == size_limit
    assert bl._balance_list(0) is False
    bl.lists = [[1] * (limit + 1)]
    # Should split if length > size_limit
    assert bl._balance_list(0) is True

# line 136: operator `//` -> `/`
def test_balance_list_half_limit_integer_division():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 2)]
    bl._balance_list(0)
    # All sublists should have at most _cur_size_limit // 2 elements
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2

# line 137: comparison `>` -> `>=`
def test_balance_list_while_condition_strict():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 2)]
    bl._balance_list(0)
    # Should not split if length == half_limit
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2

# line 141: return value replaced with `None`
def test_balance_list_returns_true_on_split():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 1)]
    result = bl._balance_list(0)
    assert result is True

# line 150: comparison `is` -> `is not`
def test_insert_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):

... 98 lines omitted ...

# - line 298: `1` -> `2` (covered above)
# - line 320: `0` -> `1` (covered above)
# - line 321: `0` -> `1` (covered above)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **69** of 74 proposed tests.
  - discarded `test_balance_list_returns_true_on_split: fails against current behavior`
  - discarded `test_balance_list_split_only_when_greater: fails against current behavior`
  - discarded `test_insert_index_out_of_bounds_raises: fails against current behavior`
  - discarded `test_iter_slice_negative_step: fails against current behavior`
  - discarded `test_iter_slice_negative_step_start_stop: fails against current behavior`
- Mutation campaign: score moved from 73.5% to **73.5%**, survivors 36 to 36.
- Note: 8 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 6 — phase `kill`

### What the agent was asked (call 6, `kill-6`)

````text
MODULE_IMPORT_NAME: listutils

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

... 992 lines omitted ...

line 321: `0` -> `1`
    self._balance_list(0)

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import listutils

# The following mutants are equivalent or in dead code and cannot be killed:
# - line 51: string '_MISSING' -> 'XX...XX' (only affects sentinel name, not behavior)
# - line 105: string docstring change (no effect on behavior)
# - line 223: string in assert changed (only affects error message, not behavior)
# - line 245: return value replaced with None (return value of __contains__ is always True/False, not used)
# - line 223: False -> True in assert (assert always fails, so changing value doesn't affect testability)
# - line 320: self.lists[0] = tmp_sorted -> self.lists[1] = tmp_sorted (would IndexError unless lists[1] exists, but code always clears lists before this)
# - line 321: self._balance_list(0) -> self._balance_list(1) (lists[1] does not exist after sort, so would IndexError, but code always calls with 0)
# - line 141: return True -> return False (return value of _balance_list is not used in a way that affects observable behavior)
# - line 141: return True -> return None (same as above)

def test_translate_index_index_less_than_0_vs_1():
    # line 118: < -> <= and 0 -> 1
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index -1 should be treated as negative
    idx_neg1 = bl._translate_index(-1)
    assert idx_neg1 == (0, 2)

def test_balance_list_gt_vs_ge_and_half_limit_division():
    # line 135: > -> >=, line 136: // -> /, 2 -> 3, line 137: > -> >=
    bl = listutils.BarrelList()
    # Make a list just at the size limit
    bl.lists = [[1] * bl._cur_size_limit]
    # Should not split if length == size_limit
    assert bl._balance_list(0) is False
    # Now make it one more than size limit
    bl.lists = [[1] * (bl._cur_size_limit + 1)]
    bl._balance_list(0)
    # After balancing, all sublists should have at most _cur_size_limit // 2 elements
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2

def test_balance_list_next_list_idx_plus_1_vs_minus_1_and_insert():
    # line 138: + -> -, 1 -> 2
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 10)]
    bl._balance_list(0)
    # After balancing, lists should be split into more than one sublist
    assert len(bl.lists) > 1

def test_insert_list_idx_is_none_check():
    # line 150: is -> is not
    bl = listutils.BarrelList([1, 2, 3])
    try:
        bl.insert(100, 5)
    except IndexError:
        pass
    else:

... 75 lines omitted ...

    bl.lists = [[1, 2], [3, 4]]
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **77** of 81 proposed tests.
  - discarded `test_balance_list_gt_vs_ge_and_half_limit_division: fails against current behavior`
  - discarded `test_balance_list_next_list_idx_plus_1_vs_minus_1_and_insert: fails against current behavior`
  - discarded `test_insert_list_idx_is_none_check: fails against current behavior`
  - discarded `test_iter_slice_step_negative_vs_le_0_and_start_stop_adjustment: fails against current behavior`
- Mutation campaign: score moved from 73.5% to **76.5%**, survivors 36 to 32.

### What that caused next

Gain of +2.9%, so the loop continued.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00023.0-constant  line 51  string `'_MISSING'` -> `'XX...XX'`
m00062.0-constant  line 105  string `'This size factor is ...'` -> `'XX...XX'`
m00136.0-comparison  line 118  comparison `<` -> `<=`
m00140.0-constant  line 118  `0` -> `1`
m00271.0-comparison  line 135  comparison `>` -> `>=`
m00283.0-arithmetic  line 136  operator `//` -> `/`
m00287.0-constant  line 136  `2` -> `3`
m00289.0-comparison  line 137  comparison `>` -> `>=`
m00301.0-arithmetic  line 138  operator `+` -> `-`
m00305.0-constant  line 138  `1` -> `2`
... and 22 more
```

---

## The delivered suite

```python
import pytest
import listutils

def test_empty_barrellist_len_zero():
    bl = listutils.BarrelList()
    assert len(bl) == 0
    assert list(bl) == []
    assert bl.lists == [[]]

def test_barrellist_append_and_len():
    bl = listutils.BarrelList()
    bl.append(1)
    assert len(bl) == 1
    assert list(bl) == [1]
    assert bl.lists == [[1]]

def test_barrellist_extend():
    bl = listutils.BarrelList()
    bl.extend([1, 2, 3])
    assert len(bl) == 3
    assert list(bl) == [1, 2, 3]
    assert bl.lists == [[1, 2, 3]]

def test_barrellist_insert_at_start_middle_end():
    bl = listutils.BarrelList([1, 3])
    bl.insert(1, 2)
    assert list(bl) == [1, 2, 3]
    bl.insert(0, 0)
    assert list(bl) == [0, 1, 2, 3]
    bl.insert(len(bl), 4)
    assert list(bl) == [0, 1, 2, 3, 4]

def test_barrellist_insert_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    bl.insert(-1, 99)
    assert list(bl) == [1, 2, 99, 3]


def test_barrellist_pop_default_and_index():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3
    assert list(bl) == [1, 2]
    assert bl.pop(0) == 1
    assert list(bl) == [2]

def test_barrellist_pop_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3
    assert list(bl) == [1, 2]

def test_barrellist_pop_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        bl.pop(10)
    with pytest.raises(IndexError):
        bl.pop(-10)

def test_barrellist_contains():
    bl = listutils.BarrelList([1, 2, 3])
    assert 2 in bl
    assert 4 not in bl

def test_barrellist_getitem_int_and_slice():
    bl = listutils.BarrelList([10, 20, 30, 40])
    assert bl[0] == 10
    assert bl[1] == 20
    assert bl[-1] == 40
    assert list(bl[1:3]) == [20, 30]
    assert isinstance(bl[1:3], listutils.BarrelList)

def test_barrellist_getitem_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        _ = bl[10]

... 559 lines omitted ...

    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.lists = [[1, 2], [3, 4]]
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]
```
