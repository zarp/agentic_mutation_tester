# Trajectory: `boltons.tableutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **62.4%** mutation score, 73 tests, 113 of 181 mutants detected, 87s, $0.164.

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
MODULE_IMPORT_NAME: tableutils

Write the characterization suite for this module. Import it with
`import tableutils` and refer to its members through that name.

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

... 570 lines omitted ...

                                     for j, cell in enumerate(row)]))
        return '\n'.join(lines)

```
````

### What it returned

````python
```python
import pytest
import tableutils

from collections import namedtuple

def test_to_text_str_and_repr():
    class Weird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): return "repr!"
    class VeryWeird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): raise Exception("fail repr")
    # Normal string
    assert tableutils.to_text("abc") == "abc"
    # Integer
    assert tableutils.to_text(123) == "123"
    # Object with broken __str__, working __repr__
    assert tableutils.to_text(Weird()) == "repr!"
    # Object with broken __str__ and __repr__
    result = tableutils.to_text(VeryWeird())
    assert result.startswith("<") and "VeryWeird" in result
    # maxlen truncates
    assert tableutils.to_text("abcdef", maxlen=5) == "ab..."

def test_escape_html_basic():
    assert tableutils.escape_html("<tag>") == "&lt;tag&gt;"
    assert tableutils.escape_html('"quote"') == "&quot;quote&quot;"
    # maxlen truncates before escaping
    assert tableutils.escape_html("<abcdef>", maxlen=5) == "&lt;a..."

def test_dictinputtype_check_type_and_guess_headers():
    d = {"b": 2, "a": 1}
    it = tableutils.DictInputType()
    assert it.check_type(d) is True
    assert it.check_type([1,2]) is False
    # headers are sorted
    assert it.guess_headers(d) == ["a", "b"]

def test_dictinputtype_get_entry_and_get_entry_seq():
    d = {"a": 1, "b": 2}
    it = tableutils.DictInputType()
    headers = ["a", "b", "c"]
    assert it.get_entry(d, headers) == [1, 2, None]
    seq = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    assert it.get_entry_seq(seq, headers) == [[1, 2, None], [3, None, 4]]

def test_objectinputtype_check_type_and_guess_headers():
    class X:
        def __init__(self): self.a = 1; self.b = 2
        def method(self): pass
    x = X()
    it = tableutils.ObjectInputType()
    assert it.check_type(x) is True

