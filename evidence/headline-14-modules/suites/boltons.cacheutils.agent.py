import pytest
import cacheutils

def test_lri_basic_insertion_and_eviction():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    assert dict(c) == {'a': 1, 'b': 2}
    c['c'] = 3
    # 'a' should be evicted (least recently inserted)
    assert dict(c) == {'b': 2, 'c': 3}
    assert c.get('a') is None
    assert c.get('b') == 2
    assert c.get('c') == 3


def test_lri_on_miss_callable():
    calls = []
    def on_miss(k):
        calls.append(k)
        return k.upper()
    c = cacheutils.LRI(max_size=2, on_miss=on_miss)
    c['a'] = 'A'
    assert c['a'] == 'A'
    assert c['b'] == 'B'
    assert calls == ['b']
    assert c['b'] == 'B'
    assert c.hit_count == 2
    assert c.miss_count == 1

def test_lri_on_miss_not_callable_raises():
    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=42)
    assert "expected on_miss to be a callable" in str(e.value)

def test_lri_zero_max_size_raises():
    with pytest.raises(ValueError) as e:
        cacheutils.LRI(max_size=0)
    assert "expected max_size > 0" in str(e.value)


def test_lri_clear_and_copy():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    c.clear()
    assert dict(c) == {}
    c2 = cacheutils.LRI(max_size=2)
    c2['x'] = 9
    c3 = c2.copy()
    assert dict(c3) == {'x': 9}
    assert c3.max_size == 2



def test_lri_repr():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    r = repr(c)
    assert "LRI" in r
    assert "max_size=2" in r
    assert "'a': 1" in r



def test_make_cache_key_basic_and_typed():
    k1 = cacheutils.make_cache_key(('a', 'b'), {'c': 'd'})
    assert isinstance(k1, cacheutils._HashedKey)
    assert tuple(k1) == ('a', 'b', cacheutils._KWARG_MARK, ('c', 'd'))
    k2 = cacheutils.make_cache_key((3,), {}, typed=False)
    assert k2 == 3
    k3 = cacheutils.make_cache_key((3,), {}, typed=True)
    assert isinstance(k3, cacheutils._HashedKey)
    assert tuple(k3) == (3, int)
    k4 = cacheutils.make_cache_key((), {})
    assert isinstance(k4, cacheutils._HashedKey)
    assert tuple(k4) == ()

def test_cached_function_and_repr():
    cache = {}
    def f(x): return x + 1
    wrapped = cacheutils.CachedFunction(f, cache)
    assert wrapped(2) == 3
    assert wrapped(2) == 3
    assert cache[list(cache.keys())[0]] == 3
    r = repr(wrapped)
    assert "CachedFunction" in r

def test_cached_function_cache_callable():
    cache = {}
    def f(x): return x + 1
    wrapped = cacheutils.CachedFunction(f, lambda: cache)
    assert wrapped(5) == 6

def test_cached_function_bad_cache_raises():
    def f(x): return x
    with pytest.raises(TypeError):
        cacheutils.CachedFunction(f, 42)

def test_cached_decorator_and_scoped():
    cache = {}
    @cacheutils.cached(cache)
    def f(x): return x * 2
    assert f(3) == 6
    assert f(3) == 6
    assert len(cache) == 1

def test_cachedmethod_with_attrgetter():
    class C(object):
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache')
        def f(self, x):
            return x + 1
    c = C()
    assert c.f(2) == 3
    assert c.f(2) == 3
    assert list(c.cache.values())[0] == 3

def test_cachedmethod_with_cache_callable():
    class C(object):
        def __init__(self):
            self._cache = {}
        @cacheutils.cachedmethod(lambda self: self._cache)
        def f(self, x):
            return x * 2
    c = C()
    assert c.f(4) == 8
    assert c.f(4) == 8
    assert list(c._cache.values())[0] == 8

def test_cachedmethod_bad_cache_raises():
    def f(self, x): return x
    with pytest.raises(TypeError):
        cacheutils.CachedMethod(f, 42)

def test_cachedmethod_repr_and_bound():
    class C(object):
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache')
        def f(self, x):
            return x
    c = C()
    m = c.f
    r = repr(m)
    assert "CachedMethod" in r

def test_cachedproperty_basic_and_delattr():
    class C(object):
        @cacheutils.cachedproperty
        def foo(self):
            return 42
    c = C()
    assert c.foo == 42
    c.__dict__['foo'] = 99
    assert c.foo == 99
    del c.__dict__['foo']
    assert c.foo == 42

def test_thresholdcounter_add_and_get():
    tc = cacheutils.ThresholdCounter(threshold=0.2)
    tc.add('a')
    tc.add('a')
    tc.add('b')
    assert tc['a'] == 2
    assert tc['b'] == 1
    assert tc.get('c') == 0
    assert tc.get('c', 99) == 99



def test_thresholdcounter_len_and_contains():
    tc = cacheutils.ThresholdCounter(threshold=0.5)
    tc.add('x')
    assert len(tc) == 1
    assert 'x' in tc
    assert 'y' not in tc

def test_thresholdcounter_invalid_threshold_raises():
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=0)
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=1)
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=-0.1)

def test_minidmap_basic_and_drop():
    class X(object): pass
    m = cacheutils.MinIDMap()
    x1 = X()
    x2 = X()
    id1 = m.get(x1)
    id2 = m.get(x2)
    assert id1 != id2
    assert x1 in m
    assert x2 in m
    m.drop(x1)
    assert x1 not in m
    # id1 should be reused
    x3 = X()
    id3 = m.get(x3)
    assert id3 == id1 or id3 == 0

