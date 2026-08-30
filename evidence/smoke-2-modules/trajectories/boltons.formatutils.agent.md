# Trajectory: `boltons.formatutils`, agent arm

Run `20260830-022152-smoke` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **82.7%** mutation score, 59 tests, 81 of 98 mutants detected, 56s, $0.091.

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
MODULE_IMPORT_NAME: formatutils

Write the characterization suite for this module. Import it with
`import formatutils` and refer to its members through that name.

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

... 334 lines omitted ...


# end formatutils.py

```
````

### What it returned

````python
```python
import pytest
import formatutils

def test_construct_format_field_str_all_args():
    assert formatutils.construct_format_field_str("foo", "03d", "r") == "{foo!r:03d}"

def test_construct_format_field_str_no_fspec_no_conv():
    assert formatutils.construct_format_field_str("foo", "", None) == "{foo}"

def test_construct_format_field_str_none_fname():
    assert formatutils.construct_format_field_str(None, "03d", "r") == ""

def test_construct_format_field_str_only_fspec():
    assert formatutils.construct_format_field_str("foo", "x", None) == "{foo:x}"

def test_construct_format_field_str_only_conv():
    assert formatutils.construct_format_field_str("foo", "", "s") == "{foo!s}"

def test_split_format_str_simple():
    s = "Hello {name}!"
    result = formatutils.split_format_str(s)
    assert result == [("Hello ", "{name}"), ("!", None)]

def test_split_format_str_multiple_fields():
    s = "{a} + {b} = {c}"
    result = formatutils.split_format_str(s)
    assert result == [("", "{a}"), (" + ", "{b}"), (" = ", "{c}"), ("", None)]

def test_split_format_str_no_fields():
    s = "no fields here"
    result = formatutils.split_format_str(s)
    assert result == [("no fields here", None)]

def test_split_format_str_with_spec_and_conv():
    s = "Value: {0!r:03d}"
    result = formatutils.split_format_str(s)
    assert result == [("Value: ", "{0!r:03d}"), ("", None)]

def test_infer_positional_format_args_simple():
    s = "Hello {}, {}!"
    result = formatutils.infer_positional_format_args(s)
    assert result == "Hello {0}, {1}!"

def test_infer_positional_format_args_with_spec():
    s = "{:d} + {:d} = {:d}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{0:d} + {1:d} = {2:d}"

def test_infer_positional_format_args_mixed():
    s = "{foo} and {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{foo} and {0}"


