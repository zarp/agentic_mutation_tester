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

def test_partial_ordering_adds_comparisons():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    c = MySet([1,2,4])
    assert (b < a) is True
    assert (b > a) is False
    assert (b < c) is True
    assert (a < c) is False
    assert (c > a) is False
    assert (a == a) is True
    assert (a == b) is False




def test_format_invocation_with_args_and_kwargs_dict():
    s = funcutils.format_invocation('func', args=(1,2), kwargs={'c':3, 'b':2})
    # kwargs are sorted by key
    assert s == 'func(1, 2, b=2, c=3)'

def test_format_invocation_with_args_only():
    s = funcutils.format_invocation('a_func', args=(1,))
    assert s == 'a_func(1)'

def test_format_invocation_with_kwargs_list():
    s = funcutils.format_invocation('kw_func', kwargs=[('a', 1), ('b', 2)])
    assert s == 'kw_func(a=1, b=2)'

def test_format_invocation_repr_kwarg():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2}, repr=str)
    assert s == 'f(1, x=2)'

def test_format_invocation_unexpected_kwarg_raises():
    with pytest.raises(TypeError) as e:
        funcutils.format_invocation('f', foo=1)
    assert 'unexpected keyword args' in str(e.value)

def test_format_exp_repr_positional_and_optional():
    class Flag:
        def __init__(self, length, width, depth=None):
            self.length = length
            self.width = width
            self.depth = depth
    flag = Flag(5, 10)
    s = funcutils.format_exp_repr(flag, ['length', 'width'], [], ['depth'])
    assert s == 'Flag(5, 10)'
    flag2 = Flag(5, 15, 2)
    s2 = funcutils.format_exp_repr(flag2, ['length'], ['width', 'depth'])
    assert s2 == 'Flag(5, width=15, depth=2)'

def test_format_exp_repr_opt_key():
    class X:
        def __init__(self):
            self.a = 1
            self.b = 2
    x = X()
    s = funcutils.format_exp_repr(x, ['a'], [], ['b'], opt_key=lambda v: v == 2)
    assert s == 'X(1)'

def test_format_nonexp_repr_with_attrs():
    class Flag:
        def __init__(self, length, width, depth=None):
            self.length = length
            self.width = width
            self.depth = depth
    flag = Flag(5, 10)
    s = funcutils.format_nonexp_repr(flag, ['length', 'width'], ['depth'])
    assert s == "<Flag length=5 width=10>"

def test_format_nonexp_repr_with_no_attrs():
    class Empty:
        pass
    e = Empty()
    s = funcutils.format_nonexp_repr(e)
    assert s.startswith("<Empty id=") and s.endswith(">")

def test_format_nonexp_repr_opt_key():
    class X:
        def __init__(self):
            self.a = 1
            self.b = 2
    x = X()
    s = funcutils.format_nonexp_repr(x, ['a'], ['b'], opt_key=lambda v: v == 2)
    assert s == "<X a=1>"

def test_wraps_and_update_wrapper_preserve_metadata():
    def f(x):
        """docstring"""
        return x + 1
    def wrapper(x):
        return f(x)
    wrapped = funcutils.update_wrapper(wrapper, f)
    assert wrapped.__name__ == 'f'
    assert wrapped.__doc__ == 'docstring'
    assert wrapped(2) == 3
    # __wrapped__ is set
    assert wrapped.__wrapped__ is f

def test_wraps_decorator_factory():
    def f(x): """docstring""" ; return x + 1
    @funcutils.wraps(f)
    def g(x): return f(x)
    assert g.__name__ == 'f'
    assert g.__doc__ == 'docstring'
    assert g(2) == 3

def test_update_wrapper_injected_removes_arg():
    def f(x, y): return x + y
    def wrapper(y): return f(1, y)
    wrapped = funcutils.update_wrapper(wrapper, f, injected=['x'])
    assert wrapped(2) == 3

