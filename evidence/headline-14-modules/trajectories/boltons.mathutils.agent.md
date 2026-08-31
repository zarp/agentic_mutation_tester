# Trajectory: `boltons.mathutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **100.0%** mutation score, 61 tests, 116 of 116 mutants detected, 62s, $0.087.

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
    assert mathutils.clamp(1000, -100, 100) == 100

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-1e10, lower=-1e20) == -1e10
    assert mathutils.clamp(1e10, upper=1e20) == 1e10

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(4.0) == 4
    assert mathutils.ceil(-2.7) == -2

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(49, options=options) == 50

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

... 193 lines omitted ...

def test_bits_repr():
    b = mathutils.Bits('1011')
    assert repr(b) == "Bits('1011')"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **39** of 43 proposed tests.
  - discarded `test_bits_as_hex: fails against current behavior`
  - discarded `test_bits_init_from_bytes: fails against current behavior`
  - discarded `test_bits_or_and_notimplemented_for_other_type: fails against current behavior`
  - discarded `test_floor_with_options_returns_largest_lte: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **83.6%**, survivors 116 to 19.

### What that caused next

19 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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

... 524 lines omitted ...

line 225: operator `//` -> `/`
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

# line 152: `0` -> `1`
def test_bits_default_val_is_zero():
    b = mathutils.Bits()
    assert b.val == 0
    assert b.len == 1  # len('{0:b}'.format(0)) == 1
    assert b.as_bin() == '0'

# line 169: `0` -> `1`
def test_bits_init_from_empty_string_gives_zero():
    b = mathutils.Bits('')
    assert b.val == 0
    assert b.len == 0  # len_ is set to len(val) == 0 for empty string
    assert b.as_bin() == ''

# line 172: comparison `<` -> `<=` and line 172: `0` -> `1`
def test_bits_init_zero_allowed_but_not_negative():
    b = mathutils.Bits(0)
    assert b.val == 0
    assert b.len == 1
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    assert "cannot represent negative values" in str(e.value)

# line 176: comparison `>` -> `>=`
def test_bits_init_value_equal_to_2_pow_len_not_allowed():
    # 2**3 == 8, so 8 with len 3 should raise
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 3)
    assert "cannot be represented with" in str(e.value)

# line 200: return value replaced with `None`
def test_bits_eq_notimplemented_for_other_type_is_notimplemented():
    b = mathutils.Bits('1011')
    result = b.__eq__(11)
    assert result is NotImplemented

# line 205: return value replaced with `None`
def test_bits_or_and_notimplemented_for_other_type():
    b = mathutils.Bits('1011')
    result_or = b.__or__(11)
    result_and = b.__and__(11)
    assert result_or is NotImplemented
    assert result_and is NotImplemented

# line 225: operator `+` -> `-` and line 225: operator `//` -> `/`

... 19 lines omitted ...

# - line 171: string change in exception message
# - line 173: string change in exception message
# - line 177: string change in exception message
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **45** of 47 proposed tests.
  - discarded `test_bits_init_from_empty_string_gives_zero: fails against current behavior`
  - discarded `test_bits_init_value_equal_to_2_pow_len_not_allowed: fails against current behavior`
- Mutation campaign: score moved from 83.6% to **90.5%**, survivors 19 to 11.

### What that caused next

Gain of +6.9%, so the loop continued.

---

## Step 3 - phase `kill`

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

... 553 lines omitted ...

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
    # Ensure the error message is exactly as in the original code
    assert 'expected upper bound' in str(e.value)
    assert '>= lower bound' in str(e.value)

def test_ceil_with_options_no_gte_error_message_and_format():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    msg = str(e.value)
    assert "no ceil options greater than or equal to" in msg
    assert ": 4" in msg

def test_floor_with_options_no_lte_error_message_and_format():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    msg = str(e.value)
    assert "no floor options less than or equal to" in msg
    assert ": 5" in msg

def test_bits_init_from_bytes_decode_ascii():
    # This test ensures that val.decode('ascii') is used, not another encoding
    b = mathutils.Bits(b'1011')
    assert b.val == 11
    assert b.len == 4
    assert b.as_bin() == '1011'

def test_bits_init_from_unicode_empty_string_sets_val_zero():
    # This test ensures that empty unicode string sets val = 0, not val = 1
    b = mathutils.Bits(u'')
    assert b.val == 0
    assert b.len == 0
    assert b.as_bin() == ''

def test_bits_init_bad_type_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    msg = str(e.value)
    assert "initialized with bad type" in msg
    assert "float" in msg

def test_bits_init_negative_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    msg = str(e.value)
    assert "Bits cannot represent negative values" in msg


