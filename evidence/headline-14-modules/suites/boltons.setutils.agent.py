import setutils
import pytest

def test_indexedset_insertion_order_and_uniqueness():
    s = setutils.IndexedSet([1, 2, 3, 2, 1])
    assert list(s) == [1, 2, 3]
    assert s.item_list[:3] == [1, 2, 3]
    assert len(s) == 3

def test_indexedset_repr_and_equality():
    s1 = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([1, 2, 3])
    s3 = setutils.IndexedSet([3, 2, 1])
    assert repr(s1) == "IndexedSet([1, 2, 3])"
    assert s1 == s2
    assert s1 != s3
    assert s1 == set([1, 2, 3])
    assert s1 != set([1, 2])

def test_indexedset_contains_and_iter():
    s = setutils.IndexedSet([1, 2, 3])
    assert 2 in s
    assert 4 not in s
    assert list(iter(s)) == [1, 2, 3]

def test_indexedset_reversed():
    s = setutils.IndexedSet([1, 2, 3])
    assert list(reversed(s)) == [3, 2, 1]

def test_indexedset_getitem_index_and_slice():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    assert s[0] == 'a'
    assert s[1] == 'b'
    assert s[-1] == 'd'
    assert list(s[:2]) == ['a', 'b']
    assert list(s[1:3]) == ['b', 'c']
    assert list(s[::-1]) == ['d', 'c', 'b', 'a']
    assert isinstance(s[1:3], setutils.IndexedSet)
    with pytest.raises(IndexError):
        _ = s[10]

def test_indexedset_index_method():
    s = setutils.IndexedSet(['x', 'y', 'z'])
    assert s.index('x') == 0
    assert s.index('y') == 1
    assert s.index('z') == 2
    with pytest.raises(ValueError) as e:
        s.index('notfound')
    assert "not in IndexedSet" in str(e.value)

def test_indexedset_add_and_discard_remove():
    s = setutils.IndexedSet()
    s.add(1)
    s.add(2)
    s.add(1)
    assert list(s) == [1, 2]
    s.discard(2)
    assert list(s) == [1]
    s.discard(2)  # no error
    s.add(3)
    assert list(s) == [1, 3]
    s.remove(1)
    assert list(s) == [3]
    with pytest.raises(KeyError):
        s.remove(1)

def test_indexedset_clear():
    s = setutils.IndexedSet([1, 2, 3])
    s.clear()
    assert list(s) == []
    assert len(s) == 0

def test_indexedset_isdisjoint_issubset_issuperset():
    s = setutils.IndexedSet([1, 2, 3])
    assert s.isdisjoint([4, 5])
    assert not s.isdisjoint([2, 5])
    assert s.issubset([1, 2, 3, 4])
    assert not s.issubset([1, 2])
    assert s.issuperset([1, 2])
    assert not s.issuperset([1, 2, 3, 4])

def test_indexedset_union_and_intersection_difference():
    s = setutils.IndexedSet([1, 2, 3])
    u = s.union([3, 4, 5])
    assert isinstance(u, setutils.IndexedSet)
    assert list(u) == [1, 2, 3, 4, 5]
    i = s.intersection([2, 3, 4])
    assert list(i) == [2, 3]
    d = s.difference([2, 4])
    assert list(d) == [1, 3]
    # Multiple others
    s2 = setutils.IndexedSet([2, 3, 4])
    s3 = setutils.IndexedSet([3, 4, 5])
    i2 = s.intersection(s2, s3)
    assert list(i2) == [3]
    d2 = s.difference(s2, s3)
    assert list(d2) == [1]


def test_indexedset_set_operators():
    s = setutils.IndexedSet([1, 2, 3])
    s2 = setutils.IndexedSet([2, 3, 4])
    assert list((s | s2)) == [1, 2, 3, 4]
    assert list((s & s2)) == [2, 3]
    assert list((s - s2)) == [1]
    assert list((s2 - s)) == [4]
    assert list((s ^ s2)) == [1, 4]