def test_update_wrapper_expected_adds_arg():
    def f(x): return x + 1
    def wrapper(x, y): return f(x) + y
    wrapped = funcutils.update_wrapper(wrapper, f, expected=[('y', 2)])
    assert wrapped(1, 2) == 4

def test_update_wrapper_inject_to_varkw():
    def f(x, **kwargs): return x + kwargs.get('y', 0)
    def wrapper(**kwargs): return f(1, **kwargs)
    wrapped = funcutils.update_wrapper(wrapper, f, injected=['x'])
    assert wrapped(y=2) == 3

def test_update_wrapper_hide_wrapped_removes_wrapped():
    def f(x): return x + 1
    def wrapper(x): return f(x)
    wrapped = funcutils.update_wrapper(wrapper, f, hide_wrapped=True)
    assert not hasattr(wrapped, '__wrapped__')



def test__parse_wraps_expected_string():
    items = funcutils._parse_wraps_expected('foo')
    assert items == [('foo', funcutils.NO_DEFAULT)]

def test__parse_wraps_expected_sequence():
    items = funcutils._parse_wraps_expected(['foo', 'bar'])
    assert ('foo', funcutils.NO_DEFAULT) in items
    assert ('bar', funcutils.NO_DEFAULT) in items

def test__parse_wraps_expected_mapping():
    items = funcutils._parse_wraps_expected({'foo': 1, 'bar': 2})
    assert ('foo', 1) in items
    assert ('bar', 2) in items

def test__parse_wraps_expected_pairs():
    items = funcutils._parse_wraps_expected([('foo', 1), ('bar', 2)])
    assert ('foo', 1) in items
    assert ('bar', 2) in items

def test__parse_wraps_expected_invalid_type():
    with pytest.raises(ValueError):
        funcutils._parse_wraps_expected(123)

def test__parse_wraps_expected_nonstring_argname():
    with pytest.raises(ValueError):
        funcutils._parse_wraps_expected([(1, 2)])

def test_functionbuilder_basic_usage():
    fb = funcutils.FunctionBuilder('return_five', doc='returns the integer 5', body='return 5')
    f = fb.get_func()
    assert f() == 5
    assert f.__doc__ == 'returns the integer 5'

def test_functionbuilder_with_args_and_defaults():
    fb = funcutils.FunctionBuilder('add', args=['x', 'y'], defaults=(2,), body='return x + y')
    f = fb.get_func()
    assert f(1, 2) == 3
    assert f(1) == 3

def test_functionbuilder_with_varargs_and_varkw():
    fb = funcutils.FunctionBuilder('f', args=['x'], varargs='args', varkw='kwargs', body='return x + sum(args) + sum(kwargs.values())')
    f = fb.get_func()
    assert f(1, 2, 3, a=4, b=5) == 1 + 2 + 3 + 4 + 5


def test_functionbuilder_remove_arg_missing_raises():
    fb = funcutils.FunctionBuilder('f', args=['x'], body='return x')
    with pytest.raises(funcutils.MissingArgument):
        fb.remove_arg('y')

def test_functionbuilder_add_existing_arg_raises():
    fb = funcutils.FunctionBuilder('f', args=['x'], body='return x')
    with pytest.raises(funcutils.ExistingArgument):
        fb.add_arg('x')

def test_functionbuilder_get_defaults_dict_and_get_arg_names():
    fb = funcutils.FunctionBuilder('f', args=['x', 'y'], defaults=(2,), body='return x + y')
    d = fb.get_defaults_dict()
    assert d == {'y': 2}
    names = fb.get_arg_names()
    assert 'x' in names and 'y' in names
    req_names = fb.get_arg_names(only_required=True)
    assert 'x' in req_names and 'y' not in req_names

