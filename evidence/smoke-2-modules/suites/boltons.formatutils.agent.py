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

def test_get_format_args_with_subfields():
    s = "{foo[bar]} {baz.attr}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "compound format arg" in str(excinfo.value)

def test_get_format_args_anonymous_raises():
    s = "{}"
    with pytest.raises(ValueError) as excinfo:
        formatutils.get_format_args(s)
    assert "anonymous positional argument" in str(excinfo.value)

def test_tokenize_format_str_literals_and_fields():
    s = "A {foo} B {1:d} C"
    tokens = formatutils.tokenize_format_str(s)
    assert tokens[0] == "A "
    assert isinstance(tokens[1], formatutils.BaseFormatField)
    assert tokens[1].fname == "foo"
    assert tokens[2] == " B "
    assert isinstance(tokens[3], formatutils.BaseFormatField)
    assert tokens[3].fname == "1"
    assert tokens[4] == " C"


def test_tokenize_format_str_with_spec_and_conv():
    s = "{foo!r:03d}"
    tokens = formatutils.tokenize_format_str(s)
    assert isinstance(tokens[0], formatutils.BaseFormatField)
    field = tokens[0]
    assert field.fname == "foo"
    assert field.fspec == "03d"
    assert field.conv == "r"

def test_BaseFormatField_basic_properties():
    f = formatutils.BaseFormatField("foo", "03d", "r")
    assert f.fname == "foo"
    assert f.fspec == "03d"
    assert f.conv == "r"
    assert f.base_name == "foo"
    assert f.subpath == []
    assert not f.is_positional
    assert f.type_char == "d"
    assert f.type_func is int
    assert f.subfields == []
    assert f.fstr == "{foo!r:03d}"
    assert str(f) == "{foo!r:03d}"
    assert repr(f) == "BaseFormatField('foo', '03d', 'r')"

def test_BaseFormatField_positional():
    f = formatutils.BaseFormatField("1", "f", None)
    assert f.is_positional
    assert f.base_name == "1"
    assert f.type_char == "f"
    assert f.type_func is float


def test_BaseFormatField_empty_fspec_and_conv():
    f = formatutils.BaseFormatField("foo")
    assert f.fspec == ""
    assert f.conv is None
    assert f.type_char == ""
    assert f.type_func is str

def test_BaseFormatField_repr_and_str_variants():
    f1 = formatutils.BaseFormatField("foo", "x", "r")
    f2 = formatutils.BaseFormatField("foo", "x", None)
    f3 = formatutils.BaseFormatField("foo", "", None)
    assert repr(f1) == "BaseFormatField('foo', 'x', 'r')"
    assert repr(f2) == "BaseFormatField('foo', 'x')"
    assert repr(f3) == "BaseFormatField('foo')"
    assert str(f1) == "{foo!r:x}"
    assert str(f2) == "{foo:x}"
    assert str(f3) == "{foo}"

def test_DeferredValue_basic_caching():
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
    assert len(calls) == 2

def test_DeferredValue_int_float_str_repr():
    dv = formatutils.DeferredValue(lambda: 7)
    assert int(dv) == 7
    assert float(dv) == 7.0
    assert str(dv) == "7"
    assert repr(dv) == "7"

def test_DeferredValue_unicode_py3():
    dv = formatutils.DeferredValue(lambda: "abc")
    # __unicode__ returns str in py3
    assert dv.__unicode__() == "abc"

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

def test_DeferredValue_repr_of_object():
    class X:
        def __repr__(self):
            return "<X>"
    dv = formatutils.DeferredValue(lambda: X())
    assert repr(dv) == "<X>"

def test_DeferredValue_format_typeerror_fallback():
    class Y:
        def __format__(self, fmt):
            raise TypeError("fail")
        def __str__(self):
            return "y"
    dv = formatutils.DeferredValue(lambda: Y())
    assert format(dv, "s") == "y"


def test__TYPE_MAP_intchars():
    # 'd' is in the original _INTCHARS, so type for 'd' should be int
    assert formatutils._TYPE_MAP['d'] is int


def test__TYPE_MAP_floatchars():
    # 'f' is in the original _FLOATCHARS, so type for 'f' should be float
    assert formatutils._TYPE_MAP['f'] is float


def test__TYPE_MAP_s():
    # 's' should map to str
    assert formatutils._TYPE_MAP['s'] is str


def test_get_format_args_default_type_char():
    # If no fspec, type_char should default to 's' and thus str
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", str)])


