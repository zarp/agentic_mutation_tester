import pytest
import setutils

# Helper for complement tests: get the _ComplementSet class
_ComplementSet = setutils.complement(set()).__class__

# ---------------------------
# IndexedSet: Construction and Basic Properties
# ---------------------------

def test_indexedset_empty_init():
    s = setutils.IndexedSet()
    assert len(s) == 0
    assert list(s) == []

def test_indexedset_init_from_iterable():
    s = setutils.IndexedSet([1, 2, 3, 2, 1])
    assert list(s) == [1, 2, 3]
    assert len(s) == 3

def test_indexedset_repr_and_eq():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([1, 2, 3])
    s3 = setutils.IndexedSet([3, 2, 1])
    assert repr(s1) == "IndexedSet([1, 2, 3])"
    assert s1 == s2
    assert s1 != s3
    assert s1 == set([1, 2, 3])
    assert s1 != set([1, 2])

def test_indexedset_from_iterable_classmethod():
    s = setutils.IndexedSet.from_iterable([4, 5, 6, 4])
    assert list(s) == [4, 5, 6]

# ---------------------------
# IndexedSet: Set Operations
# ---------------------------

def test_indexedset_add_and_contains():
    s = setutils.IndexedSet()
    s.add('a')
    s.add('b')
    s.add('a')
    assert 'a' in s
    assert 'b' in s
    assert 'c' not in s
    assert list(s) == ['a', 'b']

def test_indexedset_remove_and_discard():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    assert list(s) == [1, 3]
    with pytest.raises(KeyError):
        s.remove(2)
    s.discard(3)
    assert list(s) == [1]
    s.discard(42)  # Should not raise

def test_indexedset_clear():
    s = setutils.IndexedSet([1, 2, 3])
    s.clear()
    assert len(s) == 0
    assert list(s) == []

def test_indexedset_isdisjoint():
    s = setutils.IndexedSet([1, 2, 3])
    assert s.isdisjoint([4, 5])
    assert not s.isdisjoint([2, 5])

def test_indexedset_issubset_issuperset():
    s = setutils.IndexedSet([1, 2])
    assert s.issubset([1, 2, 3])
    assert not s.issubset([1])
    assert s.issuperset([1])
    assert not s.issuperset([1, 2, 3])

def test_indexedset_union_and_intersection():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = set([3, 4, 5])
    u = s1.union(s2)
    assert isinstance(u, setutils.IndexedSet)
    assert list(u) == [1, 2, 3, 4, 5]
    i = s1.intersection(s2)
    assert list(i) == [3]

def test_indexedset_difference_and_symmetric_difference():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = set([2, 3, 4])
    d = s1.difference(s2)
    assert list(d) == [1]
    sd = s1.symmetric_difference(s2)
    assert set(sd) == {1, 4}

def test_indexedset_operator_overloads():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([3, 4])
    assert list(s1 | s2) == [1, 2, 3, 4]
    assert list(s1 & s2) == [3]
    assert list(s1 - s2) == [1, 2]
    assert set(s1 ^ s2) == {1, 2, 4}
    # __rsub__
    s3 = set([1, 2, 3, 4])
    rsub = s3 - s1
    assert set(rsub) == {4}

def test_indexedset_inplace_operations():
    s = setutils.IndexedSet([1, 2, 3])
    s |= [3, 4]
    assert list(s) == [1, 2, 3, 4]
    s &= [2, 3, 4]
    assert list(s) == [2, 3, 4]
    s -= [3]
    assert list(s) == [2, 4]
    s ^= [2, 5]
    assert set(s) == {4, 5}

def test_indexedset_intersection_update_and_difference_update():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.intersection_update([2, 3, 5])
    assert list(s) == [2, 3]
    s.difference_update([3])
    assert list(s) == [2]

def test_indexedset_symmetric_difference_update():
    s = setutils.IndexedSet([1, 2, 3])
    s.symmetric_difference_update([2, 4])
    assert set(s) == {1, 3, 4}
    # self is other
    s2 = setutils.IndexedSet([1, 2])
    s2.symmetric_difference_update(s2)
    assert len(s2) == 0

# ---------------------------
# IndexedSet: List-like Operations
# ---------------------------

def test_indexedset_getitem_and_slice():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    assert s[0] == 'a'
    assert s[-1] == 'd'
    assert list(s[1:3]) == ['b', 'c']
    assert list(s[::-1]) == ['d', 'c', 'b', 'a']
    with pytest.raises(IndexError):
        _ = s[100]

def test_indexedset_pop():
    s = setutils.IndexedSet([1, 2, 3])
    val = s.pop()
    assert val == 3
    assert list(s) == [1, 2]
    val2 = s.pop(0)
    assert val2 == 1
    assert list(s) == [2]
    s.pop()
    assert len(s) == 0
    with pytest.raises(IndexError):
        s.pop()

def test_indexedset_count():
    s = setutils.IndexedSet([1, 2, 3])
    assert s.count(2) == 1
    assert s.count(42) == 0