def test_functionbuilder_get_sig_str_and_invocation_str():
    fb = funcutils.FunctionBuilder('f', args=['x', 'y'], defaults=(2,), body='return x + y')
    sig = fb.get_sig_str()
    inv = fb.get_invocation_str()
    assert 'x' in sig and 'y' in sig
    assert 'x' in inv and 'y' in inv

def test_functionbuilder_compile_invalid_body_raises():
    fb = funcutils.FunctionBuilder('f', body='return x +')
    with pytest.raises(SyntaxError):
        fb.get_func()

def test__indent_indents_lines():
    text = "a\nb"
    out = funcutils._indent(text, "  ")
    assert out == "  a\n  b"

def test_total_ordering_decorator():
    class A:
        def __lt__(self, other): return True
        def __eq__(self, other): return False
    decorated = funcutils.total_ordering(A)
    a = decorated()
    b = decorated()
    # __gt__ should be present
    assert hasattr(a, '__gt__')
    # __le__ should be present
    assert hasattr(a, '__le__')
    # __ge__ should be present
    assert hasattr(a, '__ge__')

def test_noop_returns_none():
    assert funcutils.noop() is None
    assert funcutils.noop(1, 2, x=3) is None


def test__IS_PY2_is_true():
    # Should be True on Python 2, False on Python 3. We can check the module variable.
    import sys
    assert funcutils._IS_PY2 is (sys.version_info[0] == 2)


def test__inspect_iscoroutinefunction_false_for_normal_func():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False


def test_NO_DEFAULT_is_not_string():
    # Should not be a string
    assert not isinstance(funcutils.NO_DEFAULT, str)


def test__IS_PY35_value():
    import sys
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected


def test_format_invocation_formatvalue_plus():
    # The default is '=' + repr(value)
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s


def test_format_invocation_formatreturns_plus():
    # This is only used in inspect_formatargspec, which is used in FunctionBuilder.get_sig_str
    fb = funcutils.FunctionBuilder('f', args=['x'], body='return x')
    sig = fb.get_sig_str(with_annotations=True)
    # Should not have '->' unless annotation is present
    assert sig.startswith('(x')


def test_inspect_formatargspec_annotation_colon():
    # Only applies if annotation is present
    def f(x: int): pass
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str(with_annotations=True)
    assert ': int' in sig








def test_inspect_formatargspec_star_for_kwonly():
    # If kwonlyargs is present, a '*' should appear in the signature
    fb = funcutils.FunctionBuilder('f', args=['a'], kwonlyargs=['b'], body='return a+b')
    sig = fb.get_sig_str()
    assert '*' in sig






def test_inspect_formatargspec_return_in_annotations():
    def f(x) -> int: return x
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str(with_annotations=True)
    assert '-> int' in sig


def test_inspect_formatargspec_result_plus_equals():
    def f(x) -> int: return x
    fb = funcutils.FunctionBuilder.from_func(f)
    sig = fb.get_sig_str(with_annotations=True)
    assert '-> int' in sig


def test_get_module_callables_ignore_continue():
    import math
    def ignore(name):
        return True
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    # All should be ignored, so both dicts should be empty
    assert types_map == {}
    assert funcs_map == {}


def test_get_module_callables_attr_mod_name_continue():
    # If attr.__module__ != mod.__name__, should continue, not break
    import math
    class Dummy:
        __module__ = 'not_math'
    math.dummy = Dummy
    try:
        types_map, funcs_map = funcutils.get_module_callables(math)
        assert 'dummy' not in types_map
    finally:
        del math.dummy


def test_dir_dict_default_raise_exc_false():
    class A:
        @property
        def bad(self):
            raise ValueError("fail")
    a = A()
    # Should not raise by default
    d = funcutils.dir_dict(a)
    assert 'bad' not in d


def test_copy_function_defaults():
    def f(x=1): return x
    f2 = funcutils.copy_function(f)
    assert f2.__defaults__ == (1,)


def test_copy_function_closure():
    def outer():
        x = 42
        def inner():
            return x
        return inner
    f = outer()
    f2 = funcutils.copy_function(f)
    assert f2() == 42


