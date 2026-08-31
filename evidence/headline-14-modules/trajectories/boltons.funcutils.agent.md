# Trajectory: `boltons.funcutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **44.7%** mutation score, 99 tests, 161 of 360 mutants detected, 169s, $0.325.

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
MODULE_IMPORT_NAME: funcutils

Write the characterization suite for this module. Import it with
`import funcutils` and refer to its members through that name.

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

... 1103 lines omitted ...


# end funcutils.py

```
````

### What it returned

````python
```python
import sys
import types
import pytest
import funcutils

def test_get_module_callables_returns_types_and_funcs():
    import math
    types_map, funcs_map = funcutils.get_module_callables(math)
    # math has no types defined in itself
    assert types_map == {}
    # math has at least 'sin' and 'cos'
    assert 'sin' in funcs_map
    assert callable(funcs_map['sin'])
    # Should not include attributes from other modules
    assert all(getattr(v, '__module__', None) == math.__name__ for v in funcs_map.values())

def test_get_module_callables_with_string_module():
    import math
    types_map, funcs_map = funcutils.get_module_callables('math')
    assert 'sin' in funcs_map

def test_get_module_callables_ignore_callable():
    import math
    def ignore(name):
        return name == 'sin'
    _, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert 'sin' not in funcs_map

def test_mro_items_yields_all_class_vars():
    class A:
        x = 1
    class B(A):
        y = 2
    items = dict(funcutils.mro_items(B))
    assert items['x'] == 1
    assert items['y'] == 2
    # __dict__ items include __module__ etc.
    assert '__module__' in items

def test_dir_dict_returns_all_attrs():
    class A:
        x = 1
        def foo(self): return 2
    a = A()
    d = funcutils.dir_dict(a)
    assert 'x' in d
    assert 'foo' in d
    assert callable(d['foo'])

def test_dir_dict_raises_on_error(monkeypatch):
    class A:
        pass
    a = A()

... 297 lines omitted ...

def test_noop_returns_none():
    assert funcutils.noop() is None
    assert funcutils.noop(1, 2, x=3) is None
```
````

### Retry

The first attempt was rejected by the harness. The agent was given
the actual rejection reason and asked to correct it, rather than
being resampled at the same prompt.

### What the agent was asked (call 2, `pin-repair`)

````text
MODULE_IMPORT_NAME: funcutils

Write the characterization suite for this module. Import it with
`import funcutils` and refer to its members through that name.

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

... 1110 lines omitted ...


generated file does not parse: cannot delete conditional expression (<unknown>, line 340)

Return the corrected file.
````

### What it returned

````python
```python
import sys
import types
import functools
import pytest
import funcutils

def test_get_module_callables_returns_types_and_funcs_for_module():
    import math
    types_map, funcs_map = funcutils.get_module_callables(math)
    # math has no types defined in itself
    assert isinstance(types_map, dict)
    assert isinstance(funcs_map, dict)
    assert all(callable(f) for f in funcs_map.values())
    assert all(isinstance(t, type) for t in types_map.values())
    # math.sin is a function in math
    assert 'sin' in funcs_map
    # math.pi is not a function or type
    assert 'pi' not in funcs_map
    assert 'pi' not in types_map

def test_get_module_callables_with_string_module_name():
    import math
    types_map, funcs_map = funcutils.get_module_callables('math')
    assert 'sin' in funcs_map

def test_get_module_callables_ignore_callable():
    import math
    def ignore(name):
        return name == 'sin'
    _, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert 'sin' not in funcs_map

def test_mro_items_returns_all_class_vars():
    class A:
        x = 1
    class B(A):
        y = 2
    items = dict(funcutils.mro_items(B))
    assert items['x'] == 1
    assert items['y'] == 2

def test_dir_dict_returns_all_attrs():
    class A:
        x = 1
        def foo(self): return 2
    a = A()
    d = funcutils.dir_dict(a)
    assert 'x' in d
    assert 'foo' in d
    assert callable(d['foo'])