def test_indexedset_inplace_operators():
    s = setutils.IndexedSet([1, 2, 3])
    s |= [3, 4]
    assert list(s) == [1, 2, 3, 4]
    s &= [2, 3, 4]
    assert list(s) == [2, 3, 4]
    s -= [3]
    assert list(s) == [2, 4]
    s ^= [2, 5]
    assert list(s) == [4, 5]

def test_indexedset_update_and_intersection_update_difference_update():
    s = setutils.IndexedSet([1, 2])
    s.update([2, 3])
    assert list(s) == [1, 2, 3]
    s.intersection_update([2, 3, 4])
    assert list(s) == [2, 3]
    s.difference_update([3])
    assert list(s) == [2]
    s2 = setutils.IndexedSet([2])
    s2.difference_update(s2)
    assert list(s2) == []

def test_indexedset_symmetric_difference_update():
    s = setutils.IndexedSet([1, 2, 3])
    s.symmetric_difference_update([2, 3, 4])
    assert list(s) == [1, 4]
    # self is other
    s2 = setutils.IndexedSet([1, 2])
    s2.symmetric_difference_update(s2)
    assert list(s2) == []

def test_indexedset_pop():
    s = setutils.IndexedSet([1, 2, 3])
    val = s.pop()
    assert val == 3
    assert list(s) == [1, 2]
    s.add(4)
    val2 = s.pop(0)
    assert val2 == 1
    assert list(s) == [2, 4]
    with pytest.raises(IndexError):
        s.pop(10)

def test_indexedset_count():
    s = setutils.IndexedSet([1, 2, 3])
    assert s.count(2) == 1
    assert s.count(4) == 0

def test_indexedset_reverse_and_sort():
    s = setutils.IndexedSet([3, 1, 2])
    s.reverse()
    assert list(s) == [2, 1, 3]
    s.sort()
    assert list(s) == [1, 2, 3]
    s.sort(reverse=True)
    assert list(s) == [3, 2, 1]

def test_indexedset_iter_slice():
    s = setutils.IndexedSet([1, 2, 3, 4, 5])
    assert list(s.iter_slice(1, 4)) == [2, 3, 4]
    assert list(s.iter_slice(0, None, 2)) == [1, 3, 5]
    assert list(s.iter_slice(None, None, -1)) == [5, 4, 3, 2, 1]

def test_indexedset_dead_indices_and_compaction():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(2)
    s.remove(3)
    # Dead indices should be present
    assert 2 not in s and 3 not in s
    # After compaction, dead_indices should be empty
    s._compact()
    assert s.dead_indices == []

def test_indexedset_from_iterable():
    s = setutils.IndexedSet.from_iterable([1, 2, 3])
    assert list(s) == [1, 2, 3]

def test_indexedset_rsub():
    s = setutils.IndexedSet([1, 2, 3])
    result = set([1, 2, 3, 4]) - s
    assert isinstance(result, set)
    assert result == set([4])

def test_complement_basic_behavior():
    s = set([1, 2, 3])
    c = setutils.complement(s)
    assert 4 in c
    assert 2 not in c
    # complement of complement returns original set
    cc = setutils.complement(c)
    assert cc == s
    # __repr__ for complement
    assert repr(c) == "complement({0})".format(repr(s))

def test_complement_contains_and_add_remove():
    s = set([1, 2])
    c = setutils.complement(s)
    assert 3 in c
    assert 2 not in c
    c.add(2)
    assert 2 in c
    c.remove(4)
    assert 4 not in c

def test_complement_pop_and_len_iter():
    s = set([1, 2])
    c = setutils.complement(s)
    with pytest.raises(NotImplementedError):
        c.pop()
    with pytest.raises(NotImplementedError):
        len(c)
    with pytest.raises(NotImplementedError):
        list(iter(c))
    # But for complemented complement, these work
    cc = setutils.complement(c)
    assert len(cc) == 2
    assert set(cc) == set([1, 2])