def test_indexedset_reverse_and_sort():
    s = setutils.IndexedSet([3, 1, 2])
    s.reverse()
    assert list(s) == [2, 1, 3]
    s.sort()
    assert list(s) == [1, 2, 3]
    s.sort(reverse=True)
    assert list(s) == [3, 2, 1]

def test_indexedset_index():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s.index('b') == 1
    with pytest.raises(ValueError):
        s.index('z')

def test_indexedset_iter_and_reversed():
    s = setutils.IndexedSet([1, 2, 3])
    assert list(iter(s)) == [1, 2, 3]
    assert list(reversed(s)) == [3, 2, 1]

def test_indexedset_iter_slice():
    s = setutils.IndexedSet([1, 2, 3, 4, 5])
    assert list(s.iter_slice(1, 4)) == [2, 3, 4]
    assert list(s.iter_slice(0, None, 2)) == [1, 3, 5]
    assert list(s.iter_slice(None, None, -1)) == [5, 4, 3, 2, 1]

# ---------------------------
# IndexedSet: Dead Indices and Compaction (internal)
# ---------------------------

def test_indexedset_compaction_and_cull():
    # Remove enough elements to trigger compaction/cull
    s = setutils.IndexedSet(range(20))
    for i in range(10):
        s.remove(i)
    # Should still have correct elements and order
    assert list(s) == list(range(10, 20))
    # Add more and check order
    s.add(100)
    assert list(s)[-1] == 100

# ---------------------------
# complement: Construction and Basic Properties
# ---------------------------

def test_complement_basic_behavior():
    s = set([1, 2, 3])
    c = setutils.complement(s)
    assert isinstance(c, _ComplementSet)
    # Should not contain 1, 2, 3, but contain 4
    assert 1 not in c
    assert 4 in c

def test_complement_of_complement_is_original():
    s = set([1, 2, 3])
    c = setutils.complement(s)
    cc = setutils.complement(c)
    assert cc == s

def test_complement_repr():
    s = set([1, 2])
    c = setutils.complement(s)
    r = repr(c)
    assert r.startswith("complement(")
    cc = setutils.complement(c)
    assert "complement(complement(" in repr(cc)

def test_complement_contains_and_add_remove():
    s = set([1, 2])
    c = setutils.complement(s)
    assert 1 not in c
    c.add(1)
    assert 1 in c
    c.remove(3)
    assert 3 not in c

def test_complement_len_iter_bool():
    s = set([1, 2])
    c = setutils.complement(s)
    with pytest.raises(NotImplementedError):
        len(c)
    with pytest.raises(NotImplementedError):
        list(iter(c))
    assert bool(c)
    cc = setutils.complement(c)
    assert len(cc) == 2
    assert set(cc) == {1, 2}
    assert bool(cc)

def test_complement_pop():
    s = set([1, 2])
    c = setutils.complement(s)
    with pytest.raises(NotImplementedError):
        c.pop()
    cc = setutils.complement(c)
    popped = cc.pop()
    assert popped in {1, 2}

# ---------------------------
# complement: Set Operations
# ---------------------------



def test_complement_difference_and_rsub():
    s = set([1, 2, 3])
    c = setutils.complement(set([2, 3]))
    d = c - s
    assert isinstance(d, _ComplementSet)
    # Should be complement({2,3} | {1,2,3}) = complement({1,2,3})
    assert 1 not in d and 4 in d
    r = s - c
    # Should be _ComplementSet(included={1,2,3} & {2,3}) = {2,3}
    assert isinstance(r, _ComplementSet)
    assert set(r) == {2, 3}





def test_complement_symmetric_difference_update():
    c = setutils.complement(set([1, 2]))
    c.symmetric_difference_update(set([2, 3]))
    # Now c._excluded should be {1,2,3}
    assert 1 not in c and 2 not in c and 3 not in c


def test_complement_complemented_and_invert():
    c = setutils.complement(set([1, 2]))
    c2 = c.complemented()
    assert isinstance(c2, _ComplementSet)
    c3 = ~c
    assert isinstance(c3, _ComplementSet)
    # In-place complement
    c.complement()
    assert isinstance(c, _ComplementSet)


# ---------------------------
# complement: NotImplemented and TypeError
# ---------------------------

def test_complement_typeerror_on_invalid_arg():
    c = setutils.complement(set([1, 2]))
    with pytest.raises(TypeError):
        c.intersection(42)
    with pytest.raises(TypeError):
        c.issubset(42)
    with pytest.raises(TypeError):
        c.issuperset(42)
    with pytest.raises(TypeError):
        c.difference_update(42)
    with pytest.raises(TypeError):
        c.symmetric_difference(42)


# ---------------------------
# Miscellaneous
# ---------------------------


def test_indexedset_repr_with_complement():
    s = setutils.IndexedSet([1, 2, 3])
    c = setutils.complement(set([2]))
    r = repr(c)
    assert "complement" in r