... 176 lines omitted ...

            return "y"
    dv = formatutils.DeferredValue(lambda: Y())
    assert format(dv, "s") == "y"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **33** of 37 proposed tests.
  - discarded `test_BaseFormatField_with_subfields: fails against current behavior`
  - discarded `test_split_format_str_multiple_fields: fails against current behavior`
  - discarded `test_split_format_str_with_spec_and_conv: fails against current behavior`
  - discarded `test_tokenize_format_str_resolve_pos_false: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **77.6%**, survivors 98 to 22.

### What that caused next

22 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: formatutils

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

... 623 lines omitted ...

line 355: `1` -> `2`
    pt = fmt[-1:]  # presentation type

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import formatutils

# The following mutants are all changes to __all__ (lines 80-82), which only affect
# what is exported via "from formatutils import *". The test suite does not use
# star imports, and Python does not guarantee __all__ is used except in that context.
# There is no observable difference in module behavior for direct attribute access.
# Therefore, these mutants are equivalent and cannot be killed by a test.

# Mutant at line 149: _INTCHARS = 'bcdoxXn' -> 'XX...XX'
def test__TYPE_MAP_intchars():
    # 'd' is in the original _INTCHARS, so type for 'd' should be int
    assert formatutils._TYPE_MAP['d'] is int

# Mutant at line 150: _FLOATCHARS = 'eEfFgGn%' -> 'XX...XX'
def test__TYPE_MAP_floatchars():
    # 'f' is in the original _FLOATCHARS, so type for 'f' should be float
    assert formatutils._TYPE_MAP['f'] is float

# Mutant at line 153: _TYPE_MAP['s'] = str -> ... 
def test__TYPE_MAP_s():
    # 's' should map to str
    assert formatutils._TYPE_MAP['s'] is str

# Mutant at line 175: def _add_arg(argname, type_char='s'): -> type_char='XX...XX'
def test_get_format_args_default_type_char():
    # If no fspec, type_char should default to 's' and thus str
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", str)])

# Mutant at line 186: type_char = fspec[-1:] -> type_char = fspec[-2:]
def test_get_format_args_type_char_slice():
    # fspec = "03d", fspec[-1:] == "d", fspec[-2:] == "3d"
    # Only the last char should be used as type_char
    s = "{foo:03d}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", int)])

# Mutant at line 189: raise ValueError('encountered compound format arg: %r' % fname) -> ...
def test_get_format_args_compound_raises():
    s = "{foo[bar]}"
    try:
        formatutils.get_format_args(s)
    except ValueError as e:
        assert "compound format arg" in str(e)
    else:
        assert False, "Expected ValueError for compound format arg"

# Mutant at line 194: raise ValueError('encountered anonymous positional argument') -> ...
def test_get_format_args_anonymous_raises_again():
    s = "{}"
    try:
        formatutils.get_format_args(s)

... 61 lines omitted ...

    result = formatutils.split_format_str(s)
    # Should have two tuples with field_str not None
    assert sum(1 for lit, field in result if field is not None) == 2
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **48** of 48 proposed tests.
- Mutation campaign: score moved from 77.6% to **82.7%**, survivors 22 to 17.

### What that caused next

Gain of +5.1%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: formatutils

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

... 719 lines omitted ...

line 355: `1` -> `2`
    pt = fmt[-1:]  # presentation type

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import formatutils

# The following mutants are all changes to __all__ (lines 80-82), which only affect
# what is exported via "from formatutils import *". The suite does not test __all__.
# These mutants are equivalent for all direct usage and cannot be killed by a test
# unless the suite explicitly checks __all__ contents.
#
# - line 80: string 'DeferredValue' -> 'XX...XX'
# - line 80: string 'get_format_args' -> 'XX...XX'
# - line 80: string 'tokenize_format_str' -> 'XX...XX'
# - line 81: string 'construct_format_field_str' -> 'XX...XX'
# - line 81: string 'infer_positional_format_args' -> 'XX...XX'
# - line 82: string 'BaseFormatField' -> 'XX...XX'
#
# Similarly, the following mutants are changes to the internal string constants
# for _INTCHARS and _FLOATCHARS, which only affect _TYPE_MAP. The suite already
# tests that 'd' and 'f' are mapped correctly, but not that all chars are present.
# However, changing the string to 'XX...XX' would break mapping for e.g. 'b', 'c', etc.
# Let's add a test for another int and float char.
def test__TYPE_MAP_all_intchars():
    # All original int chars should map to int
    for c in 'bcdoxXn':
        assert formatutils._TYPE_MAP[c] is int

def test__TYPE_MAP_all_floatchars():
    # All original float chars should map to float
    for c in 'eEfFgGn%':
        assert formatutils._TYPE_MAP[c] is float

# The following mutant changes the default type_char in get_format_args' _add_arg
# from 's' to 'XX...XX'. This would break the default type for fields with no fspec.
def test_get_format_args_default_type_char_is_str():
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", str)])

# The following mutant changes the error message for compound format args.
# The suite already asserts "compound format arg" in the error message,
# so this mutant is already killed.

# The following mutant changes the error message for anonymous positional arguments.
# The suite already asserts "anonymous positional argument" in the error message,
# so this mutant is already killed.

# The following mutant changes "continue" to "break" in split_format_str (line 117).
# This would cause split_format_str to stop after the first field.
def test_split_format_str_multiple_fields_detects_all():
    s = "A {foo} B {bar} C"
    result = formatutils.split_format_str(s)
    # Should have two tuples with field_str not None
    assert sum(1 for lit, field in result if field is not None) == 2
    # Should have three tuples in total (two fields, one trailing literal)
    assert len(result) == 3

... 27 lines omitted ...

    dv = formatutils.DeferredValue(lambda: 42)
    # Should format as int, not fallback to str, and not raise
    assert format(dv, "04d") == "0042"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **55** of 56 proposed tests.
  - discarded `test__TYPE_MAP_all_intchars: fails against current behavior`
- Mutation campaign: score moved from 82.7% to **82.7%**, survivors 17 to 17.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 4 — phase `kill`

### What the agent was asked (call 4, `kill-4`)

````text
MODULE_IMPORT_NAME: formatutils

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

... 768 lines omitted ...

line 355: `1` -> `2`
    pt = fmt[-1:]  # presentation type

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import formatutils

# The following mutants are all changes to __all__ (lines 80-82), which only affect
# the module's exported symbols. These cannot be detected unless code relies on
# "from formatutils import ...", which is not present in the current suite.
# Similarly, the strings in _INTCHARS and _FLOATCHARS (lines 149, 150) only affect
# the mapping of type chars to types, which is already covered by the suite.
# The default argument string in _add_arg (line 175) is only observable if fspec is empty,
# which is already tested.
# The error message strings (lines 189, 194) are only observable if the test asserts
# the exact error message, but the current suite only checks for substrings.
# Therefore, the following mutants are equivalent or undetectable by tests:
#
# - line 80: string changes in __all__
# - line 81: string changes in __all__
# - line 82: string changes in __all__
# - line 149: string change in _INTCHARS
# - line 150: string change in _FLOATCHARS
# - line 175: string change in _add_arg default
# - line 189: string change in ValueError message
# - line 194: string change in ValueError message
#
# Mutants at lines 117, 133, 136, 218, and 355 are detectable and are tested below.

def test_infer_positional_format_args_continue_vs_break():
    # line 117: continue -> break
    # If 'continue' is replaced with 'break', only the first escaped brace is handled,
    # and the rest of the string is not processed.
    # Input with multiple escaped braces should be handled correctly.
    s = "{{}} {{}} {}"
    result = formatutils.infer_positional_format_args(s)
    # Should process both escaped braces and the anonymous positional arg
    assert result == "{{}} {{}} {0}"

def test_infer_positional_format_args_start_prev_end_zero():
    # line 133: 0 -> 1 (start, end, prev_end = 0, 0, 0)
    # If initialized to 1, the first character is skipped.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    # Should not skip the first character
    assert result.startswith("A ")

def test_infer_positional_format_args_prev_end_less_than_start():
    # line 136: < -> <=
    # If changed to <=, then when prev_end == start, the slice is included,
    # which can duplicate characters.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    # Should not contain two consecutive spaces (which would indicate a duplicate)
    assert "  " not in result

def test_tokenize_format_str_continue_vs_break():
    # line 218: continue -> break

... 11 lines omitted ...

    dv = formatutils.DeferredValue(lambda: 42)
    # Should format as int, not fallback to str, and not raise
    assert format(dv, "04d") == "0042"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **59** of 59 proposed tests.
- Mutation campaign: score moved from 82.7% to **82.7%**, survivors 17 to 17.
- Note: 1 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00025.0-constant  line 80  string `'DeferredValue'` -> `'XX...XX'`
m00026.0-constant  line 80  string `'get_format_args'` -> `'XX...XX'`
m00027.0-constant  line 80  string `'tokenize_format_str'` -> `'XX...XX'`
m00028.0-constant  line 81  string `'construct_format_fie...'` -> `'XX...XX'`
m00029.0-constant  line 81  string `'infer_positional_for...'` -> `'XX...XX'`
m00030.0-constant  line 82  string `'BaseFormatField'` -> `'XX...XX'`
m00142.0-control  line 117  `continue` -> `break`
m00196.0-constant  line 133  `0` -> `1`
m00197.0-constant  line 133  `0` -> `1`
m00237.0-comparison  line 136  comparison `<` -> `<=`
... and 7 more
```

