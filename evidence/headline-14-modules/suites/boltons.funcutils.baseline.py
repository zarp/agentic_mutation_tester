import sys
import types
import pytest
import funcutils
import functools

# Helper for Python 2/3 compatibility
PY2 = sys.version_info[0] == 2

def test_get_module_callables_basic():
    import math
    types_map, funcs_map = funcutils.get_module_callables(math)
    # math has types (e.g., float) and functions (e.g., sin)
    assert isinstance(types_map, dict)
    assert isinstance(funcs_map, dict)
    assert 'sin' in funcs_map
    assert callable(funcs_map['sin'])
    # Should not include attributes from other modules
    assert all(getattr(math, k).__module__ == math.__name__ for k in funcs_map)

def test_get_module_callables_ignore():
    import math
    ignore = lambda name: name.startswith('a')
    types_map, funcs_map = funcutils.get_module_callables(math, ignore=ignore)
    assert all(not k.startswith('a') for k in types_map)
    assert all(not k.startswith('a') for k in funcs_map)

def test_get_module_callables_by_name():
    import math
    types_map, funcs_map = funcutils.get_module_callables('math')
    assert 'sin' in funcs_map

def test_mro_items():
    class A(object):
        x = 1
    class B(A):
        y = 2
    items = dict(funcutils.mro_items(B))
    assert 'x' in items
    assert 'y' in items
    assert items['x'] == 1
    assert items['y'] == 2

def test_dir_dict_includes_parent_attrs():
    class A(object):
        x = 1
    class B(A):
        y = 2
    b = B()
    d = funcutils.dir_dict(b)
    assert 'x' in d
    assert 'y' in d

def test_dir_dict_raises():
    class A(object):
        @property
        def bad(self):
            raise ValueError("fail")
    a = A()
    with pytest.raises(ValueError):
        funcutils.dir_dict(a, raise_exc=True)

def test_copy_function_basic():
    def foo(x):
        return x + 1
    foo.attr = 42
    foo_copy = funcutils.copy_function(foo)
    assert foo_copy is not foo
    assert foo_copy(2) == 3
    assert foo_copy.attr == 42
    # __kwdefaults__ copied if present
    if hasattr(foo, "__kwdefaults__"):
        assert foo_copy.__kwdefaults__ == foo.__kwdefaults__

def test_copy_function_no_dict():
    def foo(x):
        return x + 1
    foo.attr = 42
    foo_copy = funcutils.copy_function(foo, copy_dict=False)
    assert not hasattr(foo_copy, 'attr')

def test_partial_ordering():
    @funcutils.partial_ordering
    class MySet(set):
        def __le__(self, other):
            return set(self).issubset(other)
        def __ge__(self, other):
            return set(self).issuperset(other)
    a = MySet([1,2,3])
    b = MySet([1,2])
    c = MySet([1,2,4])
    assert b < a
    assert not b > a
    assert b < c
    assert not a < c
    assert not c > a
    assert (a == a)
    assert not (a == b)



def test_format_invocation():
    s = funcutils.format_invocation('func', args=(1, 2), kwargs={'c': 3})
    assert s == 'func(1, 2, c=3)'
    s = funcutils.format_invocation('a_func', args=(1,))
    assert s == 'a_func(1)'
    s = funcutils.format_invocation('kw_func', kwargs=[('a', 1), ('b', 2)])
    assert s == 'kw_func(a=1, b=2)'
    # Custom repr
    s = funcutils.format_invocation('f', args=(1,), kwargs={'a': 2}, repr=str)
    assert s == 'f(1, a=2)'
    # Unexpected kw
    with pytest.raises(TypeError):
        funcutils.format_invocation('f', foo=1)

def test_format_exp_repr_and_nonexp_repr():
    class Flag(object):
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
    # format_nonexp_repr
    s3 = funcutils.format_nonexp_repr(flag, ['length', 'width'], ['depth'])
    assert s3 == '<Flag length=5 width=10>'
    s4 = funcutils.format_nonexp_repr(flag)
    assert s4.startswith('<Flag id=')

