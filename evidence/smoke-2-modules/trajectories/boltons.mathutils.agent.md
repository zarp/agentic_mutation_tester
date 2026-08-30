# Trajectory: `boltons.mathutils`, agent arm

Run `20260830-022152-smoke` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **100.0%** mutation score, 66 tests, 116 of 116 mutants detected, 80s, $0.103.

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
MODULE_IMPORT_NAME: mathutils

Write the characterization suite for this module. Import it with
`import mathutils` and refer to its members through that name.

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

... 231 lines omitted ...

        cn = self.__class__.__name__
        return "{0}('{1}')".format(cn, self.as_bin())

```
````

### What it returned

````python
```python
import mathutils
import pytest

def test_clamp_within_bounds_returns_value():
    assert mathutils.clamp(1.0, 0, 5) == 1.0
    assert mathutils.clamp(3, 1, 10) == 3
    assert mathutils.clamp(0, 0, 5) == 0
    assert mathutils.clamp(5, 0, 5) == 5

def test_clamp_below_lower_returns_lower():
    assert mathutils.clamp(-1.0, 0, 5) == 0
    assert mathutils.clamp(-100, -10, 10) == -10

def test_clamp_above_upper_returns_upper():
    assert mathutils.clamp(101.0, 0, 5) == 5
    assert mathutils.clamp(123, upper=5) == 5
    assert mathutils.clamp(1000, -10, 10) == 10

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-100) == -100
    assert mathutils.clamp(100, lower=0) == 100
    assert mathutils.clamp(-100, upper=0) == -100

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(-1.2) == -1
    assert mathutils.ceil(0) == 0
    assert mathutils.ceil(5) == 5

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0.5, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(26, options=options) == 35
    assert mathutils.ceil(50, options=options) == 50

def test_ceil_with_options_exact_match():
    options = [1, 2, 3]
    assert mathutils.ceil(2, options=options) == 2

def test_ceil_with_options_no_gte_raises():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    assert "no ceil options greater than or equal to" in str(e.value)

... 195 lines omitted ...