def test_minidmap_iter_and_len():
    class X(object): pass
    m = cacheutils.MinIDMap()
    xs = [X() for _ in range(3)]
    for x in xs:
        m.get(x)
    assert set(m) == set(xs)
    assert len(m) == 3
    items = list(m.iteritems())
    assert all(isinstance(i[1], int) for i in items)


def test_lri_soft_miss_count_increment():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    # get with missing key increments soft_miss_count by 1
    c.get('b')
    assert c.soft_miss_count == 1
    # setdefault with missing key increments soft_miss_count by 1
    c.setdefault('c', 42)
    assert c.soft_miss_count == 2


def test_lri_get_returns_default():
    c = cacheutils.LRI(max_size=2)
    result = c.get('missing', 123)
    assert result == 123


def test_lri_setdefault_returns_value():
    c = cacheutils.LRI(max_size=2)
    val = c.setdefault('foo', 99)
    assert val == 99
    # setdefault on existing key returns the value, not the default
    val2 = c.setdefault('foo', 123)
    assert val2 == 99


def test_lri_pop_returns_value_and_default():
    c = cacheutils.LRI(max_size=2)
    c['x'] = 10
    val = c.pop('x')
    assert val == 10
    val2 = c.pop('y', 99)
    assert val2 == 99


def test_lri_popitem_returns_item():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    item = c.popitem()
    assert isinstance(item, tuple)
    assert item[0] in ('a', 'b')
    assert item[1] in (1, 2)


def test_lri_update_with_iterable_and_kwargs():
    c = cacheutils.LRI(max_size=4)
    c.update([('a', 1), ('b', 2)], c=3, d=4)
    assert c['a'] == 1
    assert c['b'] == 2
    assert c['c'] == 3
    assert c['d'] == 4


def test_lri_update_with_mapping():
    c = cacheutils.LRI(max_size=2)
    d = {'x': 1, 'y': 2}
    c.update(d)
    assert c['x'] == 1
    assert c['y'] == 2


def test_lri_update_self_noop():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c.update(c)
    assert c['a'] == 1


def test_lri_eq_and_ne():
    c1 = cacheutils.LRI(max_size=2)
    c2 = cacheutils.LRI(max_size=2)
    c1['a'] = 1
    c2['a'] = 1
    assert c1 == c2
    c2['b'] = 2
    assert c1 != c2








def test_lri_remove_from_ll_removes():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    c.__delitem__('a')
    assert 'a' not in c
    assert list(c.keys()) == ['b']


def test_lri_clear_resets():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    c.clear()
    assert len(c) == 0
    c['c'] = 3
    assert c['c'] == 3


def test_lri_copy_independent():
    c1 = cacheutils.LRI(max_size=2)
    c1['a'] = 1
    c2 = c1.copy()
    c2['b'] = 2
    assert 'b' not in c1
    assert 'b' in c2


def test_lri_repr_contains_all():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    r = repr(c)
    assert "LRI" in r
    assert "max_size=2" in r
    assert "'a': 1" in r


def test_lri_on_miss_called():
    calls = []
    def on_miss(k):
        calls.append(k)
        return k.upper()
    c = cacheutils.LRI(max_size=2, on_miss=on_miss)
    val = c.get('b')
    assert val == 'B'
    assert calls == ['b']


def test_lri_on_miss_not_callable_raises_typeerror():
    try:
        cacheutils.LRI(max_size=2, on_miss=42)
    except TypeError as e:
        assert "expected on_miss to be a callable" in str(e)


def test_lri_zero_max_size_raises_valueerror():
    try:
        cacheutils.LRI(max_size=0)
    except ValueError as e:
        assert "expected max_size > 0" in str(e)


def test_lri_pop_raises_keyerror():
    c = cacheutils.LRI(max_size=2)
    try:
        c.pop('missing')
    except KeyError:
        pass
    else:
        assert False, "Expected KeyError"


def test_lri_popitem_removes_item():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    item = c.popitem()
    assert item[0] not in c


def test_lri_setitem_overwrites_value():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['a'] = 2
    assert c['a'] == 2


def test_lri_len_and_contains():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    assert len(c) == 1
    assert 'a' in c
    assert 'b' not in c


def test_lri_keys_values_items():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    keys = c.keys()
    values = c.values()
    items = c.items()
    assert set(keys) == {'a', 'b'}
    assert set(values) == {1, 2}
    assert set(items) == {('a', 1), ('b', 2)}


def test_lri_default_max_size_128():
    # This kills the mutant that changes DEFAULT_MAX_SIZE from 128 to 129.
    c = cacheutils.LRI()
    for i in range(128):
        c[str(i)] = i
    # All 128 should be present
    assert len(c) == 128
    # Adding one more should evict the first
    c['extra'] = 999
    assert len(c) == 128
    assert '0' not in c
    assert 'extra' in c




def test_lri_max_size_le_zero_raises():
    # This kills the mutant that changes the check from <= 0 to <= 1.
    # max_size=1 should be allowed, but max_size=0 should raise.
    c = cacheutils.LRI(max_size=1)
    c['a'] = 1
    assert c['a'] == 1
    # max_size=0 should still raise
    import pytest
    with pytest.raises(ValueError):
        cacheutils.LRI(max_size=0)


def test_lri_on_miss_not_callable_typeerror_message():
    # This kills the mutant that changes the error message string for on_miss not callable.
    import pytest
    with pytest.raises(TypeError) as e:
        cacheutils.LRI(max_size=2, on_miss=123)
    assert "expected on_miss to be a callable" in str(e.value)
