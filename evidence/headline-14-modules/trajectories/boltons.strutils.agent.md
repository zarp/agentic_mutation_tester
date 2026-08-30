# Trajectory: `boltons.strutils`, agent arm

Run `20260830-055632-headline` | model `gpt-4.1-2025-04-14` at temperature 0.0 | Python 3.12.3 | revision `b193251-dirty`

Final: **54.0%** mutation score, 63 tests, 216 of 400 mutants detected, 148s, $0.353.

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
MODULE_IMPORT_NAME: strutils

Write the characterization suite for this module. Import it with
`import strutils` and refer to its members through that name.

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

... 1281 lines omitted ...

        return all_grafs
    return ending.join(all_grafs)

```
````

### What it returned

````python
```python
import pytest
import strutils
import sys
import uuid
import re
import string

def test_camel2under_basic():
    assert strutils.camel2under('BasicParseTest') == 'basic_parse_test'
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('A') == 'a'
    assert strutils.camel2under('') == ''

def test_camel2under_boundaries():
    assert strutils.camel2under('A1B2C3') == 'a1_b2_c3'
    assert strutils.camel2under('aB') == 'a_b'
    assert strutils.camel2under('AB') == 'ab'

def test_under2camel_basic():
    assert strutils.under2camel('complex_tokenizer') == 'ComplexTokenizer'
    assert strutils.under2camel('foo_bar_baz') == 'FooBarBaz'
    assert strutils.under2camel('foo') == 'Foo'
    assert strutils.under2camel('') == ''
    assert strutils.under2camel('_foo_') == '_Foo_'

def test_under2camel_boundaries():
    assert strutils.under2camel('a_b_c') == 'ABC'
    assert strutils.under2camel('a__b') == 'A_B'

def test_slugify_basic():
    assert strutils.slugify('First post! Hi!!!!~1    ') == 'first_post_hi_1'
    assert strutils.slugify('First post! Hi!!!!~1    ', delim='-') == 'first-post-hi-1'
    assert strutils.slugify('First post! Hi!!!!~1    ', lower=False) == 'First_Post_Hi_1'
    assert strutils.slugify('', delim='-') == ''
    assert strutils.slugify('   ', delim='-') == '-'

def test_slugify_ascii():
    result = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    assert isinstance(result, bytes)
    assert result == b'kurt_goedel_s_pretty_cool'

def test_split_punct_ws():
    assert strutils.split_punct_ws('First post! Hi!!!!~1    ') == ['First', 'post', 'Hi', '1']
    assert strutils.split_punct_ws('') == []
    assert strutils.split_punct_ws('!@#$%^&*()') == []
    assert strutils.split_punct_ws('a,b.c;d:e') == ['a', 'b', 'c', 'd', 'e']

def test_unit_len_basic():
    assert strutils.unit_len(range(10), 'number') == '10 numbers'
    assert strutils.unit_len('aeiou', 'vowel') == '5 vowels'
    assert strutils.unit_len([], 'worry') == 'No worries'

... 223 lines omitted ...