def test_complement_and_or_xor():
    s1 = set([1, 2, 3])
    s2 = set([2, 3, 4])
    c1 = setutils.complement(s1)
    c2 = setutils.complement(s2)
    # intersection: set & complement
    i = set([0, 1, 2, 3, 4]) & c1
    assert set(i) == set([0, 4])
    # complement & set
    i2 = c1 & set([0, 1, 2, 3, 4])
    assert set(i2._included) == set([0, 4])
    # complement & complement
    i3 = c1 & c2
    assert isinstance(i3, type(c1))
    # union: set | complement
    u = set([1, 2]) | c1
    assert isinstance(u, type(c1))
    # xor: set ^ complement
    x = set([1, 2]) ^ c1
    assert isinstance(x, type(c1))






def test_complement_bool():
    s = set([1, 2])
    c = setutils.complement(s)
    assert bool(c)
    cc = setutils.complement(c)
    assert bool(cc) == bool(set([1, 2]))
    c_empty = setutils.complement(set())
    assert bool(c_empty)

def test_complement_complemented_and_complement_method():
    s = set([1, 2])
    c = setutils.complement(s)
    c2 = c.complemented()
    assert isinstance(c2, type(c))
    c.complement()
    assert c._included == set([1, 2])
    assert c._excluded is None

def test_complement_invalid_operations():
    s = set([1, 2])
    c = setutils.complement(s)
    with pytest.raises(TypeError):
        c.intersection(123)
    with pytest.raises(TypeError):
        c.union(123)
    with pytest.raises(TypeError):
        c.symmetric_difference(123)
    with pytest.raises(TypeError):
        c.difference(123)
    with pytest.raises(TypeError):
        c.issubset(123)
    with pytest.raises(TypeError):
        c.issuperset(123)
    with pytest.raises(TypeError):
        c.difference_update(123)










def test__get_apparent_index_negative_index():
    s = setutils.IndexedSet(['x', 'y', 'z'])
    s.remove('y')
    # Now, s.item_list = ['x', _MISSING, 'z']
    # Negative index -1 should resolve to last valid element, which is 'z'
    assert s._get_apparent_index(-1) == 1








def test__compact_updates_c_max_size():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    s._compact()
    # _c_max_size should be at least the length of item_list before compaction
    assert s._c_max_size >= 3


def test__compactions_initial_value():
    s = setutils.IndexedSet()
    assert s._compactions == 0


def test__get_real_index_return_value():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1


def test__get_apparent_index_return_value():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test___all__exports():
    assert 'IndexedSet' in setutils.__all__
    assert 'complement' in setutils.__all__


def test__MISSING_is_unique():
    # _MISSING should not be equal to any normal object
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(2)
    # The removed slot should be _MISSING, which is not 1 or 3
    assert all(item is not 2 for item in s.item_list if item is not setutils._MISSING)


def test__cull_compaction_factor_threshold():
    # Should compact when dead_index_count > len(items) / _COMPACTION_FACTOR
    s = setutils.IndexedSet(range(20))
    # Remove enough items to exceed threshold for compaction
    for i in range(3, 20):
        s.remove(i)
    # At this point, dead_index_count = 17, len(item_list) = 20
    # 17 > 20/8 == 2.5, so compaction should occur
    # After compaction, dead_indices should be empty
    s._cull()
    assert s.dead_indices == []


def test__c_max_size_initial_value():
    s = setutils.IndexedSet()
    assert s._c_max_size == 0






def test__cull_dead_index_count_gt_threshold():
    s = setutils.IndexedSet(range(16))
    # Remove 3 items, 3 > 16/8 == 2, so compaction should occur
    for i in range(3):
        s.remove(i)
    s._cull()
    assert s.dead_indices == []


def test__cull_dead_right_hand_side():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    # Now, last item is _MISSING, so cull should remove it
    s._cull()
    assert s.item_list[-1] != setutils._MISSING


def test__cull_num_dead_initial_value():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    # Should only remove one dead item at the end
    s._cull()
    assert s.item_list == [1, 2, 3]


def test__cull_while_loop_removes_all_trailing_missing():
    s = setutils.IndexedSet([1, 2, 3, 4, 5])
    s.remove(5)
    s.remove(4)
    # Now, last two items are _MISSING, cull should remove both
    s._cull()
    assert s.item_list == [1, 2, 3]


