import pytest
import formatutils

def test_construct_format_field_str_all_args():
    assert formatutils.construct_format_field_str('foo', '03d', 'r') == '{foo!r:03d}'

def test_construct_format_field_str_no_fspec_no_conv():
    assert formatutils.construct_format_field_str('foo', '', None) == '{foo}'

def test_construct_format_field_str_none_fname():
    assert formatutils.construct_format_field_str(None, '03d', 'r') == ''

def test_construct_format_field_str_only_conv():
    assert formatutils.construct_format_field_str('foo', '', 's') == '{foo!s}'

def test_construct_format_field_str_only_fspec():
    assert formatutils.construct_format_field_str('foo', 'x>10', None) == '{foo:x>10}'

def test_split_format_str_simple():
    s = "Hello {name}!"
    result = formatutils.split_format_str(s)
    assert result == [("Hello ", "{name}"), ("!", None)]

def test_split_format_str_multiple_fields():
    s = "{a} + {b} = {c}"
    result = formatutils.split_format_str(s)
    assert result == [("", "{a}"), (" + ", "{b}"), (" = ", "{c}")]

def test_split_format_str_literal_only():
    s = "no fields here"
    result = formatutils.split_format_str(s)
    assert result == [("no fields here", None)]

def test_split_format_str_with_conversion_and_spec():
    s = "Value: {val!r:03d}"
    result = formatutils.split_format_str(s)
    assert result == [("Value: ", "{val!r:03d}")]

def test_infer_positional_format_args_simple():
    s = "Hello {}, you are {} years old"
    result = formatutils.infer_positional_format_args(s)
    assert result == "Hello {0}, you are {1} years old"

def test_infer_positional_format_args_with_spec():
    s = "Value: {:03d}, Hex: {:x}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "Value: {0:03d}, Hex: {1:x}"

def test_infer_positional_format_args_with_escaped_braces():
    s = "Escaped {{}} and {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "Escaped {{}} and {0}"

def test_infer_positional_format_args_mixed_named_and_anon():
    s = "{foo} and {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{foo} and {0}"

def test_infer_positional_format_args_no_fields():
    s = "no fields"
    result = formatutils.infer_positional_format_args(s)
    assert result == "no fields"

def test_get_format_args_named_and_positional():
    s = "{noun} is {1:d} years old{punct}"
    result = formatutils.get_format_args(s)
    assert result == ([(1, int)], [('noun', str), ('punct', str)])

def test_get_format_args_only_named():
    s = "{foo} {bar!r} {baz:03d}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str), ('bar', str), ('baz', int)])

def test_get_format_args_only_positional():
    s = "{0} {1:f} {2!r}"
    result = formatutils.get_format_args(s)
    assert result == ([(0, str), (1, float), (2, str)], [])

def test_get_format_args_duplicate_fields():
    s = "{foo} {foo} {1} {1:d}"
    result = formatutils.get_format_args(s)
    assert result == ([(1, str)], [('foo', str)])

def test_get_format_args_compound_field_raises():
    s = "{foo.bar}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "compound format arg" in str(excinfo.value)

def test_get_format_args_anonymous_field_raises():
    s = "{}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "anonymous positional argument" in str(excinfo.value)

def test_get_format_args_field_in_spec():
    s = "{foo:{bar}}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str), ('bar', str)])

def test_tokenize_format_str_literals_and_fields():
    s = "A {foo} B {bar:03d} C"
    tokens = formatutils.tokenize_format_str(s)
    assert tokens[0] == "A "
    assert isinstance(tokens[1], formatutils.BaseFormatField)
    assert tokens[1].fname == "foo"
    assert tokens[2] == " B "
    assert isinstance(tokens[3], formatutils.BaseFormatField)
    assert tokens[3].fname == "bar"
    assert tokens[3].fspec == "03d"
    assert tokens[4] == " C"



def test_BaseFormatField_basic_properties():
    f = formatutils.BaseFormatField("foo", "03d", "r")
    assert f.fname == "foo"
    assert f.fspec == "03d"
    assert f.conv == "r"
    assert f.base_name == "foo"
    assert f.subpath == []
    assert f.is_positional is False
    assert f.type_char == "d"
    assert f.type_func is int
    assert f.fstr == "{foo!r:03d}"
    assert str(f) == "{foo!r:03d}"
    assert repr(f) == "BaseFormatField('foo', '03d', 'r')"

def test_BaseFormatField_positional_field():
    f = formatutils.BaseFormatField("0", "f")
    assert f.is_positional is True
    assert f.base_name == "0"
    assert f.type_func is float