def test_MultiReplace_dict_and_list():
    # dict input
    m = strutils.MultiReplace({'foo': 'zoo
````

### Retry

The first attempt was rejected by the harness. The agent was given
the actual rejection reason and asked to correct it, rather than
being resampled at the same prompt.

### What the agent was asked (call 2, `pin-repair`)

````text
MODULE_IMPORT_NAME: strutils

Write the characterization suite for this module. Import it with
`import strutils` and refer to its members through that name.

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

... 1288 lines omitted ...


generated file does not parse: unterminated string literal (detected at line 281) (<unknown>, line 281)

Return the corrected file.
````

### What it returned

````python
```python
import strutils
import pytest
import sys
import uuid

def test_camel2under_basic():
    assert strutils.camel2under('BasicParseTest') == 'basic_parse_test'
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('A') == 'a'
    assert strutils.camel2under('') == ''

def test_under2camel_basic():
    assert strutils.under2camel('complex_tokenizer') == 'ComplexTokenizer'
    assert strutils.under2camel('foo_bar_baz') == 'FooBarBaz'
    assert strutils.under2camel('foo') == 'Foo'
    assert strutils.under2camel('') == ''
    assert strutils.under2camel('_foo') == '_Foo'
    assert strutils.under2camel('foo_') == 'Foo_'
    assert strutils.under2camel('__foo__') == '__Foo__'

def test_slugify_basic_and_ascii():
    assert strutils.slugify('First post! Hi!!!!~1    ') == 'first_post_hi_1'
    result = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    assert result == b'kurt_goedel_s_pretty_cool'
    assert strutils.slugify('', delim='-', lower=False) == ''
    assert strutils.slugify('A B', delim='-', lower=False) == 'A-B'
    assert strutils.slugify('A B', delim='-', lower=True) == 'a-b'

def test_split_punct_ws_various():
    assert strutils.split_punct_ws('First post! Hi!!!!~1    ') == ['First', 'post', 'Hi', '1']
    assert strutils.split_punct_ws('') == []
    assert strutils.split_punct_ws('abc') == ['abc']
    assert strutils.split_punct_ws('a,b.c!d') == ['a', 'b', 'c', 'd']

def test_unit_len_plural_and_zero():
    assert strutils.unit_len(range(10), 'number') == '10 numbers'
    assert strutils.unit_len('aeiou', 'vowel') == '5 vowels'
    assert strutils.unit_len([], 'worry') == 'No worries'
    assert strutils.unit_len([1], 'item') == '1 item'

def test_ordinalize_various():
    assert strutils.ordinalize(1) == '1st'
    assert strutils.ordinalize(2) == '2nd'
    assert strutils.ordinalize(3) == '3rd'
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(21) == '21st'
    assert strutils.ordinalize(22) == '22nd'
    assert strutils.ordinalize(23) == '23rd'

... 225 lines omitted ...

    assert strutils.unwrap_text('a\nb\nc') == 'a b c'
    # empty string
    assert strutils.unwrap_text('') == ''
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **22** of 27 proposed tests.
  - discarded `test_asciify_basic_and_ignore: fails against current behavior`
  - discarded `test_bytes2human_various: fails against current behavior`
  - discarded `test_indent_basic_and_key: fails against current behavior`
  - discarded `test_pluralize_and_singularize_regular_and_irregular: fails against current behavior`
  - discarded `test_under2camel_basic: fails against current behavior`
- Mutation campaign: score moved from 0.0% to **34.5%**, survivors 400 to 262.

### What that caused next

262 mutants went undetected. That list, not a request for more tests, becomes the next prompt.

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

### What the agent was asked (call 3, `kill-2`)

````text
MODULE_IMPORT_NAME: strutils

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

... 1648 lines omitted ...


... and 222 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import strutils

# The following mutants are all changes to string literals in __all__.
# Changing the names in __all__ does not affect any runtime behavior unless
# someone does `from strutils import *`, which is not done in the test suite.
# There is no way to distinguish these changes with a test that does not
# rely on import * or introspection of __all__, which is not required by the
# current suite. Therefore, these mutants are equivalent and cannot be killed
# by a test under the current constraints.

# The following mutant changes '' to 'XX...XX' in under2camel:
# This only affects the output for input strings with empty segments, e.g. leading/trailing/multiple underscores.
def test_under2camel_empty_segment():
    # 'foo__bar' -> ['foo', '', 'bar'] -> ['Foo', '', 'Bar'] -> 'FooBar'
    assert strutils.under2camel('foo__bar') == 'FooBar'
    # '_foo' -> ['', 'foo'] -> ['_', 'Foo'] -> '_Foo'
    assert strutils.under2camel('_foo') == '_Foo'
    # 'foo_' -> ['foo', ''] -> ['Foo', '_'] -> 'Foo_'
    assert strutils.under2camel('foo_') == 'Foo_'
    # '' -> [''] -> ['_'] -> '_'
    assert strutils.under2camel('') == '_'

# The following mutant changes `or` to `and` in under2camel:
# This would cause only non-empty segments to be capitalized, empty segments would always yield '_'.
def test_under2camel_and_vs_or():
    # The correct behavior is that empty segments yield '_'
    assert strutils.under2camel('foo__bar') == 'FooBar'
    assert strutils.under2camel('_foo') == '_Foo'
    assert strutils.under2camel('foo_') == 'Foo_'
    assert strutils.under2camel('') == '_'

# The following mutant changes '_' to 'XX...XX' in under2camel:
# This would affect the output for empty segments as above.
def test_under2camel_empty_segment_literal():
    # The correct output is '_', not 'XX...XX'
    assert strutils.under2camel('foo__bar') == 'FooBar'
    assert strutils.under2camel('_foo') == '_Foo'
    assert strutils.under2camel('foo_') == 'Foo_'
    assert strutils.under2camel('') == '_'

# The following mutant changes the default 'th' to 'XX...XX' in ordinalize:
def test_ordinalize_default_th():
    # 4th, 11th, 12th, 13th, 1515th
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(1515) == '1515th'

# The following mutants are in singularize:
# - removed `not` in `if not word or word in _IRR_S2P:`
# - return value replaced with None
# - removed `not` in `elif not word.endswith('s'):`

... 58 lines omitted ...

# The following mutants in bytes2human, MultiReplace, etc., are not shown here.
# If any of those are string literal changes or dead code, they are equivalent.

```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **24** of 28 proposed tests.
  - discarded `test_singularize_irregular_and_non_plural: fails against current behavior`
  - discarded `test_under2camel_and_vs_or: fails against current behavior`
  - discarded `test_under2camel_empty_segment: fails against current behavior`
  - discarded `test_under2camel_empty_segment_literal: fails against current behavior`
- Mutation campaign: score moved from 34.5% to **35.8%**, survivors 262 to 257.

### What that caused next

Gain of +1.3%, so the loop continued.

---

## Step 3 — phase `kill`

### What the agent was asked (call 4, `kill-3`)

````text
MODULE_IMPORT_NAME: strutils

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

... 1685 lines omitted ...


... and 217 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import strutils

# The following mutants are all changes to the __all__ list, which only affects
# what is exported via "from strutils import *". The test suite does not use
# star imports, and the module's runtime behavior is otherwise unaffected.
# These mutants are equivalent and cannot be killed by any test:
#
# line 75: string 'camel2under' -> 'XX...XX'
# line 75: string 'under2camel' -> 'XX...XX'
# line 75: string 'split_punct_ws' -> 'XX...XX'
# line 76: string 'ordinalize' -> 'XX...XX'
# line 76: string 'cardinalize' -> 'XX...XX'
# line 76: string 'singularize' -> 'XX...XX'
# line 77: string 'is_ascii' -> 'XX...XX'
# line 77: string 'html2text' -> 'XX...XX'
# line 77: string 'strip_ansi' -> 'XX...XX'
# line 78: string 'find_hashtags' -> 'XX...XX'
# line 78: string 'gzip_bytes' -> 'XX...XX'
# line 79: string 'iter_splitlines' -> 'XX...XX'
# line 79: string 'indent' -> 'XX...XX'
# line 80: string 'args2cmd' -> 'XX...XX'
# line 80: string 'parse_int_list' -> 'XX...XX'
# line 81: string 'int_list_complement' -> 'XX...XX'
# line 81: string 'int_list_to_int_tupl...' -> 'XX...XX'
# line 82: string 'multi_replace' -> 'XX...XX'

def test_under2camel_empty_string_and_leading_underscore():
    # line 107: string '' -> 'XX...XX'
    # line 107: or -> and
    # line 107: string '_' -> 'XX...XX'
    # The original: ''.join(w.capitalize() or '_' for w in under_string.split('_'))
    # Mutant: ''.join(w.capitalize() and 'XX...XX' for ...)
    # Input: empty string and string with leading underscore
    assert strutils.under2camel('') == ''
    assert strutils.under2camel('_foo') == '_Foo'
    assert strutils.under2camel('foo_bar') == 'FooBar'
    assert strutils.under2camel('foo__bar') == 'Foo_Bar'

def test_singularize_empty_and_irregular_and_short():
    # line 237: removed not
    # line 238: return value replaced with None
    # line 243: removed not
    # line 244: return value replaced with None
    # line 245: 2 -> 3
    # line 247: and -> or
    # line 247: string 'ies' -> 'XX...XX'
    # line 247: 4 -> 5
    # line 247: string 'aeiou' -> 'XX...XX'
    # line 248: 3 -> 4
    # line 248: string 'y' -> 'XX...XX'
    # line 249: string 'es' -> 'XX...XX'
    # line 249: 3 -> 4
    # line 250: 2 -> 3

... 37 lines omitted ...

    assert strutils.pluralize('sheep') == 'sheep'
    # Test regular
    assert strutils.pluralize('dog') == 'dogs'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **25** of 27 proposed tests.
  - discarded `test_singularize_empty_and_irregular_and_short: fails against current behavior`
  - discarded `test_under2camel_empty_string_and_leading_underscore: fails against current behavior`
- Mutation campaign: score moved from 35.8% to **36.0%**, survivors 257 to 256.

### What that caused next

Gain of +0.3%, so the loop continued.

---

## Step 4 — phase `kill`

### What the agent was asked (call 5, `kill-4`)

````text
MODULE_IMPORT_NAME: strutils

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

... 1713 lines omitted ...


... and 216 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import strutils

# The following mutants are changes to __all__ (lines 75-82), which only affect
# what is exported via "from strutils import *". The test suite does not use
# star imports, and the module's runtime behavior is otherwise unaffected.
# These mutants are equivalent and cannot be killed by tests.

# The following mutants are changes to the logic or return values of under2camel.
# We can kill them by checking behavior for empty string and for underscores.

def test_under2camel_empty_string():
    # line 107: '' -> 'XX...XX'
    # line 107: or -> and
    # line 107: '_' -> 'XX...XX'
    assert strutils.under2camel('') == ''

def test_under2camel_leading_trailing_underscore():
    # Should produce '_' for empty segments
    assert strutils.under2camel('_foo') == '_Foo'
    assert strutils.under2camel('foo_') == 'Foo_'
    assert strutils.under2camel('_foo_') == '_Foo_'
    assert strutils.under2camel('__') == '__'

def test_under2camel_multiple_underscores():
    # Should produce '_' for each empty segment
    assert strutils.under2camel('foo__bar') == 'Foo_Bar'

# Mutants in singularize (lines 237-252): logic changes and return value changes.
# We'll test cases that exercise the various branches.

def test_singularize_empty_and_irregular():
    # line 237: removed not
    # line 238: return value replaced with None
    assert strutils.singularize('') == ''
    assert strutils.singularize('feet') == 'foot'

def test_singularize_non_plural():
    # line 243: removed not
    # line 244: return value replaced with None
    assert strutils.singularize('dog') == 'dog'

def test_singularize_two_letter_word():
    # line 245: 2 -> 3
    assert strutils.singularize('as') == 'a'

def test_singularize_ies_rule():
    # line 247: or/and, 'ies'->'XX...XX', 4->5, 'aeiou'->'XX...XX'
    # line 248: 3->4, 'y'->'XX...XX'
    assert strutils.singularize('parties') == 'party'
    # test with a word where -ies is preceded by a vowel (should not apply rule)
    assert strutils.singularize('movies') == 'movie'

def test_singularize_es_rule():

... 37 lines omitted ...

    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(1515) == '1515th'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **36** of 40 proposed tests.
  - discarded `test_singularize_es_rule: fails against current behavior`
  - discarded `test_singularize_ies_rule: fails against current behavior`
  - discarded `test_under2camel_empty_string: fails against current behavior`
  - discarded `test_under2camel_leading_trailing_underscore: fails against current behavior`
- Mutation campaign: score moved from 36.0% to **38.2%**, survivors 256 to 247.

### What that caused next

Gain of +2.3%, so the loop continued.

---

## Step 5 — phase `kill`

### What the agent was asked (call 6, `kill-5`)

````text
MODULE_IMPORT_NAME: strutils

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

... 1784 lines omitted ...


... and 207 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import strutils

# The following mutants are changes to __all__ and do not affect runtime behavior,
# so cannot be detected by any test that does not inspect __all__ directly.
# These are equivalent mutants for the purposes of this suite.

def test___all___contains_expected_names():
    # These names must be present in __all__ as per the original module.
    expected = [
        'camel2under', 'under2camel', 'slugify', 'split_punct_ws',
        'unit_len', 'ordinalize', 'cardinalize', 'pluralize', 'singularize',
        'asciify', 'is_ascii', 'is_uuid', 'html2text', 'strip_ansi',
        'bytes2human', 'find_hashtags', 'a10n', 'gzip_bytes', 'gunzip_bytes',
        'iter_splitlines', 'indent', 'escape_shell_args',
        'args2cmd', 'args2sh', 'parse_int_list', 'format_int_list',
        'int_list_complement', 'int_list_to_int_tuples', 'MultiReplace',
        'multi_replace', 'unwrap_text'
    ]
    for name in expected:
        assert name in strutils.__all__

# line 197: string 'th' -> 'XX...XX'
def test_ordinalize_default_suffix_is_th():
    # For a number ending in 0, 4, 5, 6, 7, 8, 9, should get 'th'
    for n in [0, 4, 5, 6, 7, 8, 9, 10, 14, 111, 112, 113]:
        result = strutils.ordinalize(n)
        assert result.endswith('th'), f"ordinalize({n}) = {result}"

# line 245: 2 -> 3
def test_singularize_two_letter_word_as():
    # 'as' is two letters, should become 'a'
    assert strutils.singularize('as') == 'a'

# line 247: string 'ies' -> 'XX...XX'
# line 247: 4 -> 5
# line 247: string 'aeiou' -> 'XX...XX'
# line 248: 3 -> 4
# line 248: string 'y' -> 'XX...XX'
def test_singularize_ies_rule_and_vowel_check():
    # 'parties' -> 'party' (consonant before 'ies')
    assert strutils.singularize('parties') == 'party'
    # 'boyies' (not a real word, but vowel before 'ies') -> 'boyies' (should not singularize)
    assert strutils.singularize('boyies') == 'boyies'
    # 'flies' -> 'fly'
    assert strutils.singularize('flies') == 'fly'
    # 'babies' -> 'baby'
    assert strutils.singularize('babies') == 'baby'

# line 249: string 'es' -> 'XX...XX'
# line 249: 3 -> 4
# line 250: 2 -> 3
def test_singularize_es_rule():
    # 'buses' -> 'bus'

... 106 lines omitted ...

    assert strutils.slugify('', delim='-', lower=False) == ''
    assert strutils.slugify('A B', delim='-', lower=False) == 'A-B'
    assert strutils.slugify('A B', delim='-', lower=True) == 'a-b'
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **50** of 52 proposed tests.
  - discarded `test_singularize_ies_rule_and_vowel_check: fails against current behavior`
  - discarded `test_under2camel_multiple_underscores_new: fails against current behavior`
- Mutation campaign: score moved from 38.2% to **46.0%**, survivors 247 to 216.
- Note: 1 duplicate test names skipped

### What that caused next

Gain of +7.8%, so the loop continued.

---

## Step 6 — phase `kill`

### What the agent was asked (call 7, `kill-6`)

````text
MODULE_IMPORT_NAME: strutils

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

... 1910 lines omitted ...


... and 176 more survivors not shown.

Write new tests that catch as many of these as you can.
````

### What it returned

````python
```python
import strutils

def test_ordinalize_default_suffix_th_vs_xx():
    # line 197: string 'th' -> 'XX...XX'
    # For a number ending in 0, 4, 5, 6, 7, 8, 9, should get 'th'
    for n in [0, 4, 5, 6, 7, 8, 9, 10, 14, 111, 112, 113]:
        result = strutils.ordinalize(n)
        assert result.endswith('th'), f"ordinalize({n}) = {result}"

def test_singularize_two_letter_word_len2():
    # line 245: 2 -> 3
    # 'as' is two letters, should become 'a'
    assert strutils.singularize('as') == 'a'

def test_singularize_ies_rule_and_aeiou_check():
    # line 247: string 'ies' -> 'XX...XX'
    # line 247: 4 -> 5
    # line 247: string 'aeiou' -> 'XX...XX'
    # line 248: 3 -> 4
    # line 248: string 'y' -> 'XX...XX'
    # 'parties' -> 'party' (consonant before 'ies')
    assert strutils.singularize('parties') == 'party'
    # 'flies' -> 'fly' (consonant before 'ies')
    assert strutils.singularize('flies') == 'fly'
    # 'boys' -> 'boy' (should not match 'ies' rule)
    assert strutils.singularize('boys') == 'boy'

def test_pluralize_y_rule_aeiou_check():
    # line 273: string 'aeiou' -> 'XX...XX'
    # consonant before 'y'
    assert strutils.pluralize('party') == 'parties'
    # vowel before 'y'
    assert strutils.pluralize('boy') == 'boys'
    # consonant before 'y'
    assert strutils.pluralize('fly') == 'flies'
    # vowel before 'y'
    assert strutils.pluralize('key') == 'keys'

def test_pluralize_es_rule():
    # line 276: string 'es' -> 'XX...XX'
    # 'bus' -> 'buses'
    assert strutils.pluralize('bus') == 'buses'
    # 'match' -> 'matches'
    assert strutils.pluralize('match') == 'matches'
    # 'dish' -> 'dishes'
    assert strutils.pluralize('dish') == 'dishes'

def test__match_case_lower_returns_disciple():
    # line 284: return value replaced with None
    # master is lower, disciple is returned lower
    assert strutils._match_case('dog', 'cat') == 'cat'

def test__match_case_upper_returns_disciple_upper():

... 95 lines omitted ...

    assert strutils.singularize('errata') == 'erratum'

# Many more irregulars exist, but the above pattern suffices for the shown mutants.
```
````

### What the harness did with it

- Suite ran and passed against the unmodified module.
- Quality filters: kept **63** of 63 proposed tests.
- Mutation campaign: score moved from 46.0% to **54.0%**, survivors 216 to 184.
- Note: 3 duplicate test names skipped

### What that caused next

Gain of +8.0%, so the loop continued.

---

## What the finished suite still cannot detect

These are reported to the user at the top of the generated file. Some are
equivalent mutants that no test can catch; the rest are real gaps.

```text
m00432.0-constant  line 197  string `'th'` -> `'XX...XX'`
m00564.0-constant  line 245  `2` -> `3`
m00592.0-constant  line 247  `4` -> `5`
m00598.0-constant  line 247  string `'aeiou'` -> `'XX...XX'`
m00742.0-constant  line 273  string `'aeiou'` -> `'XX...XX'`
m00791.0-constant  line 276  string `'es'` -> `'XX...XX'`
m00827.0-return  line 284  return value replaced with `None`
m00878.0-return  line 291  return value replaced with `None`
m00919.0-constant  line 306  string `'fish'` -> `'XX...XX'`
m01024.0-constant  line 306  string `'fish'` -> `'XX...XX'`
... and 174 more
```

---

## The delivered suite

```python
import strutils
import pytest
import sys
import uuid

def test_camel2under_basic():
    assert strutils.camel2under('BasicParseTest') == 'basic_parse_test'
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('A') == 'a'
    assert strutils.camel2under('') == ''


def test_slugify_basic_and_ascii():
    assert strutils.slugify('First post! Hi!!!!~1    ') == 'first_post_hi_1'
    result = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    assert result == b'kurt_goedel_s_pretty_cool'
    assert strutils.slugify('', delim='-', lower=False) == ''
    assert strutils.slugify('A B', delim='-', lower=False) == 'A-B'
    assert strutils.slugify('A B', delim='-', lower=True) == 'a-b'

def test_split_punct_ws_various():
    assert strutils.split_punct_ws('First post! Hi!!!!~1    ') == ['First', 'post', 'Hi', '1']
    assert strutils.split_punct_ws('') == []
    assert strutils.split_punct_ws('abc') == ['abc']
    assert strutils.split_punct_ws('a,b.c!d') == ['a', 'b', 'c', 'd']

def test_unit_len_plural_and_zero():
    assert strutils.unit_len(range(10), 'number') == '10 numbers'
    assert strutils.unit_len('aeiou', 'vowel') == '5 vowels'
    assert strutils.unit_len([], 'worry') == 'No worries'
    assert strutils.unit_len([1], 'item') == '1 item'

def test_ordinalize_various():
    assert strutils.ordinalize(1) == '1st'
    assert strutils.ordinalize(2) == '2nd'
    assert strutils.ordinalize(3) == '3rd'
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(21) == '21st'
    assert strutils.ordinalize(22) == '22nd'
    assert strutils.ordinalize(23) == '23rd'
    assert strutils.ordinalize(101) == '101st'
    assert strutils.ordinalize('hi') == 'hi'
    assert strutils.ordinalize(1515) == '1515th'
    assert strutils.ordinalize(1, ext_only=True) == 'st'
    assert strutils.ordinalize(2, ext_only=True) == 'nd'
    assert strutils.ordinalize(11, ext_only=True) == 'th'
    assert strutils.ordinalize('', ext_only=True) == ''

def test_cardinalize_plural_and_singular():
    assert strutils.cardinalize('vowel', 5) == 'vowels'
    assert strutils.cardinalize('Wish', 3) == 'Wishes'
    assert strutils.cardinalize('item', 1) == 'item'
    assert strutils.cardinalize('item', 0) == 'items'


def test_find_hashtags_ascii_and_unicode():
    assert strutils.find_hashtags('#atag http://asite/#ananchor') == ['atag']
    assert strutils.find_hashtags('no hashtags here') == []
    assert strutils.find_hashtags('foo #bar #baz') == ['bar', 'baz']
    assert strutils.find_hashtags('foo ＃bar') == ['bar']
    # Unicode hashtag
    s = "can't get enough of that dignity chicken #肯德基 woo"
    tags = strutils.find_hashtags(s)
    assert any('\u80af' in tag or '\u57fa' in tag for tag in tags) or tags == ['肯德基']

def test_a10n_numeronym():
    assert strutils.a10n('abbreviation') == 'a10n'
    assert strutils.a10n('internationalization') == 'i18n'
    assert strutils.a10n('') == ''

... 559 lines omitted ...

    assert strutils.pluralize('embargo') == 'embargoes'
    assert strutils.singularize('embargoes') == 'embargo'
    assert strutils.pluralize('erratum') == 'errata'
    assert strutils.singularize('errata') == 'erratum'
```