def test_wraps_and_update_wrapper_basic():
    def print_return(func):
        @funcutils.wraps(func)
        def wrapper(*args, **kwargs):
            ret = func(*args, **kwargs)
            return ret
        return wrapper

    @print_return
    def example():
        """docstring"""
        return 'example return value'

    assert example() == 'example return value'
    assert example.__name__ == 'example'
    assert example.__doc__ == 'docstring'
    assert hasattr(example, '__wrapped__')
    # update_wrapper returns a new function, not in-place
    def foo(): return 1
    def bar(): return 2
    wrapped = funcutils.update_wrapper(bar, foo)
    assert wrapped is not bar
    assert wrapped.__name__ == foo.__name__



def test__parse_wraps_expected():
    # None
    assert funcutils._parse_wraps_expected(None) == []
    # string
    assert funcutils._parse_wraps_expected('foo') == [('foo', funcutils.NO_DEFAULT)]
    # sequence of strings
    assert funcutils._parse_wraps_expected(['foo', 'bar']) == [('foo', funcutils.NO_DEFAULT), ('bar', funcutils.NO_DEFAULT)]
    # mapping
    d = {'foo': 1, 'bar': 2}
    out = funcutils._parse_wraps_expected(d)
    assert ('foo', 1) in out and ('bar', 2) in out
    # sequence of pairs
    out = funcutils._parse_wraps_expected([('foo', 1), ('bar', 2)])
    assert ('foo', 1) in out and ('bar', 2) in out
    # error on bad input
    with pytest.raises(ValueError):
        funcutils._parse_wraps_expected(123)
    with pytest.raises(ValueError):
        funcutils._parse_wraps_expected([(1, 2)])

def test_functionbuilder_basic():
    fb = funcutils.FunctionBuilder('return_five', doc='returns the integer 5', body='return 5')
    f = fb.get_func()
    assert f() == 5
    assert f.__doc__ == 'returns the integer 5'
    # With vargs/kwargs
    fb.varkw = 'kw'
    f2 = fb.get_func()
    assert f2(a=1) == 5

def test_functionbuilder_from_func_and_add_arg_remove_arg():
    def foo(a, b=2): return a + b
    fb = funcutils.FunctionBuilder.from_func(foo)
    assert fb.name == 'foo'
    assert 'a' in fb.args
    # Add arg
    if not PY2:
        fb.add_arg('c', 3)
        assert 'c' in fb.args
        # Remove arg
        fb.remove_arg('c')
        assert 'c' not in fb.args
    else:
        fb.add_arg('c', 3)
        assert 'c' in fb.args
        fb.remove_arg('c')
        assert 'c' not in fb.args

def test_functionbuilder_get_defaults_dict_and_get_arg_names():
    fb = funcutils.FunctionBuilder('f', args=['a', 'b', 'c'], defaults=(1, 2))
    d = fb.get_defaults_dict()
    assert d == {'b': 1, 'c': 2}
    names = fb.get_arg_names()
    assert set(names) == set(['a', 'b', 'c'])
    req_names = fb.get_arg_names(only_required=True)
    assert req_names == ('a',)

def test_functionbuilder_remove_arg_missing():
    fb = funcutils.FunctionBuilder('f', args=['a', 'b'])
    with pytest.raises(funcutils.MissingArgument):
        fb.remove_arg('c')

def test_functionbuilder_add_arg_existing():
    fb = funcutils.FunctionBuilder('f', args=['a', 'b'])
    with pytest.raises(funcutils.ExistingArgument):
        if not PY2:
            fb.add_arg('a')
        else:
            fb.add_arg('a')

def test_indent():
    text = "foo\nbar"
    out = funcutils._indent(text, "  ")
    assert out == "  foo\n  bar"

def test_total_ordering_decorator():
    # Only test if our own total_ordering is used (Python <2.7)
    if not hasattr(functools, 'total_ordering'):
        @funcutils.total_ordering
        class A(object):
            def __lt__(self, other): return True
            def __eq__(self, other): return False
        a = A()
        b = A()
        assert a < b
        assert not (a == b)
        assert a <= b
        assert a != b

def test_noop():
    assert funcutils.noop() is None
    assert funcutils.noop(1, 2, foo='bar') is None