def test_bits_repr():
    b = mathutils.Bits(5, 4)
    assert repr(b) == "Bits('0101')"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **45** of 46 proposed tests.
  - discarded `test_floor_with_options_returns_largest_lte: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **85.3%**, survivors 116 to 17.

### What that caused next

17 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: mathutils

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

... 535 lines omitted ...

line 225: `8` -> `9`
    tmpl = '%0{0}X'.format(2 * (self.len // 8 + ((self.len % 8) != 0)))

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

# line 69: comparison `<` -> `<=`
def test_clamp_upper_equal_lower_allowed():
    # Should not raise when upper == lower
    assert mathutils.clamp(5, 5, 5) == 5

# line 70: string change in error message (unobservable if exception is not raised)
# Already covered by test_clamp_upper_less_than_lower_raises

# line 96: operator `%` -> `*`
def test_ceil_with_options_no_gte_error_message_contains_x():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # The error message should contain the value of x (4)
    assert "4" in str(e.value)

# line 96: string change in error message (unobservable if exception is not raised)
# Already covered by test_ceil_with_options_no_gte_raises

# line 123: string change in error message (unobservable if exception is not raised)
# Already covered by test_floor_with_options_no_lte_raises

# line 152: `0` -> `1` (default val for Bits)
def test_bits_default_init_is_zero():
    b = mathutils.Bits()
    assert b.val == 0
    # Should be length 1 (since 0 in binary is '0')
    assert b.len == 1
    assert b.as_bin() == '0'

# line 159: comparison `is` -> `is not` (if len_ is None)
def test_bits_len_is_none_sets_len():
    b = mathutils.Bits(3)
    # 3 in binary is '11', so len should be 2
    assert b.len == 2

# line 169: `0` -> `1` (val = 0 if val is empty string)
def test_bits_init_from_empty_bin_string_gives_zero():
    b = mathutils.Bits('')
    assert b.val == 0
    assert b.len == 0

# line 171: string change in error message (unobservable if exception is not raised)
# Already covered by test_bits_init_bad_type_raises

# line 172: comparison `<` -> `<=` and line 172: `0` -> `1`
def test_bits_init_zero_allowed():
    b = mathutils.Bits(0)
    assert b.val == 0
    assert b.len == 1

... 36 lines omitted ...

    # 1 bit: should be 2 hex digits (1 byte)
    b4 = mathutils.Bits(1, 1)
    assert b4.as_hex() == '01'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **53** of 54 proposed tests.
  - discarded `test_bits_init_value_equal_to_2_pow_len_allowed: fails against current behavior`
- Mutation campaign: score moved from 85.3% to **94.0%**, survivors 17 to 7.

### What that caused next

Gain of +8.6%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: mathutils

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

... 570 lines omitted ...

line 177: string `'value {0} cannot be ...'` -> `'XX...XX'`
    raise ValueError('value {0} cannot be represented with {1} bits'.format(val, len_))

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

def test_clamp_upper_less_than_lower_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    # The error message should contain 'expected upper bound'
    assert "expected upper bound" in str(e.value)

def test_ceil_with_options_no_gte_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # The error message should contain 'no ceil options greater than or equal to'
    assert "no ceil options greater than or equal to" in str(e.value)

def test_floor_with_options_no_lte_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
    # The error message should contain 'no floor options less than or equal to'
    assert "no floor options less than or equal to" in str(e.value)

def test_bits_init_bad_type_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    # The error message should contain 'bad type'
    assert "bad type" in str(e.value)

def test_bits_init_negative_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    # The error message should contain 'Bits cannot represent negative values'
    assert "Bits cannot represent negative values" in str(e.value)

def test_bits_init_value_too_large_for_len_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 2)
    # The error message should contain 'cannot be represented with'
    assert "cannot be represented with" in str(e.value)

# The mutant at line 176 (comparison > -> >=) is equivalent for all valid inputs:
# If val == 2 ** len_, then len('{0:b}'.format(val)) > len_, so len_ would be set to a higher value,
# or the user explicitly passed len_ too small, which is already tested by the value-too-large test.
# The current suite already covers this, and no further test can distinguish the mutant.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **59** of 59 proposed tests.
- Mutation campaign: score moved from 94.0% to **94.0%**, survivors 7 to 7.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 4 — phase `kill`

### What the agent was asked (call 4, `kill-4`)

````text
MODULE_IMPORT_NAME: mathutils

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

... 614 lines omitted ...

line 177: string `'value {0} cannot be ...'` -> `'XX...XX'`
    raise ValueError('value {0} cannot be represented with {1} bits'.format(val, len_))

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

def test_clamp_upper_less_than_lower_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('expected upper bound')

def test_ceil_with_options_no_gte_error_message_exact():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('no ceil options greater than or equal to')

def test_floor_with_options_no_lte_error_message_exact():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('no floor options less than or equal to')

def test_bits_init_bad_type_error_message_exact():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('initialized with bad type')

def test_bits_init_negative_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('Bits cannot represent negative values')

def test_bits_init_value_too_large_for_len_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 2)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('value 8 cannot be represented with 2 bits')

# The mutant at line 176 (comparison > -> >=) cannot be killed:
# If val == 2 ** len_, then '{0:b}'.format(val) will have len_+1 digits,
# so len_ will be set to len_+1, and the check will not trigger.
# If len_ is provided, then val == 2 ** len_ is not representable in len_ bits,
# so the check is correct. The current tests already cover the > case.
# There is no input that distinguishes > from >= here, because
# Bits(4, 2) and Bits(4, 2) both raise, and Bits(4, 3) is allowed.
# So, no test can kill this mutant.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **65** of 65 proposed tests.
- Mutation campaign: score moved from 94.0% to **99.1%**, survivors 7 to 1.

### What that caused next

Gain of +5.2%, so the loop continued.

---

## Step 5 — phase `kill`

### What the agent was asked (call 5, `kill-5`)

````text
MODULE_IMPORT_NAME: mathutils

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

... 640 lines omitted ...

line 176: comparison `>` -> `>=`
    if val > 2 ** len_:

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

def test_bits_init_value_equal_to_2_pow_len_allowed():
    # The original code raises ValueError if val > 2 ** len_
    # The mutant would allow val == 2 ** len_, but the original allows it too.
    # Let's check the boundary: val == 2 ** len_ should raise in the original.
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 3)  # 8 == 2 ** 3
    assert "cannot be represented with" in str(e.value)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **65** of 66 proposed tests.
  - discarded `test_bits_init_value_equal_to_2_pow_len_allowed: fails against current behavior`
- Mutation campaign: score moved from 99.1% to **99.1%**, survivors 1 to 1.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 6 — phase `kill`

### What the agent was asked (call 6, `kill-6`)

````text
MODULE_IMPORT_NAME: mathutils

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

... 642 lines omitted ...

line 176: comparison `>` -> `>=`
    if val > 2 ** len_:

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

def test_bits_init_value_equal_to_2_pow_len_allowed():
    # Original: if val > 2 ** len_: raise
    # Mutant:   if val >= 2 ** len_: raise
    # So val == 2 ** len_ should be allowed in original, but not in mutant.
    # For len_ = 3, val = 8 (2 ** 3)
    b = mathutils.Bits(8, 3)
    assert b.val == 8
    assert b.len == 3
    assert b.as_bin() == '1000'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **66** of 66 proposed tests.
- Mutation campaign: score moved from 99.1% to **100.0%**, survivors 1 to 0.

### What that caused next

Gain of +0.9%, so the loop continued.

---

## The delivered suite

```python
import mathutils
import pytest