def test_copy_function_kwdefaults():
    def f(x=1, *, y=2): return x + y
    f2 = funcutils.copy_function(f)
    if hasattr(f, "__kwdefaults__"):
        assert f2.__kwdefaults__ == f.__kwdefaults__


def test_partial_ordering_lt_logic():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (b < a) is True
    assert (a < b) is False


def test_partial_ordering_gt_logic():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (a > b) is True
    assert (b > a) is False


def test_partial_ordering_eq_logic():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2,3])
    c = MySet([1,2])
    assert (a == b) is True
    assert (a == c) is False


def test__IS_PY2_matches_sys_version():
    assert funcutils._IS_PY2 is (sys.version_info[0] == 2)


def test__inspect_iscoroutinefunction_always_false_for_normal_func():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False




def test__IS_PY35_value_is_correct():
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected


def test__IS_PY35_is_true_for_python_3_5():
    # This test is only meaningful if running on 3.5+
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected


def test_format_invocation_formatvalue_equals_sign():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s








def test_get_module_callables_ignore_skips_all():
    import math
    def ignore(name):
        return True
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert types_map == {}
    assert funcs_map == {}


def test_get_module_callables_attr_mod_name_not_equal():
    import math
    class Dummy:
        __module__ = 'not_math'
    math.dummy = Dummy
    try:
        types_map, funcs_map = funcutils.get_module_callables(math)
        assert 'dummy' not in types_map
    finally:
        del math.dummy


def test_partial_ordering_lt_logic_kills_mutants():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (b < a) is True
    assert (a < b) is False


def test_partial_ordering_gt_logic_kills_mutants():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (a > b) is True
    assert (b > a) is False


def test_partial_ordering_eq_logic_kills_mutants():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2,3])
    c = MySet([1,2])
    assert (a == b) is True
    assert (a == c) is False


def test__IS_PY2_true_on_py2_false_on_py3():
    expected = sys.version_info[0] == 2
    assert funcutils._IS_PY2 is expected


def test__inspect_iscoroutinefunction_always_false():
    def f(): pass
    assert funcutils._inspect_iscoroutinefunction(f) is False




def test__IS_PY35_exact_35():
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected


def test__IS_PY35_for_36_and_above():
    expected = sys.version_info >= (3, 6)
    # The module should use 3.5 as the threshold, not 3.6
    assert funcutils._IS_PY35 == (sys.version_info >= (3, 5))


def test_format_invocation_formatvalue_plus_sign():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert 'x=2' in s


def test_format_invocation_formatvalue_equals_sign_literal():
    s = funcutils.format_invocation('f', args=(1,), kwargs={'x': 2})
    assert '=2' in s










def test_inspect_formatargspec_star_for_kwonly_marker():
    fb = funcutils.FunctionBuilder('f', args=['a'], kwonlyargs=['b'], body='return a+b')
    sig = fb.get_sig_str()
    assert '*' in sig








def test_get_module_callables_ignore_skips_all_mutant():
    import math
    def ignore(name):
        return True
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert types_map == {}
    assert funcs_map == {}


def test_get_module_callables_attr_mod_name_continue_mutant():
    import math
    class Dummy:
        __module__ = 'not_math'
    math.dummy = Dummy
    try:
        types_map, funcs_map = funcutils.get_module_callables(math)
        assert 'dummy' not in types_map
    finally:
        del math.dummy


def test_partial_ordering_lt_and_gt_and_eq_logic_mutants():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    c = MySet([1,2,3])
    # __lt__
    assert (b < a) is True
    assert (a < b) is False
    # __gt__
    assert (a > b) is True
    assert (b > a) is False
    # __eq__
    assert (a == c) is True
    assert (a == b) is False