def test_BaseFormatField_empty_fname():
    f = formatutils.BaseFormatField("", "")
    assert f.is_positional is True
    assert f.base_name == ""
    assert f.subpath == []

def test_BaseFormatField_with_subfields():
    f = formatutils.BaseFormatField("foo", "{bar}")
    assert f.subfields == ["bar"]

def test_BaseFormatField_repr_and_str_variants():
    f1 = formatutils.BaseFormatField("foo")
    assert repr(f1) == "BaseFormatField('foo')"
    assert str(f1) == "{foo}"

    f2 = formatutils.BaseFormatField("foo", "03d")
    assert repr(f2) == "BaseFormatField('foo', '03d')"
    assert str(f2) == "{foo:03d}"

def test_DeferredValue_caching_behavior():
    calls = []
    def func():
        calls.append(1)
        return 42
    dv = formatutils.DeferredValue(func)
    assert dv.get_value() == 42
    assert dv.get_value() == 42
    assert calls == [1]

def test_DeferredValue_no_cache():
    calls = []
    def func():
        calls.append(1)
        return 99
    dv = formatutils.DeferredValue(func, cache_value=False)
    assert dv.get_value() == 99
    assert dv.get_value() == 99
    assert calls == [1, 1]

def test_DeferredValue_int_float_str_repr():
    dv = formatutils.DeferredValue(lambda: 7)
    assert int(dv) == 7
    assert float(dv) == 7.0
    assert str(dv) == "7"
    assert repr(dv) == "7"

def test_DeferredValue_unicode_py3():
    dv = formatutils.DeferredValue(lambda: "hello")
    # __unicode__ returns str in py3
    assert dv.__unicode__() == "hello"

def test_DeferredValue_format_int():
    dv = formatutils.DeferredValue(lambda: 42)
    assert format(dv, "04d") == "0042"

def test_DeferredValue_format_float():
    dv = formatutils.DeferredValue(lambda: 3.14159)
    assert format(dv, ".2f") == "3.14"

def test_DeferredValue_format_str_fallback():
    class Weird:
        def __format__(self, fmt):
            raise ValueError("fail")
        def __str__(self):
            return "weird"
    dv = formatutils.DeferredValue(lambda: Weird())
    assert format(dv, "s") == "weird"

def test_DeferredValue_format_typeerror_fallback():
    class Weird:
        def __format__(self, fmt):
            raise TypeError("fail")
        def __str__(self):
            return "weird"
    dv = formatutils.DeferredValue(lambda: Weird())
    assert format(dv, "s") == "weird"


def test___all___contains_expected_names():
    # This test will fail if any of the names in __all__ are changed.
    expected = [
        'DeferredValue',
        'get_format_args',
        'tokenize_format_str',
        'construct_format_field_str',
        'infer_positional_format_args',
        'BaseFormatField'
    ]
    assert set(formatutils.__all__) == set(expected)


def test_split_format_str_multiple_fields_break_survivor():
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "{a} + {b} = {c}"
    result = formatutils.split_format_str(s)
    # The correct result should have all three fields.
    assert result == [("", "{a}"), (" + ", "{b}"), (" = ", "{c}")]


def test_infer_positional_format_args_starts_at_zero():
    # If the initial value is 1 instead of 0, the first anonymous field will be {1}
    s = "{} {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "{0} {1}"


def test_infer_positional_format_args_brace_copy_logic():
    # If the comparison is <=, it will duplicate a character at the boundary.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"




def test_get_format_args_float_type_chars():
    # If _FLOATCHARS is wrong, float types will not be detected.
    s = "{foo:e} {bar:E} {baz:f} {qux:F} {quux:g} {corge:G} {grault:n} {waldo:%}"
    result = formatutils.get_format_args(s)
    expected = ([], [
        ('foo', float), ('bar', float), ('baz', float),
        ('qux', float), ('quux', float), ('corge', float),
        ('grault', float), ('waldo', float)
    ])
    assert result == expected


def test_get_format_args_str_type_char():
    # If _TYPE_MAP['s'] is missing or wrong, 's' fields will not be str.
    s = "{foo:s}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_default_type_char_is_s():
    # If default is not 's', type will not be str for fields with no spec.
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_compound_field_error_message():
    s = "{foo.bar}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "compound format arg" in str(excinfo.value)


def test_get_format_args_anonymous_field_error_message():
    s = "{}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "anonymous positional argument" in str(excinfo.value)




def test_tokenize_format_str_break_survivor():
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "A {foo} B {bar}"
    tokens = formatutils.tokenize_format_str(s)
    # Should tokenize both fields
    assert any(isinstance(t, formatutils.BaseFormatField) and t.fname == "foo" for t in tokens)
    assert any(isinstance(t, formatutils.BaseFormatField) and t.fname == "bar" for t in tokens)