def test_clamp_within_bounds_returns_value():
    assert mathutils.clamp(1.0, 0, 5) == 1.0
    assert mathutils.clamp(3, 1, 10) == 3
    assert mathutils.clamp(0, 0, 5) == 0
    assert mathutils.clamp(5, 0, 5) == 5

def test_clamp_below_lower_returns_lower():
    assert mathutils.clamp(-1.0, 0, 5) == 0
    assert mathutils.clamp(-100, -10, 10) == -10

def test_clamp_above_upper_returns_upper():
    assert mathutils.clamp(101.0, 0, 5) == 5
    assert mathutils.clamp(123, upper=5) == 5
    assert mathutils.clamp(1000, -10, 10) == 10

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-100) == -100
    assert mathutils.clamp(100, lower=0) == 100
    assert mathutils.clamp(-100, upper=0) == -100

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(-1.2) == -1
    assert mathutils.ceil(0) == 0
    assert mathutils.ceil(5) == 5

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0.5, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(26, options=options) == 35
    assert mathutils.ceil(50, options=options) == 50

def test_ceil_with_options_exact_match():
    options = [1, 2, 3]
    assert mathutils.ceil(2, options=options) == 2

def test_ceil_with_options_no_gte_raises():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    assert "no ceil options greater than or equal to" in str(e.value)

def test_ceil_with_unsorted_options():
    options = [10, 1, 5]
    assert mathutils.ceil(2, options=options) == 5

def test_floor_no_options_behaves_like_math_floor():
    assert mathutils.floor(3.7) == 3
    assert mathutils.floor(-1.2) == -2
    assert mathutils.floor(0) == 0
    assert mathutils.floor(5) == 5


def test_floor_with_options_exact_match():
    options = [1, 2, 3]
    assert mathutils.floor(2, options=options) == 2

def test_floor_with_options_no_lte_raises():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
    assert "no floor options less than or equal to" in str(e.value)

... 328 lines omitted ...

    b = mathutils.Bits(8, 3)
    assert b.val == 8
    assert b.len == 3
    assert b.as_bin() == '1000'
```