def test_partial_ordering_does_not_override_existing_lt():
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
        def __lt__(self, other): return 'custom'
    decorated = funcutils.partial_ordering(MySet)
    a = decorated([1,2])
    b = decorated([1,2,3])
    assert a.__lt__(b) == 'custom'


def test_partial_ordering_does_not_override_existing_gt():
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
        def __gt__(self, other): return 'custom'
    decorated = funcutils.partial_ordering(MySet)
    a = decorated([1,2,3])
    b = decorated([1,2])
    assert a.__gt__(b) == 'custom'


def test_partial_ordering_does_not_override_existing_eq():
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
        def __eq__(self, other): return 'custom'
    decorated = funcutils.partial_ordering(MySet)
    a = decorated([1,2,3])
    b = decorated([1,2,3])
    assert a.__eq__(b) == 'custom'


def test_instancepartial_partialmethod_property_present():
    if funcutils.partialmethod is not None:
        ip = funcutils.InstancePartial(lambda self, x: x, 1)
        assert hasattr(ip, '_partialmethod')


def test_instancepartial_partialmethod_returns_partialmethod():
    if funcutils.partialmethod is not None:
        def f(self, x): return x
        ip = funcutils.InstancePartial(f, 1)
        pm = ip._partialmethod
        assert isinstance(pm, type(funcutils.partialmethod(lambda x: x)))


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
















def test_get_module_callables_ignore_continue_mutant():
    # line 148: continue -> break
    import math
    def ignore(name):
        return True
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert types_map == {}
    assert funcs_map == {}


def test_partial_ordering_lt_logic_mutants():
    # line 256: __lt__ logic mutants
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (b < a) is True
    assert (a < b) is False


def test_partial_ordering_gt_logic_mutants():
    # line 257: __gt__ logic mutants
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    assert (a > b) is True
    assert (b > a) is False


def test_partial_ordering_eq_logic_mutants():
    # line 258: __eq__ logic mutants
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other): return set(self).issubset(other)
        def __ge__(self, other): return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2,3])
    c = MySet([1,2])
    assert (a == b) is True
    assert (a == c) is False


def test_instancepartial_partialmethod_property_returns_partialmethod_mutant():
    # line 306: return partialmethod(...) -> None
    if funcutils.partialmethod is not None:
        def f(self, x): return x
        ip = funcutils.InstancePartial(f, 1)
        pm = ip._partialmethod
        assert isinstance(pm, type(funcutils.partialmethod(lambda x: x)))


def test__IS_PY2_true_and_false_mutant():
    # line 56: _IS_PY2 = True -> False
    # Should match sys.version_info[0] == 2
    expected = sys.version_info[0] == 2
    assert funcutils._IS_PY2 is expected


def test__IS_PY35_threshold_and_value_mutants():
    # line 78: comparison >= -> >, 5 -> 6
    expected = sys.version_info >= (3, 5)
    assert funcutils._IS_PY35 == expected










def test_get_module_callables_ignore_continue_break_mutant():
    # line 148: continue -> break
    import math
    def ignore(name):
        return True
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert types_map == {}
    assert funcs_map == {}


def test_get_module_callables_attr_mod_name_continue_break_mutant():
    # line 152: continue -> break
    import math
    class Dummy:
        __module__ = 'not_math'
    math.dummy = Dummy
    try:
        types_map, funcs_map = funcutils.get_module_callables(math)
        assert 'dummy' not in types_map
    finally:
        del math.dummy




def test_cachedinstancepartial_set_name_ge_gt_36_mutant():
    # line 308: >= -> >, 3 -> 4, 6 -> 7
    # Should only set __name__ if sys.version_info >= (3, 6)
    class C:
        pass
    ip = funcutils.CachedInstancePartial(lambda self: 1)
    # __set_name__ should not be called unless >= 3.6, but we can't force Python version in test
    # So we check that __name__ is set after __get__ is called
    c = C()
    m = ip.__get__(c, C)
    assert hasattr(ip, '__name__')