... 12 lines omitted ...

#   but the tests above assert on the original message content, so these are covered.
# - Changing operator % to * in error message formatting (lines 96, 123, 171, 177) is not equivalent,
#   as it would raise a TypeError instead of ValueError, but the tests above will fail if the wrong operator is used.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **52** of 53 proposed tests.
  - discarded `test_bits_init_from_unicode_empty_string_sets_val_zero: fails against current behavior`
- Mutation campaign: score moved from 90.5% to **94.0%**, survivors 11 to 7.

### What that caused next

Gain of +3.4%, so the loop continued.

---

## Step 4 - phase `kill`

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

... 603 lines omitted ...

line 177: string `'value {0} cannot be ...'` -> `'XX...XX'`
    raise ValueError('value {0} cannot be represented with {1} bits'.format(val, len_))

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

# The following tests are to kill surviving mutants that only change error message strings.
# These mutants cannot be killed by input/output value assertions, but only by checking the exact error message.
# The existing suite already checks the relevant error messages for all such cases:
# - clamp upper < lower (line 70)
# - ceil with no gte option (line 96)
# - floor with no lte option (line 123)
# - Bits bad type (line 171)
# - Bits negative value (line 173)
# - Bits value too large for len (line 177)
# Therefore, no new tests are needed for these string mutants.

# The only surviving mutant that is not a string change is:
# line 169: `val = 0` -> `val = 1`
# This is in Bits __init__, when initializing from an empty string (unicode or bytes).
# The original code sets val = 0 if the string is empty; the mutant sets val = 1.
# We need a test that initializes Bits with an empty string and asserts the value is 0.

def test_bits_init_from_empty_string_results_in_zero():
    b = mathutils.Bits('')
    assert b.val == 0
    assert b.len == 0

def test_bits_init_from_empty_unicode_results_in_zero():
    b = mathutils.Bits(u'')
    assert b.val == 0
    assert b.len == 0

def test_bits_init_from_empty_bytes_results_in_zero():
    b = mathutils.Bits(b'')
    assert b.val == 0
    assert b.len == 0
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **55** of 55 proposed tests.
- Mutation campaign: score moved from 94.0% to **94.8%**, survivors 7 to 6.

### What that caused next

Gain of +0.9%, so the loop continued.

---

## Step 5 - phase `kill`

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

... 618 lines omitted ...

line 177: string `'value {0} cannot be ...'` -> `'XX...XX'`
    raise ValueError('value {0} cannot be represented with {1} bits'.format(val, len_))

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import mathutils
import pytest

# The following tests ensure that the exact error messages are preserved.
# They are not redundant with the existing tests, which only check for substrings.

def test_clamp_upper_less_than_lower_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert str(e.value) == "expected upper bound (0) >= lower bound (5)"

def test_ceil_with_options_no_gte_exact_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    assert str(e.value) == "no ceil options greater than or equal to: 4"

def test_floor_with_options_no_lte_exact_error_message():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    assert str(e.value) == "no floor options less than or equal to: 5"

def test_bits_init_bad_type_exact_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    assert str(e.value) == "initialized with bad type: float"

def test_bits_init_negative_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    assert str(e.value) == "Bits cannot represent negative values"

def test_bits_init_value_too_large_for_len_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(5, 2)
    assert str(e.value) == "value 5 cannot be represented with 2 bits"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **61** of 61 proposed tests.
- Mutation campaign: score moved from 94.8% to **100.0%**, survivors 6 to 0.

### What that caused next

Gain of +5.2%, so the loop continued.

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
    assert mathutils.clamp(1000, -100, 100) == 100

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-1e10, lower=-1e20) == -1e10
    assert mathutils.clamp(1e10, upper=1e20) == 1e10

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(4.0) == 4
    assert mathutils.ceil(-2.7) == -2

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(49, options=options) == 50

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
    assert mathutils.floor(4.0) == 4
    assert mathutils.floor(-2.7) == -3


def test_floor_with_options_no_lte_raises():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    assert "no floor options less than or equal to" in str(e.value)

def test_floor_with_unsorted_options():
    options = [10, 1, 5]
    assert mathutils.floor(6, options=options) == 5

def test_bits_init_from_int_and_len():
    b = mathutils.Bits(5, 4)
    assert b.val == 5
    assert b.len == 4
    assert b.as_bin() == '0101'

def test_bits_init_from_int_no_len():

... 318 lines omitted ...

def test_bits_init_value_too_large_for_len_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(5, 2)
    assert str(e.value) == "value 5 cannot be represented with 2 bits"
```