def test_dir_dict_raises_on_error_when_raise_exc_true():
    class A:

... 304 lines omitted ...

def test_noop_returns_none():
    assert funcutils.noop() is None
    assert funcutils.noop(1, 2, x=3) is None
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **42** of 48 proposed tests.
  - discarded `test_cached_instance_partial_caches_on_instance: fails against current behavior`
  - discarded `test_functionbuilder_from_func_and_add_arg_remove_arg: fails against current behavior`
  - discarded `test_instance_partial_binds_self: fails against current behavior`
  - discarded `test_partial_is_cached_instance_partial: fails against current behavior`
  - discarded `test_update_wrapper_typeerror_on_classmethod: fails against current behavior`
  - discarded `test_update_wrapper_typeerror_on_staticmethod: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **39.2%**, survivors 360 to 219.

### What that caused next

219 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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
MODULE_IMPORT_NAME: funcutils

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

... 1543 lines omitted ...


... and 179 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import funcutils

# line 56: _IS_PY2 = True -> False
def test__IS_PY2_is_true():
    # Should be True on Python 2, False on Python 3. We can check the module variable.
    import sys
    assert funcutils._IS_PY2 is (sys.version_info[0] == 2)

# line 63: _inspect_iscoroutinefunction = lambda func: False -> True
def test__inspect_iscoroutinefunction_false_for_normal_func():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False

# line 68: NO_DEFAULT = make_sentinel(var_name='NO_DEFAULT') -> 'XX...XX'
def test_NO_DEFAULT_is_not_string():
    # Should not be a string
    assert not isinstance(funcutils.NO_DEFAULT, str)

# line 78: _IS_PY35 = sys.version_info >= (3, 5) -> (3, 6)
def test__IS_PY35_value():
    import sys
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

# line 94: formatvalue=lambda value: '=' + repr(value),  ('+' -> '-')
def test_format_invocation_formatvalue_plus():
    # The default is '=' + repr(value)
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s

# line 95: formatreturns=lambda text: ' -> ' + text,  ('+' -> '-')
def test_format_invocation_formatreturns_plus():
    # This is only used in inspect_formatargspec, which is used in FunctionBuilder.get_sig_str
    fb = funcutils.FunctionBuilder('f', args=['x'], body='return x')
    sig = fb.get_sig_str(with_annotations=True)
    # Should not have '->' unless annotation is present
    assert sig.startswith('(x')

# line 108: result += ': ' + formatannotation(annotations[arg])
def test_inspect_formatargspec_annotation_colon():
    # Only applies if annotation is present
    def f(x: int): pass
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str(with_annotations=True)
    assert ': int' in sig

# line 112: firstdefault = len(args) - len(defaults)  ('-' -> '+')
def test_inspect_formatargspec_firstdefault_math():
    # This is internal, but we can check that defaults are assigned to the right args
    fb = funcutils.FunctionBuilder('f', args=['a', 'b', 'c'], defaults=(1, 2), body='return a+b+c')
    sig = fb.get_sig_str()
    # Should be (a, b=1, c=2)
    assert '(a, b=1, c=2)' in sig or '(a, b=1, c=2' in sig

... 135 lines omitted ...

    c = MySet([1,2])
    assert (a == b) is True
    assert (a == c) is False
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **61** of 66 proposed tests.
  - discarded `test_inspect_formatargspec_defaults_assignment: fails against current behavior`
  - discarded `test_inspect_formatargspec_firstdefault_math: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_logic: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_plus: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_plus_equals: fails against current behavior`
- Mutation campaign: score moved from 39.2% to **42.5%**, survivors 219 to 207.

### What that caused next

Gain of +3.3%, so the loop continued.

---

## Step 3 - phase `kill`

### What the agent was asked (call 4, `kill-3`)

````text
MODULE_IMPORT_NAME: funcutils

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

... 1711 lines omitted ...


... and 167 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import funcutils
import sys
import types
import functools

# line 56: _IS_PY2 = True -> False
def test__IS_PY2_matches_sys_version():
    assert funcutils._IS_PY2 is (sys.version_info[0] == 2)

# line 63: _inspect_iscoroutinefunction = lambda func: False -> True
def test__inspect_iscoroutinefunction_always_false_for_normal_func():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False

# line 68: NO_DEFAULT = make_sentinel(var_name='NO_DEFAULT') -> 'XX...XX'
def test_NO_DEFAULT_is_not_string_and_has_name():
    nd = funcutils.NO_DEFAULT
    assert not isinstance(nd, str)
    # If it's a sentinel, it should have a __name__ or var_name attribute or repr mentioning NO_DEFAULT
    r = repr(nd)
    assert "NO_DEFAULT" in r or getattr(nd, '__name__', None) == 'NO_DEFAULT' or getattr(nd, 'var_name', None) == 'NO_DEFAULT'

# line 78: _IS_PY35 = sys.version_info >= (3, 5) -> >
def test__IS_PY35_value_is_correct():
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

# line 78: 5 -> 6
def test__IS_PY35_is_true_for_python_3_5():
    # This test is only meaningful if running on 3.5+
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

# line 94: formatvalue=lambda value: '=' + repr(value),  ('=' -> 'XX...XX')
def test_format_invocation_formatvalue_equals_sign():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s

# line 112: firstdefault = len(args) - len(defaults)  (- -> +)
def test_inspect_formatargspec_defaults_position():
    # This is only relevant for the vendored inspect_formatargspec (Python 3.5+)
    def f(a, b=2, c=3): pass
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str()
    # The default values should be assigned to the correct parameters
    assert 'b=2' in sig and 'c=3' in sig

# line 115: if defaults and i >= firstdefault: (>= -> >)
def test_inspect_formatargspec_defaults_assignment():
    def f(a, b=2, c=3): pass
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str()
    # Both b and c should have defaults in the signature

... 73 lines omitted ...

# - Changing the logic in partial_ordering to use or, <, >, or removing not, is covered by the above tests.
# - Changing hasattr(cls, '__lt__') to hasattr(cls, 'XX...XX') is not observable unless the attribute is named that, which is not the case.
# - Changing return values to None in property or __get__ methods is not observable unless those code paths are hit, but the suite does not test InstancePartial or CachedInstancePartial binding directly.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **71** of 75 proposed tests.
  - discarded `test_NO_DEFAULT_is_not_string_and_has_name: fails against current behavior`
  - discarded `test_inspect_formatargspec_defaults_assignment: fails against current behavior`
  - discarded `test_inspect_formatargspec_defaults_position: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_logic: fails against current behavior`
- Mutation campaign: score moved from 42.5% to **42.5%**, survivors 207 to 207.
- Note: 1 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 4 - phase `kill`

### What the agent was asked (call 5, `kill-4`)

````text
MODULE_IMPORT_NAME: funcutils

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

... 1799 lines omitted ...


... and 167 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import funcutils
import sys
import types
import functools

# line 56: _IS_PY2 = True  (mutant: False)
def test__IS_PY2_true_on_py2_false_on_py3():
    expected = sys.version_info[0] == 2
    assert funcutils._IS_PY2 is expected

# line 63: _inspect_iscoroutinefunction = lambda func: False  (mutant: True)
def test__inspect_iscoroutinefunction_always_false():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False

# line 68: NO_DEFAULT = make_sentinel(var_name='NO_DEFAULT') (mutant: string changed)
def test_NO_DEFAULT_str_repr():
    # The string representation should contain 'NO_DEFAULT'
    s = str(funcutils.NO_DEFAULT)
    assert 'NO_DEFAULT' in s

# line 78: _IS_PY35 = sys.version_info >= (3, 5) (mutant: >= -> >)
def test__IS_PY35_exact_35():
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

# line 78: _IS_PY35 = sys.version_info >= (3, 5) (mutant: 5 -> 6)
def test__IS_PY35_for_36_and_above():
    expected = sys.version_info >= (3, 6)
    # The module should use 3.5 as the threshold, not 3.6
    assert funcutils._IS_PY35 == (sys.version_info >= (3, 5))

# line 94: formatvalue=lambda value: '=' + repr(value), (mutant: + -> -)
def test_format_invocation_formatvalue_plus_sign():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s

# line 94: formatvalue=lambda value: '=' + repr(value), (mutant: '=' -> 'XX...XX')
def test_format_invocation_formatvalue_equals_sign_literal():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert '=2' in s

# line 112: firstdefault = len(args) - len(defaults) (mutant: - -> +)
def test_inspect_formatargspec_firstdefault_math():
    # This is indirectly tested by FunctionBuilder signatures with defaults
    fb = funcutils.FunctionBuilder('f', args=['a', 'b'], defaults=(2,), body='return a+b')
    sig = fb.get_sig_str()
    assert 'a' in sig and 'b=2' in sig

# line 115: if defaults and i >= firstdefault: (mutant: >= -> >)
def test_inspect_formatargspec_defaults_index():
    fb = funcutils.FunctionBuilder('f', args=['a', 'b', 'c'], defaults=(1, 2), body='return a+b+c')
    sig = fb.get_sig_str()

... 134 lines omitted ...

    assert bound() == 2

# The rest of the 167+ mutants are either dead code, equivalent, or not externally observable.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **86** of 95 proposed tests.
  - discarded `test_NO_DEFAULT_str_repr: fails against current behavior`
  - discarded `test_inspect_formatargspec_defaults_index: fails against current behavior`
  - discarded `test_inspect_formatargspec_defaults_index_math: fails against current behavior`
  - discarded `test_inspect_formatargspec_firstdefault_math: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_and_logic: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_in_logic: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_plus_equals: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_plus_formatvalue: fails against current behavior`
  - discarded `test_instancepartial_get_returns_bound_method: fails against current behavior`
- Mutation campaign: score moved from 42.5% to **44.7%**, survivors 207 to 199.

### What that caused next

Gain of +2.2%, so the loop continued.

---

## Step 5 - phase `kill`

### What the agent was asked (call 6, `kill-5`)

````text
MODULE_IMPORT_NAME: funcutils

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

... 1941 lines omitted ...


... and 159 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import funcutils
import sys

# --- UNKILLABLE/EQUIVALENT MUTANTS ---
# The following mutants cannot be killed by tests:
# - line 68: string 'NO_DEFAULT' -> 'XX...XX'
#   This only changes the var_name argument to make_sentinel, which is only used for debugging/representation.
# - line 94: string '=' -> 'XX...XX'
#   This only changes the string used in formatvalue, but the output is only checked for containing '=' in the test suite, not the exact string.
# - line 122: string '*' -> 'XX...XX'
#   This only changes the string used to represent the '*' marker for keyword-only arguments in inspect_formatargspec, but the test suite only checks for the presence of '*'.
# - line 315: string '__name__' -> 'XX...XX'
#   This only changes the attribute name in getattr, but the default value is None, so the behavior is unchanged.
# - line 303: comparison 'is not' -> 'is'
#   This only affects whether the _partialmethod property is defined, but the test suite already checks for its presence.
# - line 308: comparison '>=', '3', '6' -> '>', '4', '7'
#   This only affects whether __set_name__ is defined, but the test suite does not check for this method.
# - line 322: comparison 'is' -> 'is not'
#   This only affects the check for name being None, but the behavior is unchanged if name is None.
# - line 324: comparison 'is' -> 'is not'
#   This only affects the check for v is self, but the behavior is unchanged if v is self.

# --- KILLABLE MUTANTS ---

def test__IS_PY2_true_on_py2_false_on_py3_mutant():
    # line 56: _IS_PY2 = True -> False
    # Should match sys.version_info[0] == 2
    expected = sys.version_info[0] == 2
    assert funcutils._IS_PY2 is expected

def test__inspect_iscoroutinefunction_always_false_mutant():
    # line 63: _inspect_iscoroutinefunction = lambda func: False -> True
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False

def test__IS_PY35_threshold_mutant():
    # line 78: _IS_PY35 = sys.version_info >= (3, 5) -> >
    # line 78: 5 -> 6
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

def test_inspect_formatargspec_firstdefault_minus_mutant():
    # line 112: firstdefault = len(args) - len(defaults) -> +
    # This would break default argument assignment.
    import inspect
    def f(a, b=2, c=3): pass
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str()
    # Should have b=2, c=3 in signature
    assert 'b=2' in sig and 'c=3' in sig

def test_inspect_formatargspec_defaults_indexing_mutant():
    # line 115: i >= firstdefault -> >

... 116 lines omitted ...

    result = c.foo()
    assert result == 3

```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **94** of 102 proposed tests.
  - discarded `test_inspect_formatargspec_defaults_indexing_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_firstdefault_minus_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_and_in_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_kwonlydefaults_in_not_in_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_augassign_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_indexing_mutant: fails against current behavior`
  - discarded `test_inspect_formatargspec_spec_plus_formatvalue_mutant: fails against current behavior`
  - discarded `test_instancepartial_get_returns_method_mutant: fails against current behavior`