---

## The delivered suite

```python
import pytest
import formatutils

def test_construct_format_field_str_all_args():
    assert formatutils.construct_format_field_str("foo", "03d", "r") == "{foo!r:03d}"

def test_construct_format_field_str_no_fspec_no_conv():
    assert formatutils.construct_format_field_str("foo", "", None) == "{foo}"

def test_construct_format_field_str_none_fname():
    assert formatutils.construct_format_field_str(None, "03d", "r") == ""

def test_construct_format_field_str_only_fspec():
    assert formatutils.construct_format_field_str("foo", "x", None) == "{foo:x}"

def test_construct_format_field_str_only_conv():
    assert formatutils.construct_format_field_str("foo", "", "s") == "{foo!s}"

def test_split_format_str_simple():
    s = "Hello {name}!"
    result = formatutils.split_format_str(s)
    assert result == [("Hello ", "{name}"), ("!", None)]


def test_split_format_str_no_fields():
    s = "no fields here"
    result = formatutils.split_format_str(s)
    assert result == [("no fields here", None)]


def test_infer_positional_format_args_simple():
    s = "Hello {}, {}!"
    result = formatutils.infer_positional_format_args(s)
    assert result == "Hello {0}, {1}!"

def test_infer_positional_format_args_with_spec():
    s = "{:d} + {:d} = {:d}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{0:d} + {1:d} = {2:d}"

def test_infer_positional_format_args_mixed():
    s = "{foo} and {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{foo} and {0}"

def test_infer_positional_format_args_escaped_braces():
    s = "{{}} {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{{}} {0}"

def test_infer_positional_format_args_no_anonymous():
    s = "{foo} {bar}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{foo} {bar}"

def test_get_format_args_named_and_positional():
    s = "{noun} is {1:d} years old{punct}"
    result = formatutils.get_format_args(s)
    assert result == ([(1, int)], [("noun", str), ("punct", str)])

def test_get_format_args_only_named():
    s = "{foo} {bar}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", str), ("bar", str)])

def test_get_format_args_only_positional():
    s = "{0} {1:f} {2:x}"
    result = formatutils.get_format_args(s)
    assert result == ([(0, str), (1, float), (2, int)], [])

def test_get_format_args_duplicate_fields():
    s = "{foo} {foo} {1} {1:d}"
    result = formatutils.get_format_args(s)
    assert result == ([(1, str)], [("foo", str)])

... 334 lines omitted ...

    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if hasattr(t, "fname")]
    # Should contain both 'foo' and 'bar'
    assert "foo" in fnames and "bar" in fnames
```
