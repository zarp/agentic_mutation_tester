# Trajectory: `boltons.namedutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **72.7%** mutation score, 39 tests, 88 of 121 mutants detected, 37s, $0.078.

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
MODULE_IMPORT_NAME: namedutils

Write the characterization suite for this module. Import it with
`import namedutils` and refer to its members through that name.

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

... 370 lines omitted ...


    return result

```
````

### What it returned

````python
```python
import pytest
import namedutils

def test_namedtuple_basic_usage_and_repr():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, tuple)
    assert p.x == 1
    assert p.y == 2
    assert p[0] == 1
    assert p[1] == 2
    assert repr(p) == "Point(x=1, y=2)"
    assert p.__class__.__name__ == "Point"
    assert p.__doc__ == "Point(x, y)"
    assert p._fields == ('x', 'y')

def test_namedtuple_unpacking_and_asdict():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(11, 22)
    x, y = p
    assert (x, y) == (11, 22)
    d = p._asdict()
    assert d == {'x': 11, 'y': 22}
    assert list(d.keys()) == ['x', 'y']
    assert list(d.values()) == [11, 22]

def test_namedtuple_make_and_replace():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point._make([5, 6])
    assert isinstance(p, Point)
    assert p.x == 5
    assert p.y == 6
    p2 = p._replace(x=100)
    assert isinstance(p2, Point)
    assert p2.x == 100
    assert p2.y == 6
    # _replace with unknown field
    with pytest.raises(ValueError) as e:
        p._replace(z=1)
    assert "Got unexpected field names" in str(e.value)

def test_namedtuple_make_wrong_length():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    with pytest.raises(TypeError) as e:
        Point._make([1])
    assert "Expected 2 arguments, got 1" in str(e.value)
    with pytest.raises(TypeError) as e:
        Point._make([1, 2, 3])
    assert "Expected 2 arguments, got 3" in str(e.value)

def test_namedtuple_invalid_typename_and_fieldnames():
    # Invalid typename: contains dash
    with pytest.raises(ValueError) as e:

... 195 lines omitted ...

    assert t1._fields == t2._fields
    assert t1._asdict() == t2._asdict()
    assert repr(t1) == repr(t2)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **23** of 24 proposed tests.
  - discarded `test_namedlist_make_wrong_length: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **72.7%**, survivors 121 to 33.

### What that caused next

33 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: namedutils

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

... 722 lines omitted ...

line 396: string `'__main__'` -> `'XX...XX'`
    result.__module__ = frame.f_globals.get('__name__', '__main__')

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import namedutils
import pytest

# The following mutants are equivalent or untestable:
# - line 64: exec string in Python 2-only dead code, never executed in Python 3.
# - line 70: __all__ string values do not affect runtime behavior in any way tested.
# - line 214/379: __name__ in exec namespace is not observable from outside.
# - line 221/386: SyntaxError message formatting only visible if template is invalid, which is not testable without breaking the suite.
# - line 229/395: _getframe(1) vs _getframe(2) only affects __module__ attribute, which is not exposed in the API or tested.
# - line 230/396: __module__ fallback string is not observable in any public API.
# - line 169/328: The mutant changes == to != in a condition that is always True for valid input, so cannot be killed without breaking input validation.
# - line 169/328: The string '_' in the isalnum check is not observable unless you pass invalid field names, which is already tested.
# - line 179/183/186/191/194/338/342/345/350/353: Error message string changes only, not observable except by breaking input validation, which is already tested.
# - line 221/386: string ':\n' -> 'XX...XX' in SyntaxError message, not observable without breaking the code.
# - line 70: string 'namedtuple'/'namedlist' in __all__, not observable.

def test_namedtuple_verbose_flag_prints_class_definition(capsys):
    # line 138: verbose=False -> True
    # If verbose=True, the class definition should be printed to stdout.
    T = namedutils.namedtuple('VerbosePoint', ['x', 'y'], verbose=True)
    out = capsys.readouterr().out
    assert "class VerbosePoint(tuple):" in out
    assert "def __new__(_cls, x, y):" in out
    # The returned class should still work
    t = T(1, 2)
    assert t.x == 1
    assert t.y == 2

def test_namedlist_verbose_flag_prints_class_definition(capsys):
    # line 297: verbose=False -> True
    T = namedutils.namedlist('VerboseList', ['a', 'b'], verbose=True)
    out = capsys.readouterr().out
    assert "class VerboseList(list):" in out
    assert "def __new__(_cls, a, b):" in out
    t = T(3, 4)
    assert t.a == 3
    assert t.b == 4
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **25** of 25 proposed tests.
- Mutation campaign: score moved from 72.7% to **72.7%**, survivors 33 to 33.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: namedutils

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

... 747 lines omitted ...

line 396: string `'__main__'` -> `'XX...XX'`
    result.__module__ = frame.f_globals.get('__name__', '__main__')

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import namedutils

# The following mutants are equivalent or unkillable:
# - line 64: string 'exec code in global_...' -> 'XX...XX'
#   (This is only used in Python 2, and the exec_ function is not called in any test, so cannot be killed.)
# - line 70: string 'namedlist' -> 'XX...XX'
# - line 70: string 'namedtuple' -> 'XX...XX'
#   (These only affect __all__, which is not used or asserted in any test.)
# - line 214: string 'namedtuple_%s' -> 'XX...XX'
# - line 229: 1 -> 2
# - line 230: string '__name__' -> 'XX...XX'
# - line 230: string '__main__' -> 'XX...XX'
# - line 297: False -> True (default argument, but always explicitly set in tests)
# - line 379: string 'namedlist_%s' -> 'XX...XX'
# - line 395: 1 -> 2
# - line 396: string '__name__' -> 'XX...XX'
# - line 396: string '__main__' -> 'XX...XX'
# These cannot be killed by any test that does not inspect __all__ or frame internals.

def test_namedtuple_invalid_fieldname_character():
    # line 169: comparison == -> !=
    # Should reject field names with invalid characters (e.g., dash)
    try:
        namedutils.namedtuple('Point', ['x-y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid field name"

def test_namedtuple_invalid_fieldname_character_underscore():
    # line 169: string '_' -> 'XX...XX'
    # Should still allow underscores in field names
    try:
        namedutils.namedtuple('Point', ['x_y'])
    except ValueError:
        assert False, "Underscore should be allowed in field names"

def test_namedtuple_invalid_typename_message():
    # line 179: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Bad-Type', ['x', 'y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid typename"

def test_namedtuple_keyword_fieldname_message():
    # line 183: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Point', ['for'])
    except ValueError as e:
        assert "cannot be a keyword" in str(e)
    else:

... 114 lines omitted ...

        assert "bad" in str(e)
    else:
        assert False, "Expected SyntaxError for invalid class definition"
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **39** of 41 proposed tests.
  - discarded `test_namedlist_syntaxerror_message_and_concat: fails against current behavior`
  - discarded `test_namedtuple_syntaxerror_message_and_concat: fails against current behavior`
- Mutation campaign: score moved from 72.7% to **72.7%**, survivors 33 to 33.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00034.0-constant  line 64  string `'exec code in global_...'` -> `'XX...XX'`
m00063.0-constant  line 70  string `'namedlist'` -> `'XX...XX'`
m00064.0-constant  line 70  string `'namedtuple'` -> `'XX...XX'`
m00088.0-constant  line 138  `False` -> `True`
m00164.0-comparison  line 169  comparison `==` -> `!=`
m00168.0-constant  line 169  string `'_'` -> `'XX...XX'`
m00263.0-constant  line 179  string `'Type names and field...'` -> `'XX...XX'`
m00278.0-constant  line 183  string `'Type names and field...'` -> `'XX...XX'`
m00296.0-constant  line 186  string `'Type names and field...'` -> `'XX...XX'`
m00329.0-constant  line 191  string `'Field names cannot s...'` -> `'XX...XX'`
... and 23 more
```

