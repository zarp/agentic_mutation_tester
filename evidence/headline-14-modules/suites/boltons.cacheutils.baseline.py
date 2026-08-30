import pytest
import cacheutils

import sys
import types

# --- LRI and LRU ---

def test_lri_basic_set_get_evict():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c['b'] = 2
    assert c['a'] == 1
    assert c['b'] == 2
    c['c'] = 3  # should evict 'a'
    assert 'a' not in c
    assert c['b'] == 2
    assert c['c'] == 3


def test_lri_on_miss_typeerror():
    with pytest.raises(TypeError):
        cacheutils.LRI(max_size=2, on_miss=123)

def test_lri_max_size_zero():
    with pytest.raises(ValueError):
        cacheutils.LRI(max_size=0)

def test_lri_get_and_setdefault_soft_miss():
    c = cacheutils.LRI(max_size=2)
    assert c.get('foo') is None
    assert c.soft_miss_count == 1
    assert c.setdefault('foo', 42) == 42
    assert c['foo'] == 42
    assert c.soft_miss_count == 2

def test_lri_update_and_clear():
    c = cacheutils.LRI(max_size=3)
    c.update({'a': 1, 'b': 2})
    c.update([('c', 3)])
    assert set(c.keys()) == {'a', 'b', 'c'}
    c.clear()
    assert len(c) == 0
    assert list(c.keys()) == []



def test_lri_repr():
    c = cacheutils.LRI(max_size=2, on_miss=None)
    c['a'] = 1
    r = repr(c)
    assert 'LRI' in r
    assert 'max_size=2' in r

def test_lri_update_with_kwargs():
    c = cacheutils.LRI(max_size=3)
    c.update({'a': 1}, b=2, c=3)
    assert set(c.keys()) == {'a', 'b', 'c'}

def test_lri_update_self_noop():
    c = cacheutils.LRI(max_size=2)
    c['a'] = 1
    c.update(c)
    assert c['a'] == 1

def test_lri_ne_and_eq():
    c1 = cacheutils.LRI(max_size=2)
    c2 = cacheutils.LRI(max_size=2)
    assert not (c1 != c2)
    c1['a'] = 1
    assert c1 != c2

def test_lru_usage_and_eviction():
    c = cacheutils.LRU(max_size=2)
    c['a'] = 1
    c['b'] = 2
    _ = c['a']  # access 'a' to make it most recently used
    c['c'] = 3  # should evict 'b'
    assert 'b' not in c
    assert 'a' in c
    assert 'c' in c

def test_lru_on_miss():
    c = cacheutils.LRU(max_size=2, on_miss=lambda k: k*2)
    assert c['x'] == 'xx'
    assert c['x'] == 'xx'
    assert c.hit_count == 1
    assert c.miss_count == 1

def test_lru_repr():
    c = cacheutils.LRU(max_size=2)
    c['a'] = 1
    r = repr(c)
    assert 'LRU' in r

# --- make_cache_key and _HashedKey ---

def test_make_cache_key_simple():
    k = cacheutils.make_cache_key((1, 2), {'a': 3})
    assert isinstance(k, cacheutils._HashedKey)
    assert tuple(k) == (1, 2, cacheutils._KWARG_MARK, ('a', 3))

def test_make_cache_key_typed():
    k1 = cacheutils.make_cache_key((3,), {}, typed=True)
    k2 = cacheutils.make_cache_key((3.0,), {}, typed=True)
    assert k1 != k2

def test_make_cache_key_fasttype():
    k = cacheutils.make_cache_key((42,), {})
    assert k == 42

def test__HashedKey_repr_and_hash():
    k = cacheutils._HashedKey([1, 2, 3])
    r = repr(k)
    assert '_HashedKey' in r
    assert hash(k) == hash(tuple([1, 2, 3]))

# --- CachedFunction and cached ---

def test_CachedFunction_basic():
    cache = {}
    def f(x): return x + 1
    cf = cacheutils.CachedFunction(f, cache)
    assert cf(1) == 2
    assert cf(1) == 2  # from cache
    assert len(cache) == 1

def test_CachedFunction_cache_callable():
    cache = {}
    def f(x): return x + 1
    cf = cacheutils.CachedFunction(f, lambda: cache)
    assert cf(2) == 3
    assert cf(2) == 3
    assert len(cache) == 1

def test_CachedFunction_cache_typeerror():
    with pytest.raises(TypeError):
        cacheutils.CachedFunction(lambda x: x, 123)

def test_CachedFunction_repr():
    cache = {}
    def f(x): return x
    cf = cacheutils.CachedFunction(f, cache)
    r = repr(cf)
    assert 'CachedFunction' in r

def test_cached_decorator():
    cache = {}
    @cacheutils.cached(cache)
    def f(x): return x * 2
    assert f(3) == 6
    assert f(3) == 6
    assert len(cache) == 1

def test_cached_decorator_typed():
    cache = {}
    @cacheutils.cached(cache, typed=True)
    def f(x): return x
    assert f(3) == 3
    assert f(3.0) == 3.0
    assert len(cache) == 2

# --- CachedMethod and cachedmethod ---

class DummyObj:
    def __init__(self):
        self.cache = {}