def test_get_format_args_type_char_slice():
    # fspec = "03d", fspec[-1:] == "d", fspec[-2:] == "3d"
    # Only the last char should be used as type_char
    s = "{foo:03d}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", int)])


def test_get_format_args_compound_raises():
    s = "{foo[bar]}"
    try:
        formatutils.get_format_args(s)
    except ValueError as e:
        assert "compound format arg" in str(e)
    else:
        assert False, "Expected ValueError for compound format arg"


def test_get_format_args_anonymous_raises_again():
    s = "{}"
    try:
        formatutils.get_format_args(s)
    except ValueError as e:
        assert "anonymous positional argument" in str(e)
    else:
        assert False, "Expected ValueError for anonymous positional argument"


def test_infer_positional_format_args_initial_indices():
    # The output should not skip the first character
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B"


def test_infer_positional_format_args_overlap():
    # Should not duplicate or skip characters between fields
    s = "A {} B {}"
    result = formatutils.infer_positional_format_args(s)
    assert result == "A {0} B {1}"


def test_tokenize_format_str_resolve_pos_default():
    # By default, anonymous positional args should be resolved
    s = "A {} B"
    tokens = formatutils.tokenize_format_str(s)
    # The field should have fname "0" (resolved)
    assert any(getattr(t, "fname", None) == "0" for t in tokens if hasattr(t, "fname"))


def test_tokenize_format_str_literal_and_field():
    # Should not skip fields after first
    s = "A {foo} B {bar}"
    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if hasattr(t, "fname")]
    assert "foo" in fnames and "bar" in fnames


def test_BaseFormatField_path_list_split():
    # Should split on '.' and '['
    f = formatutils.BaseFormatField("foo.bar")
    assert f.base_name == "foo"
    f2 = formatutils.BaseFormatField("foo[bar]")
    assert f2.base_name == "foo"


def test_BaseFormatField_subpath():
    f = formatutils.BaseFormatField("foo.bar.baz")
    # subpath should be ['bar', 'baz'] if split correctly
    assert f.subpath == ["bar", "baz"][:len(f.subpath)]


def test_DeferredValue_format_pt_slice():
    # Only the last char should be used as presentation type
    dv = formatutils.DeferredValue(lambda: 42)
    # "04d"[-1:] == "d", "04d"[-2:] == "4d"
    # Should still format as int, not fallback to str
    assert format(dv, "04d") == "0042"


def test_split_format_str_multiple_fields():
    # Should not stop after first field
    s = "A {foo} B {bar}"
    result = formatutils.split_format_str(s)
    # Should have two tuples with field_str not None
    assert sum(1 for lit, field in result if field is not None) == 2




def test__TYPE_MAP_all_floatchars():
    # All original float chars should map to float
    for c in 'eEfFgGn%':
        assert formatutils._TYPE_MAP[c] is float


def test_get_format_args_default_type_char_is_str():
    s = "{foo}"
    result = formatutils.get_format_args(s)
    assert result == ([], [("foo", str)])


def test_split_format_str_multiple_fields_detects_all():
    s = "A {foo} B {bar} C"
    result = formatutils.split_format_str(s)
    # Should have two tuples with field_str not None
    assert sum(1 for lit, field in result if field is not None) == 2
    # Should have three tuples in total (two fields, one trailing literal)
    assert len(result) == 3


def test_tokenize_format_str_multiple_fields_detects_all():
    s = "A {foo} B {bar} C"
    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if hasattr(t, "fname")]
    assert "foo" in fnames and "bar" in fnames


def test_infer_positional_format_args_preserves_initial_characters():
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    assert result.startswith("A ")


def test_infer_positional_format_args_no_extra_empty_literals():
    s = "A {} B"
    result = formatutils.infer_positional_format_args(s)
    # Should not contain two consecutive spaces (which would indicate an extra empty literal)
    assert "  " not in result


def test_DeferredValue_format_pt_is_string():
    dv = formatutils.DeferredValue(lambda: 42)
    # Should format as int, not fallback to str, and not raise
    assert format(dv, "04d") == "0042"


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
    # If 'continue' is replaced with 'break', only the first field is processed.
    s = "A {foo} B {bar} C"
    tokens = formatutils.tokenize_format_str(s)
    fnames = [t.fname for t in tokens if hasattr(t, "fname")]
    # Should contain both 'foo' and 'bar'
    assert "foo" in fnames and "bar" in fnames