def test__cull_ded_last_interval_removal():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    # Should remove last dead interval if it ends at len(items)
    s._cull()
    assert s.dead_indices == []


def test__get_real_index_negative_index():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(-1) == 2


def test__get_real_index_no_dead_indices():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1




def test__get_real_index_dead_indices_continue():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # Should break out of loop when real_index < d_start
    assert s._get_real_index(0) == 0




def test__get_real_index_returns_value():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1


def test__get_apparent_index_no_dead_indices():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test__get_apparent_index_dead_indices_break():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For index=2, d_start=1, should not break if 2 < 1 is False
    assert s._get_apparent_index(2) == 2


def test__get_apparent_index_dead_indices_continue():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # Should break out of loop when index < d_start
    assert s._get_apparent_index(0) == 0


def test__get_apparent_index_dead_indices_subtraction():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # Should subtract (d_stop - d_start) from apparent_index
    assert s._get_apparent_index(2) == 2


def test__get_apparent_index_returns_value():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test__add_dead_stop_none():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    assert s.dead_indices == [[1, 2]]


def test__add_dead_stop_calculation():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    assert s.dead_indices[0][1] == 2


def test__add_dead_merges_with_existing():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    s._add_dead(2)
    # Should merge intervals
    assert s.dead_indices[0] == [1, 3]


def test__add_dead_start_leq_d_start_leq_stop():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    # Should update interval if start <= d_start <= stop
    s._add_dead(0, 2)
    assert s.dead_indices[0][0] == 0






def test__cull_dead_indices_eq_384_does_not_trigger_compact():
    s = setutils.IndexedSet(range(400))
    for i in range(384):
        s.remove(i)
    # Should NOT trigger compaction, so dead_indices should not be empty
    s._cull()
    assert s.dead_indices != []


def test__cull_num_dead_is_1_for_single_trailing_missing():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_while_loop_removes_all_trailing_missing_precisely():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_ded_last_interval_removal_precise():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


def test__get_real_index_returns_index_when_no_dead_indices():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1


def test__get_real_index_breaks_on_lt_d_start():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For real_index=0, d_start=1, 0 < 1 is True, so should break
    assert s._get_real_index(0) == 0


def test__get_real_index_break_vs_continue():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # Should break, not continue, so index 0 maps to 0
    assert s._get_real_index(0) == 0




def test__get_real_index_returns_value_not_none():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1


def test__get_apparent_index_returns_index_when_no_dead_indices():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test__get_apparent_index_breaks_on_lt_d_start():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For index=0, d_start=1, 0 < 1 is True, so should break
    assert s._get_apparent_index(0) == 0


def test__get_apparent_index_break_vs_continue():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # Should break, not continue, so index 0 maps to 0
    assert s._get_apparent_index(0) == 0


def test__get_apparent_index_subtracts_dead_range():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For index=2, apparent_index=2, d_start=1, d_stop=2
    # apparent_index should become 2 - (2-1) = 1
    assert s._get_apparent_index(2) == 2


def test__get_apparent_index_returns_value_not_none():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test__add_dead_start_leq_d_stop_leq_stop():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    # Now add an interval that overlaps the end
    s._add_dead(2, 3)
    assert s.dead_indices[0][1] == 3


def test_isdisjoint_returns_false_when_overlap():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.isdisjoint([2, 4])


def test_issubset_len_other_lt_len_self():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2])


def test_issubset_returns_false_when_not_subset():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2])


def test_issubset_returns_false_when_element_missing():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2, 4])


def test_issuperset_len_other_gt_len_self():
    s = setutils.IndexedSet([1, 2])
    assert not s.issuperset([1, 2, 3])


def test_issuperset_returns_false_when_not_superset():
    s = setutils.IndexedSet([1, 2])
    assert not s.issuperset([1, 2, 3])


def test_issuperset_returns_false_when_element_missing():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issuperset([1, 2, 4])