def test_CachedMethod_with_attrgetter():
    class C:
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache')
        def foo(self, x):
            return x + 1
    c = C()
    assert c.foo(1) == 2
    assert c.foo(1) == 2
    assert len(c.cache) == 1

def test_CachedMethod_with_cache_callable():
    class C:
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod(lambda obj: obj.cache)
        def foo(self, x):
            return x + 2
    c = C()
    assert c.foo(2) == 4
    assert c.foo(2) == 4
    assert len(c.cache) == 1


def test_CachedMethod_cache_typeerror():
    def f(self, x): return x
    with pytest.raises(TypeError):
        cacheutils.CachedMethod(f, 123)

def test_CachedMethod_repr():
    class C:
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache')
        def foo(self, x):
            return x
    c = C()
    r = repr(c.foo)
    assert 'CachedMethod' in r

def test_cachedmethod_decorator():
    class C:
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache')
        def foo(self, x):
            return x * 2
    c = C()
    assert c.foo(4) == 8
    assert c.foo(4) == 8
    assert len(c.cache) == 1

def test_cachedmethod_decorator_typed():
    class C:
        def __init__(self):
            self.cache = {}
        @cacheutils.cachedmethod('cache', typed=True)
        def foo(self, x):
            return x
    c = C()
    assert c.foo(3) == 3
    assert c.foo(3.0) == 3.0
    assert len(c.cache) == 2

# --- cachedproperty ---

def test_cachedproperty_basic():
    class C:
        def __init__(self):
            self.calls = 0
        @cacheutils.cachedproperty
        def foo(self):
            self.calls += 1
            return 42
    c = C()
    assert c.foo == 42
    assert c.foo == 42
    assert c.calls == 1  # only called once

def test_cachedproperty_delattr():
    class C:
        @cacheutils.cachedproperty
        def foo(self):
            return 99
    c = C()
    assert c.foo == 99
    del c.__dict__['foo']
    assert c.foo == 99  # recomputed

def test_cachedproperty_repr():
    class C:
        @cacheutils.cachedproperty
        def foo(self): return 1
    r = repr(C.foo)
    assert 'cachedproperty' in r

# --- ThresholdCounter ---

def test_thresholdcounter_add_and_get():
    tc = cacheutils.ThresholdCounter(threshold=0.1)
    tc.add('a')
    assert tc['a'] == 1
    tc.add('a')
    assert tc['a'] == 2
    assert 'a' in tc
    assert tc.get('b') == 0

def test_thresholdcounter_update_with_iterable():
    tc = cacheutils.ThresholdCounter(threshold=0.2)
    tc.update(['x', 'y', 'x'])
    assert tc['x'] == 2
    assert tc['y'] == 1





def test_thresholdcounter_commonality_and_counts():
    tc = cacheutils.ThresholdCounter(threshold=0.5)
    for i in range(10):
        tc.add('a')
    for i in range(2):
        tc.add('b')
    assert tc.get_common_count() == tc['a'] + tc['b']
    assert tc.get_uncommon_count() == tc.total - tc.get_common_count()
    assert 0 < tc.get_commonality() <= 1

def test_thresholdcounter_invalid_threshold():
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=0)
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=1)
    with pytest.raises(ValueError):
        cacheutils.ThresholdCounter(threshold=-0.1)

def test_thresholdcounter_len_and_contains():
    tc = cacheutils.ThresholdCounter(threshold=0.5)
    tc.add('a')
    assert len(tc) == 1
    assert 'a' in tc
    assert 'b' not in tc


# --- MinIDMap ---

def test_minidmap_basic_and_drop():
    class Obj: pass
    m = cacheutils.MinIDMap()
    o1 = Obj()
    o2 = Obj()
    id1 = m.get(o1)
    id2 = m.get(o2)
    assert id1 != id2
    assert o1 in m
    assert o2 in m
    m.drop(o1)
    assert o1 not in m
    # id1 should be reused
    o3 = Obj()
    id3 = m.get(o3)
    assert id3 == id1

def test_minidmap_iter_and_len():
    class Obj: pass
    m = cacheutils.MinIDMap()
    objs = [Obj() for _ in range(3)]
    for o in objs:
        m.get(o)
    assert len(m) == 3
    assert set(m) == set(objs)
    items = list(m.iteritems())
    assert all(isinstance(i[1], int) for i in items)

def test_minidmap_weakref_cleanup(monkeypatch):
    import gc
    class Obj: pass
    m = cacheutils.MinIDMap()
    o = Obj()
    id1 = m.get(o)
    # Remove all references to o, force gc, id1 should be freed
    ref = o
    del o
    gc.collect()
    # The free list should now contain id1
    assert id1 in m.free or id1 == 0  # id1 is 0 for first object

def test_minidmap_drop_and_reuse():
    class Obj: pass
    m = cacheutils.MinIDMap()
    o1 = Obj()
    o2 = Obj()
    id1 = m.get(o1)
    id2 = m.get(o2)
    m.drop(o1)
    o3 = Obj()
    id3 = m.get(o3)
    assert id3 == id1

def test_minidmap_contains_and_iter():
    class Obj: pass
    m = cacheutils.MinIDMap()
    o1 = Obj()
    o2 = Obj()
    m.get(o1)
    m.get(o2)
    assert o1 in m
    assert o2 in m
    assert set(iter(m)) == {o1, o2}