---

## The delivered suite

```python
import pytest
import namedutils

def test_namedtuple_basic_usage_and_repr():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, tuple)
    assert p.x == 1
    assert p.y == 2
    assert p[0] == 1
    assert p[1] == 2
    assert repr(p) == "Point(x=1, y=2)"
    assert p.__class__.__name__ == "Point"
    assert p.__doc__ == "Point(x, y)"
    assert p._fields == ('x', 'y')

def test_namedtuple_unpacking_and_asdict():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(11, 22)
    x, y = p
    assert (x, y) == (11, 22)
    d = p._asdict()
    assert d == {'x': 11, 'y': 22}
    assert list(d.keys()) == ['x', 'y']
    assert list(d.values()) == [11, 22]

def test_namedtuple_make_and_replace():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point._make([5, 6])
    assert isinstance(p, Point)
    assert p.x == 5
    assert p.y == 6
    p2 = p._replace(x=100)
    assert isinstance(p2, Point)
    assert p2.x == 100
    assert p2.y == 6
    # _replace with unknown field
    with pytest.raises(ValueError) as e:
        p._replace(z=1)
    assert "Got unexpected field names" in str(e.value)

def test_namedtuple_make_wrong_length():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    with pytest.raises(TypeError) as e:
        Point._make([1])
    assert "Expected 2 arguments, got 1" in str(e.value)
    with pytest.raises(TypeError) as e:
        Point._make([1, 2, 3])
    assert "Expected 2 arguments, got 3" in str(e.value)

def test_namedtuple_invalid_typename_and_fieldnames():
    # Invalid typename: contains dash
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Bad-Type', ['x', 'y'])
    assert "alphanumeric characters and underscores" in str(e.value)
    # Invalid fieldname: is a keyword
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['for'])
    assert "cannot be a keyword" in str(e.value)
    # Invalid fieldname: starts with digit
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['1x'])
    assert "cannot start with a number" in str(e.value)
    # Invalid fieldname: starts with underscore
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['_x'])
    assert "cannot start with an underscore" in str(e.value)
    # Duplicate fieldname
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['x', 'x'])
    assert "duplicate field name" in str(e.value)

def test_namedtuple_rename_option():
    # Should rename invalid and duplicate fields

... 329 lines omitted ...

    except ValueError as e:
        assert "duplicate field name" in str(e)
    else:
        assert False, "Expected ValueError for duplicate field name"
```