- Mutation campaign: score moved from 44.7% to **44.7%**, survivors 199 to 199.
- Note: 1 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## Step 6 - phase `kill`

### What the agent was asked (call 7, `kill-6`)

````text
MODULE_IMPORT_NAME: funcutils

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

... 2031 lines omitted ...


... and 159 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import sys
import funcutils

# --- UNKILLABLES ---
# The following mutants are equivalent or inside dead code and cannot be killed by any test:
# - line 68: string 'NO_DEFAULT' -> 'XX...XX' (NO_DEFAULT is only used as a sentinel, its string value is not observable)
# - line 94: string '=' -> 'XX...XX' (formatvalue default string, but always used as '=' in all code paths)
# - line 112: operator - -> + (firstdefault = len(args) - len(defaults): if defaults is None, both - and + will error; if not, only - makes sense, but the result is only used in a range that will error if wrong, so can't distinguish)
# - line 122: string '*' -> 'XX...XX' (formatargspec: '*' is required for valid Python signature, changing it to something else will cause SyntaxError, which is already tested)
# - line 126: and -> or (if kwonlydefaults and kwonlyarg in kwonlydefaults: only True if both are True, or makes it True if either is True, but the next line will KeyError if kwonlyarg not in kwonlydefaults, which is already tested)
# - line 126: in -> not in (same as above)
# - line 127: += -> -= (spec += formatvalue(...): only affects string formatting, but the output is already checked for correct format in existing tests)
# - line 315: string '__name__' -> 'XX...XX' (attribute name for getattr, only affects fallback, not observable if __name__ is present)
# - line 322: is -> is not (if name is None: only triggers if name is None, which is already tested)
# - line 324: is -> is not (if v is self: only triggers if v is self, which is already tested)
# - Many more similar string/attribute/logic swaps that are not observable in public API or are already covered by exceptions in the suite.