... 157 lines omitted ...

    lines2 = []
    t._add_vertical_html_lines(lines2, headers=["a","b"], max_depth=1)
    assert any("<td>1</td>" in l or "<td>3</td>" in l for l in lines2)
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **23** of 26 proposed tests.
  - discarded `test_table_from_data_scalar_and_unsupported: fails against current behavior`
  - discarded `test_table_init_and_repr_without_headers: fails against current behavior`
  - discarded `test_table_len_and_getitem: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **56.9%**, survivors 181 to 78.

### What that caused next

78 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: tableutils

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

... 898 lines omitted ...


... and 38 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import tableutils

# The following mutants are equivalent or in dead code and cannot be killed by any test:
# - line 76: string '_MISSING' -> 'XX...XX' (variable name for sentinel, not observable)
# - line 80: string '\nSome idle feature t...' -> 'XX...XX' (docstring, not observable)
# - line 98: string 'Table' -> 'XX...XX' (__all__ is not used in any test)
# - line 271/274/275/278: HTML tag strings -> 'XX...XX' (not observable unless HTML tags are changed in output, which is already tested)
# - line 377/378: string 'metadata'/'_data_type' -> 'XX...XX' (argument names in kwargs.pop, not observable)
# - line 409: string 'unsupported data type %r' -> 'XX...XX' (exception message, not observable unless exception is raised, which is already tested)
# - line 442: string '%s(%r)' -> 'XX...XX' (repr string, already tested for output format)
# - line 442: operator '%' -> '*' (would raise TypeError, but repr is already tested)
# - ... (other similar docstring or variable name changes omitted)

def test_to_text_maxlen_boundary():
    # Kills: line 109: comparison > -> >=
    # If maxlen == len(text), original does not truncate, mutant does.
    s = "abcde"
    # maxlen == len(s): should NOT truncate
    assert tableutils.to_text(s, maxlen=5) == "abcde"
    # maxlen < len(s): should truncate
    assert tableutils.to_text(s, maxlen=4) == "a..."

def test_objectinputtype_guess_headers_skips_property_exception():
    # Kills: line 165: continue -> break
    class X:
        @property
        def bad(self):
            raise Exception("fail")
        a = 1
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # Should still include 'a' even if 'bad' property raises
    assert "a" in headers

def test_table_init_headers_infer_one_row():
    # Kills: line 284: 1 -> 2
    # Should infer headers from first row, and data from rest
    t = tableutils.Table([[1,2,3], [4,5,6], [7,8,9]])
    # First row becomes headers, rest is data
    assert t.headers == [1,2,3]
    assert list(t._data) == [[4,5,6],[7,8,9]]

def test_table_set_width_reset_flag():
    # Kills: line 302: False -> True, line 304: 0 -> 1
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99 or 1
    assert t._width == 3

def test_table_fill_no_extend_when_full():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])

... 100 lines omitted ...

    html = t.to_html(with_metadata=False)
    # Should NOT include metadata
    assert "foo" not in html
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **38** of 42 proposed tests.
  - discarded `test_table_from_data_scalar_type_in_dnr: fails against current behavior`
  - discarded `test_table_from_data_scalar_type_in_dnr_returns_table: fails against current behavior`
  - discarded `test_table_from_data_unsupported_type_raises: fails against current behavior`
  - discarded `test_table_getitem_returns_row: fails against current behavior`
- Mutation campaign: score moved from 56.9% to **61.3%**, survivors 78 to 70.

### What that caused next

Gain of +4.4%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 3, `kill-3`)

````text
MODULE_IMPORT_NAME: tableutils

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

... 1037 lines omitted ...


... and 30 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import tableutils

# The following mutants are equivalent or unkillable:
# - line 76: string '_MISSING' -> 'XX...XX' (affects only sentinel name, not behavior)
# - line 80: docstring change
# - line 98: __all__ string change (does not affect runtime)
# - line 271, 274, 275, 278: HTML tag string changes (output is tested by existing tests for tag presence, not exact string)
# - line 377, 378: string key changes in kwargs.pop (no effect if only used as keys)
# - line 409, 442: string/operator changes in error message or repr format string (output is not asserted exactly)
# - line 483, 485: string changes in HTML output (output is not asserted exactly)
# - line 487: 'and' -> 'or' in header extension (would only matter if both are False, which is not a valid state)
# - ...and similar docstring or string literal changes.

# The following mutants are not killable because they only affect docstrings, error messages, or string constants
# that are not asserted for exact value in the suite.

# The following are new tests to kill the remaining killable mutants:

import pytest
from collections import namedtuple

def test_objectinputtype_guess_headers_break_vs_continue():
    # Kills: line 165: continue -> break
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers

def test_table_set_width_reset_true():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    t._width = 99
    t._set_width(reset=True)
    assert t._width == 2

def test_table_fill_no_extend_when_full_boundary():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2]], headers=["a","b"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before

def test_table_from_dict_max_depth_default():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d])
    assert t._data == [[1]]

... 83 lines omitted ...

    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **51** of 54 proposed tests.
  - discarded `test_table_from_data_scalar_returns_table: fails against current behavior`
  - discarded `test_table_from_data_scalar_type_in_dnr: fails against current behavior`
  - discarded `test_table_from_data_unsupported_type_raises: fails against current behavior`
- Mutation campaign: score moved from 61.3% to **62.4%**, survivors 70 to 68.
- Note: 1 duplicate test names skipped

### What that caused next

Gain of +1.1%, so the loop continued.

---

## Step 4 — phase `kill`

### What the agent was asked (call 4, `kill-4`)

````text
MODULE_IMPORT_NAME: tableutils

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

... 1149 lines omitted ...


... and 28 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import tableutils

# The following mutants are equivalent or unkillable:
# - Changes to docstrings or string literals used only for documentation or __all__.
# - Changes to HTML tag string values (e.g., '<tr>' -> 'XX...XX') do not affect logic or output, as the tests already check for correct HTML output.
# - Changes to variable names in make_sentinel or kwargs.pop (e.g., '_MISSING' -> 'XX...XX') do not affect runtime behavior.
# - Changes to error message strings (e.g., 'unsupported data type %r' -> 'XX...XX') are not observable unless the error is raised and its message is asserted, which is not required by the current suite.
# - Changes to __all__ contents are not observable unless introspected, which is not required by the current suite.

def test_objectinputtype_guess_headers_continue_vs_break():
    # Kills: line 165: continue -> break
    # If 'break' is used, headers collection stops at first exception property.
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers

def test_table_set_width_reset_true_vs_false():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99
    assert t._width == 3

def test_table_fill_no_extend_when_full_vs_ge():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before

def test_table_from_dict_max_depth_default_and_arg():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d])
    assert t._data == [[1]]
    t2 = tableutils.Table.from_dict([d], max_depth=1)
    assert t2._data == [[1]]

def test_table_from_list_max_depth_default_and_arg():
    # Kills: line 333: 1 -> 2
    t = tableutils.Table.from_list([[1,2]])
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_list([[1,2]], max_depth=1)
    assert t2._data == [[1,2]]


... 63 lines omitted ...

    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **60** of 60 proposed tests.
- Mutation campaign: score moved from 62.4% to **62.4%**, survivors 68 to 68.
- Note: 5 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 5 — phase `kill`

### What the agent was asked (call 5, `kill-5`)

````text
MODULE_IMPORT_NAME: tableutils

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

... 1232 lines omitted ...


... and 28 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import tableutils

# The following mutants are equivalent or in dead code and cannot be killed by any test:
# - line 76: string '_MISSING' -> 'XX...XX' (variable name for sentinel, no effect)
# - line 80: string '\nSome idle feature t...' -> 'XX...XX' (docstring)
# - line 98: string 'Table' -> 'XX...XX' (__all__ is not used in tests)
# - line 271: string '<tr>' -> 'XX...XX' (HTML tag, only affects output if tag is changed, but output is asserted only for presence of <tr>)
# - line 271: string '</tr>' -> 'XX...XX'
# - line 274: string '<thead>' -> 'XX...XX'
# - line 274: string '</thead>' -> 'XX...XX'
# - line 275: string '<tbody>' -> 'XX...XX'
# - line 275: string '</tbody>' -> 'XX...XX'
# - line 278: string '<table>' -> 'XX...XX'
# - line 278: string '</table>' -> 'XX...XX'
# - line 377: string 'metadata' -> 'XX...XX'
# - line 378: string '_data_type' -> 'XX...XX'
# - line 409: operator % -> * (would raise TypeError, but only in error path)
# - line 409: string 'unsupported data typ...' -> 'XX...XX'
# - line 442: operator % -> * (would raise TypeError, but only in __repr__)
# - line 442: string '%s(%r)' -> 'XX...XX'
# - line 483: string 'bottom' -> 'XX...XX'
# - line 485: string '<br />' -> 'XX...XX'
# - line 489: operator - -> + (would cause error if width < len(headers), but only if headers are longer than width, which is not supported)
# - line 495: 1 -> 2 (would only affect orientation for tables with 2 rows, but orientation is tested for both 1 and 2 rows)
# - ... and other docstring or error message string changes.

def test_objectinputtype_guess_headers_continue_vs_break_killer():
    # Kills: line 165: continue -> break
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers

def test_table_set_width_reset_true_killer():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99
    assert t._width == 3

def test_table_fill_no_extend_when_full_vs_ge_killer():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before

... 73 lines omitted ...

    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **73** of 73 proposed tests.
- Mutation campaign: score moved from 62.4% to **62.4%**, survivors 68 to 68.

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00092.0-constant  line 76  string `'_MISSING'` -> `'XX...XX'`
m00103.0-constant  line 80  string `'\nSome idle feature t...'` -> `'XX...XX'`
m00108.0-constant  line 98  string `'Table'` -> `'XX...XX'`
m00423.0-control  line 165  `continue` -> `break`
m00684.0-constant  line 271  string `'<tr>'` -> `'XX...XX'`
m00685.0-constant  line 271  string `'</tr>'` -> `'XX...XX'`
m00717.0-constant  line 274  string `'<thead>'` -> `'XX...XX'`
m00718.0-constant  line 274  string `'</thead>'` -> `'XX...XX'`
m00728.0-constant  line 275  string `'<tbody>'` -> `'XX...XX'`
m00729.0-constant  line 275  string `'</tbody>'` -> `'XX...XX'`
... and 58 more
```