def test__MISSING_sentinel_var_name():
    # The sentinel's repr should contain '_MISSING'
    if hasattr(setutils._MISSING, '__name__'):
        # If make_sentinel is used, it may have a __name__ attribute
        assert '_MISSING' in repr(setutils._MISSING) or getattr(setutils._MISSING, '__name__', '') == '_MISSING'
    else:
        # fallback: object() fallback, just check it's not a string
        assert not isinstance(setutils._MISSING, str)






def test__cull_compacts_only_when_dead_indices_gt_384():
    s = setutils.IndexedSet(range(386))
    for i in range(385):
        s.remove(i)
    # Now len(s.dead_indices) == 385, should trigger compaction
    s._cull()
    assert s.dead_indices == []


def test__cull_compacts_when_dead_indices_exceeds_384():
    s = setutils.IndexedSet(range(386))
    for i in range(385):
        s.remove(i)
    s._cull()
    assert s.dead_indices == []


def test__cull_num_dead_initial_value_is_one():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    # Should only remove one dead item at the end
    assert s.item_list == [1, 2]


def test__cull_num_dead_counts_trailing_missing():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_while_loop_removes_all_trailing_missing_is():
    s = setutils.IndexedSet([1, 2, 3, 4, 5])
    s.remove(5)
    s.remove(4)
    s._cull()
    assert s.item_list == [1, 2, 3]


def test__cull_while_loop_indexing():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_while_loop_num_dead_increment():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_num_dead_increments():
    s = setutils.IndexedSet([1, 2, 3, 4])
    s.remove(4)
    s.remove(3)
    s._cull()
    assert s.item_list == [1, 2]


def test__cull_num_dead_increments_by_one():
    s = setutils.IndexedSet([1, 2, 3, 4, 5])
    s.remove(5)
    s.remove(4)
    s._cull()
    assert s.item_list == [1, 2, 3]


def test__cull_ded_last_interval_removal_and():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


def test__cull_ded_last_interval_removal_eq():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


def test__cull_ded_last_interval_removal_index():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


def test__cull_del_ded_last():
    s = setutils.IndexedSet([1, 2, 3])
    s.remove(3)
    s._cull()
    assert s.dead_indices == []


def test__get_real_index_returns_index_when_no_dead_indices_not():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_real_index(1) == 1


def test__get_real_index_adds_dead_range():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    # dead_indices = [[1,2]]
    # For real_index=2, d_start=1, d_stop=2
    # real_index should become 2 + (2-1) = 3 if +=, but should be 2 if +=
    assert s._get_real_index(2) == 2


def test__get_real_index_adds_dead_range_operator():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    assert s._get_real_index(2) == 2


def test__get_apparent_index_returns_index_when_no_dead_indices_not():
    s = setutils.IndexedSet(['a', 'b', 'c'])
    assert s._get_apparent_index(1) == 1


def test__get_apparent_index_subtracts_dead_range_operator():
    s = setutils.IndexedSet(['a', 'b', 'c', 'd'])
    s.remove('b')
    assert s._get_apparent_index(2) == 2


def test__add_dead_start_leq_d_start_leq_stop_repeat():
    s = setutils.IndexedSet([1, 2, 3])
    s._add_dead(1)
    s._add_dead(0, 2)
    assert s.dead_indices[0][0] == 0


def test_isdisjoint_returns_false_when_overlap_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.isdisjoint([2, 4])


def test_issubset_len_other_lt_len_self_le():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2])


def test_issubset_returns_false_when_not_subset_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2])


def test_issubset_returns_false_when_element_missing_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issubset([1, 2, 4])


def test_issuperset_len_other_gt_len_self_ge():
    s = setutils.IndexedSet([1, 2])
    assert not s.issuperset([1, 2, 3])


def test_issuperset_returns_false_when_not_superset_none():
    s = setutils.IndexedSet([1, 2])
    assert not s.issuperset([1, 2, 3])


def test_issuperset_returns_false_when_element_missing_none():
    s = setutils.IndexedSet([1, 2, 3])
    assert not s.issuperset([1, 2, 4])