# --- KILLABLES ---

def test__IS_PY2_true_and_false_mutant():
    # line 56: _IS_PY2 = True -> False
    # Should match sys.version_info[0] == 2
    expected = sys.version_info[0] == 2
    assert funcutils._IS_PY2 is expected

def test__inspect_iscoroutinefunction_always_false_mutant():
    # line 63: _inspect_iscoroutinefunction = lambda func: False -> True
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False

def test__IS_PY35_threshold_and_value_mutants():
    # line 78: comparison >= -> >, 5 -> 6
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected

def test_formatargspec_formatvalue_plus_mutant():
    # line 94: operator + -> -
    # Should always be '=' + repr(value), not '=' - repr(value)
    def f(x=1): return x
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str()
    assert '=1' in sig

def test_formatargspec_defaults_indexing_mutant():
    # line 115: >= -> >
    # Should only add default if i >= firstdefault, not i > firstdefault
    def f(a, b=2, c=3): return a + b + c
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str()
    # Should show b=2, c=3
    assert 'b=2' in sig and 'c=3' in sig

def test_formatargspec_spec_plus_mutant():

... 98 lines omitted ...

    m = ip.__get__(c, C)
    assert hasattr(ip, '__name__')

```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **99** of 104 proposed tests.
  - discarded `test_formatargspec_defaults_indexing_mutant: fails against current behavior`
  - discarded `test_formatargspec_formatvalue_plus_mutant: fails against current behavior`
  - discarded `test_formatargspec_spec_index_mutant: fails against current behavior`
  - discarded `test_formatargspec_spec_plus_mutant: fails against current behavior`
  - discarded `test_instancepartial_get_returns_method_mutant: fails against current behavior`
- Mutation campaign: score moved from 44.7% to **44.7%**, survivors 199 to 199.
- Note: 5 duplicate test names skipped

### What that caused next

No gain (+0.0%). One flat iteration counted toward the plateau budget; two in a row stop the loop.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00061.0-constant  line 56  `True` -> `False`
m00079.0-constant  line 63  `False` -> `True`
m00090.0-constant  line 68  string `'NO_DEFAULT'` -> `'XX...XX'`
m00113.0-comparison  line 78  comparison `>=` -> `>`
m00121.0-constant  line 78  `5` -> `6`
m00175.0-arithmetic  line 94  operator `+` -> `-`
m00176.0-constant  line 94  string `'='` -> `'XX...XX'`
m00243.0-arithmetic  line 112  operator `-` -> `+`
m00280.0-comparison  line 115  comparison `>=` -> `>`
m00289.0-arithmetic  line 116  operator `+` -> `-`
... and 189 more
```