def test_BaseFormatField_subpath_split():
    # If the regex is wrong, subpath will not be split correctly.
    f = formatutils.BaseFormatField("foo.bar[0]")
    # Should split at '.' and '['
    assert f.base_name == "foo"
    assert f.subpath == ["bar", "0]"]


def test_BaseFormatField_subpath_index():
    # If subpath starts at 2, it will miss the first subfield.
    f = formatutils.BaseFormatField("foo.bar.baz")
    # Should have subpath ["bar", "baz"]
    assert f.subpath == ["bar", "baz"]


def test_DeferredValue_format_pt_slice():
    # If pt = fmt[-2:], type char will be wrong for single-char specs.
    dv = formatutils.DeferredValue(lambda: 42)
    # "d" is the type char, should format as int
    assert format(dv, "04d") == "0042"


def test_split_format_str_multiple_fields_all_fields():
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "{a} + {b} = {c}"
    result = formatutils.split_format_str(s)
    assert result == [("", "{a}"), (" + ", "{b}"), (" = ", "{c}")]


def test_infer_positional_format_args_initial_index_zero():
    # If initial prev_end is 1, the first character is skipped.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"


def test_infer_positional_format_args_brace_copy_logic_boundary():
    # If the comparison is <=, it will duplicate a character at the boundary.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"




def test_get_format_args_float_type_chars_all():
    s = "{foo:e} {bar:E} {baz:f} {qux:F} {quux:g} {corge:G} {grault:n} {waldo:%}"
    result = formatutils.get_format_args(s)
    expected = ([], [
        ('foo', float), ('bar', float), ('baz', float),
        ('qux', float), ('quux', float), ('corge', float),
        ('grault', float), ('waldo', float)
    ])
    assert result == expected


def test_get_format_args_str_type_char_s():
    s = "{foo:s}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_default_type_char_is_s_for_no_spec():
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_compound_field_error_message_text():
    s = "{foo.bar}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "compound format arg" in str(excinfo.value)


def test_get_format_args_anonymous_field_error_message_text():
    s = "{}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "anonymous positional argument" in str(excinfo.value)




def test_tokenize_format_str_multiple_fields_all_fields():
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "A {foo} B {bar}"
    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if isinstance(t, formatutils.BaseFormatField)]
    assert "foo" in fnames
    assert "bar" in fnames


def test_DeferredValue_format_pt_slice_single_char():
    # If pt = fmt[-2:], type char will be wrong for single-char specs.
    dv = formatutils.DeferredValue(lambda: 42)
    assert format(dv, "04d") == "0042"


def test_split_format_str_all_fields_are_processed():
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "{a} + {b} = {c}"
    result = formatutils.split_format_str(s)
    assert result == [("", "{a}"), (" + ", "{b}"), (" = ", "{c}")]


def test_infer_positional_format_args_initial_prev_end_zero():
    # If prev_end starts at 1, the first character is skipped.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"


def test_infer_positional_format_args_brace_copy_logic_strictly_less():
    # If the comparison is <=, it will duplicate a character at the boundary.
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"




def test_get_format_args_float_type_chars_survivor():
    s = "{foo:e} {bar:E} {baz:f} {qux:F} {quux:g} {corge:G} {grault:n} {waldo:%}"
    result = formatutils.get_format_args(s)
    expected = ([], [
        ('foo', float), ('bar', float), ('baz', float),
        ('qux', float), ('quux', float), ('corge', float),
        ('grault', float), ('waldo', float)
    ])
    assert result == expected


def test_get_format_args_str_type_char_survivor():
    s = "{foo:s}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_default_type_char_is_s_survivor():
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [('foo', str)])


def test_get_format_args_compound_field_error_message_survivor():
    s = "{foo.bar}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "compound format arg" in str(excinfo.value)


def test_get_format_args_anonymous_field_error_message_survivor():
    s = "{}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "anonymous positional argument" in str(excinfo.value)


def test_tokenize_format_str_resolve_pos_false():
    s = "{} {}"
    tokens = formatutils.tokenize_format_str(s, resolve_pos=False)
    # Should not convert anonymous fields to explicit positional
    fnames = [t.fname for t in tokens if isinstance(t, formatutils.BaseFormatField)]
    assert fnames == ['', '']


def test_tokenize_format_str_all_fields_are_processed():
    s = "A {foo} B {bar}"
    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if isinstance(t, formatutils.BaseFormatField)]
    assert "foo" in fnames
    assert "bar" in fnames