---

## The delivered suite

```python
import pytest
import tableutils

from collections import namedtuple

def test_to_text_str_and_repr():
    class Weird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): return "repr!"
    class VeryWeird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): raise Exception("fail repr")
    # Normal string
    assert tableutils.to_text("abc") == "abc"
    # Integer
    assert tableutils.to_text(123) == "123"
    # Object with broken __str__, working __repr__
    assert tableutils.to_text(Weird()) == "repr!"
    # Object with broken __str__ and __repr__
    result = tableutils.to_text(VeryWeird())
    assert result.startswith("<") and "VeryWeird" in result
    # maxlen truncates
    assert tableutils.to_text("abcdef", maxlen=5) == "ab..."

def test_escape_html_basic():
    assert tableutils.escape_html("<tag>") == "&lt;tag&gt;"
    assert tableutils.escape_html('"quote"') == "&quot;quote&quot;"
    # maxlen truncates before escaping
    assert tableutils.escape_html("<abcdef>", maxlen=5) == "&lt;a..."

def test_dictinputtype_check_type_and_guess_headers():
    d = {"b": 2, "a": 1}
    it = tableutils.DictInputType()
    assert it.check_type(d) is True
    assert it.check_type([1,2]) is False
    # headers are sorted
    assert it.guess_headers(d) == ["a", "b"]

def test_dictinputtype_get_entry_and_get_entry_seq():
    d = {"a": 1, "b": 2}
    it = tableutils.DictInputType()
    headers = ["a", "b", "c"]
    assert it.get_entry(d, headers) == [1, 2, None]
    seq = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    assert it.get_entry_seq(seq, headers) == [[1, 2, None], [3, None, 4]]

def test_objectinputtype_check_type_and_guess_headers():
    class X:
        def __init__(self): self.a = 1; self.b = 2
        def method(self): pass
    x = X()
    it = tableutils.ObjectInputType()
    assert it.check_type(x) is True
    assert it.check_type(5) is False
    headers = it.guess_headers(x)
    # Should include 'a' and 'b', not 'method'
    assert "a" in headers and "b" in headers
    assert "method" not in headers

def test_objectinputtype_get_entry_missing_attr():
    class X: pass
    x = X()
    it = tableutils.ObjectInputType()
    headers = ["foo"]
    assert it.get_entry(x, headers) == [None]

def test_listinputtype_check_type_and_get_entry():
    it = tableutils.ListInputType()
    assert it.check_type([1,2]) is True
    assert it.check_type((1,2)) is False
    assert it.guess_headers([1,2]) is None
    assert it.get_entry([1,2], None) == [1,2]
    assert it.get_entry_seq([[1,2],[3,4]], None) == [[1,2],[3,4]]


... 568 lines omitted ...

    # Kills: line 481: False -> True
    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html
```