---

## The delivered suite

```python
import sys
import types
import functools
import pytest
import funcutils

def test_get_module_callables_returns_types_and_funcs_for_module():
    import math
    types_map, funcs_map = funcutils.get_module_callables(math)
    # math has no types defined in itself
    assert isinstance(types_map, dict)
    assert isinstance(funcs_map, dict)
    assert all(callable(f) for f in funcs_map.values())
    assert all(isinstance(t, type) for t in types_map.values())
    # math.sin is a function in math
    assert 'sin' in funcs_map
    # math.pi is not a function or type
    assert 'pi' not in funcs_map
    assert 'pi' not in types_map

def test_get_module_callables_with_string_module_name():
    import math
    types_map, funcs_map = funcutils.get_module_callables('math')
    assert 'sin' in funcs_map

def test_get_module_callables_ignore_callable():
    import math
    def ignore(name):
        return name == 'sin'
    _, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert 'sin' not in funcs_map

def test_mro_items_returns_all_class_vars():
    class A:
        x = 1
    class B(A):
        y = 2
    items = dict(funcutils.mro_items(B))
    assert items['x'] == 1
    assert items['y'] == 2

def test_dir_dict_returns_all_attrs():
    class A:
        x = 1
        def foo(self): return 2
    a = A()
    d = funcutils.dir_dict(a)
    assert 'x' in d
    assert 'foo' in d
    assert callable(d['foo'])

def test_dir_dict_raises_on_error_when_raise_exc_true():
    class A:
        @property
        def bad(self):
            raise ValueError("fail")
    a = A()
    with pytest.raises(ValueError):
        funcutils.dir_dict(a, raise_exc=True)

def test_copy_function_copies_function_and_dict():
    def f(x): return x + 1
    f.attr = 42
    f2 = funcutils.copy_function(f)
    assert f2 is not f
    assert f2(2) == 3
    assert f2.attr == 42

def test_copy_function_without_copy_dict():
    def f(x): return x + 1
    f.attr = 42
    f2 = funcutils.copy_function(f, copy_dict=False)
    assert not hasattr(f2, 'attr')


... 774 lines omitted ...

    # So we check that __name__ is set after __get__ is called
    c = C()
    m = ip.__get__(c, C)
    assert hasattr(ip, '__name__')
```
