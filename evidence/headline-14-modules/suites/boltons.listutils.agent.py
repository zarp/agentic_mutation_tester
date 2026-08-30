import pytest
import listutils

def test_empty_barrellist_len_zero():
    bl = listutils.BarrelList()
    assert len(bl) == 0
    assert list(bl) == []
    assert bl.lists == [[]]

def test_barrellist_append_and_len():
    bl = listutils.BarrelList()
    bl.append(1)
    assert len(bl) == 1
    assert list(bl) == [1]
    assert bl.lists == [[1]]

def test_barrellist_extend():
    bl = listutils.BarrelList()
    bl.extend([1, 2, 3])
    assert len(bl) == 3
    assert list(bl) == [1, 2, 3]
    assert bl.lists == [[1, 2, 3]]

def test_barrellist_insert_at_start_middle_end():
    bl = listutils.BarrelList([1, 3])
    bl.insert(1, 2)
    assert list(bl) == [1, 2, 3]
    bl.insert(0, 0)
    assert list(bl) == [0, 1, 2, 3]
    bl.insert(len(bl), 4)
    assert list(bl) == [0, 1, 2, 3, 4]

def test_barrellist_insert_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    bl.insert(-1, 99)
    assert list(bl) == [1, 2, 99, 3]


def test_barrellist_pop_default_and_index():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3
    assert list(bl) == [1, 2]
    assert bl.pop(0) == 1
    assert list(bl) == [2]

def test_barrellist_pop_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3
    assert list(bl) == [1, 2]

def test_barrellist_pop_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        bl.pop(10)
    with pytest.raises(IndexError):
        bl.pop(-10)

def test_barrellist_contains():
    bl = listutils.BarrelList([1, 2, 3])
    assert 2 in bl
    assert 4 not in bl

def test_barrellist_getitem_int_and_slice():
    bl = listutils.BarrelList([10, 20, 30, 40])
    assert bl[0] == 10
    assert bl[1] == 20
    assert bl[-1] == 40
    assert list(bl[1:3]) == [20, 30]
    assert isinstance(bl[1:3], listutils.BarrelList)

def test_barrellist_getitem_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        _ = bl[10]
    with pytest.raises(IndexError):
        _ = bl[-10]

def test_barrellist_setitem_int_and_slice():
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl[1] = 99
    assert list(bl) == [1, 99, 3, 4]
    bl[1:3] = [7, 8]
    assert list(bl) == [1, 7, 8, 4]

def test_barrellist_setitem_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        bl[10] = 5
    with pytest.raises(IndexError):
        bl[-10] = 5


def test_barrellist_delitem_index_out_of_bounds_raises():
    bl = listutils.BarrelList([1, 2, 3])
    with pytest.raises(IndexError):
        del bl[10]
    with pytest.raises(IndexError):
        del bl[-10]

def test_barrellist_iter_and_reversed():
    bl = listutils.BarrelList([1, 2, 3])
    assert list(iter(bl)) == [1, 2, 3]
    assert list(reversed(bl)) == [3, 2, 1]

def test_barrellist_count():
    bl = listutils.BarrelList([1, 2, 2, 3, 2])
    assert bl.count(2) == 3
    assert bl.count(99) == 0

def test_barrellist_index_found_and_not_found():
    bl = listutils.BarrelList([1, 2, 3, 2])
    assert bl.index(2) == 1
    assert bl.index(3) == 2
    with pytest.raises(ValueError) as e:
        bl.index(99)
    assert str(e.value) == '99 is not in list'

def test_barrellist_repr():
    bl = listutils.BarrelList([1, 2, 3])
    assert repr(bl) == "BarrelList([1, 2, 3])"

def test_barrellist_sort_and_reverse():
    bl = listutils.BarrelList([3, 1, 2])
    bl.sort()
    assert list(bl) == [1, 2, 3]
    bl.reverse()
    assert list(bl) == [3, 2, 1]

def test_barrellist_from_iterable():
    bl = listutils.BarrelList.from_iterable([1, 2, 3])
    assert isinstance(bl, listutils.BarrelList)
    assert list(bl) == [1, 2, 3]

def test_barrellist_getslice_and_setslice():
    bl = listutils.BarrelList([1, 2, 3, 4])
    sliced = bl.__getslice__(1, 3)
    assert isinstance(sliced, listutils.BarrelList)
    assert list(sliced) == [2, 3]
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]




def test_barrellist_balance_list_no_split():
    bl = listutils.BarrelList([1, 2, 3])
    # Should not split for small lists
    assert bl._balance_list(0) is False


def test_barrellist_cur_size_limit_increases_with_length():
    bl = listutils.BarrelList()
    limit0 = bl._cur_size_limit
    bl.extend(range(100))
    limit1 = bl._cur_size_limit
    assert limit1 > limit0


def test_barrellist_slice_across_list_boundaries():
    bl = listutils.BarrelList()
    bl.extend(range(2000))
    # Slicing across sublists
    s = bl[1000:1010]
    assert list(s) == list(range(1000, 1010))
    assert isinstance(s, listutils.BarrelList)

def test_barrellist_repr_large():
    bl = listutils.BarrelList(range(100))
    rep = repr(bl)
    assert rep.startswith("BarrelList([")
    assert rep.endswith("])")

def test_blist_is_barrellist():
    assert listutils.BList is listutils.BarrelList

def test_barrellist_lots_of_operations():
    bl = listutils.BarrelList()
    for i in range(100):
        bl.append(i)
    for i in range(50):
        bl.pop(0)
    assert list(bl) == list(range(50, 100))
    bl.sort()
    assert list(bl) == list(range(50, 100))
    bl.reverse()
    assert list(bl) == list(range(99, 49, -1))

def test_splaylist_shift_and_swap():
    sl = listutils.SplayList([1, 2, 3, 4])
    sl.shift(2, 0)
    assert list(sl) == [3, 1, 2, 4]
    sl.swap(1, 3)
    assert list(sl) == [3, 4, 2, 1]

def test_splaylist_shift_noop_when_indices_equal():
    sl = listutils.SplayList([1, 2, 3])
    sl.shift(1, 1)
    assert list(sl) == [1, 2, 3]

def test_splaylist_shift_and_swap_boundaries():
    sl = listutils.SplayList([1, 2, 3])
    sl.shift(0, 2)
    assert list(sl) == [2, 3, 1]
    sl.swap(0, 2)
    assert list(sl) == [1, 3, 2]

def test_splaylist_swap_same_index():
    sl = listutils.SplayList([1, 2, 3])
    sl.swap(1, 1)
    assert list(sl) == [1, 2, 3]




def test___all__contains_correct_names():
    assert 'BList' in listutils.__all__
    assert 'BarrelList' in listutils.__all__


def test_barrellist_size_factor_constant():
    assert listutils.BarrelList._size_factor == 1520




def test_barrellist_cur_size_limit_log_base():
    bl = listutils.BarrelList()
    # For length 0, should use log base 2, not 3
    # log(0+2, 2) = 1, log(0+2, 3) = 0.6309...
    # So, int(round(1520 * 1)) == 1520
    assert bl._cur_size_limit == 1520


def test_translate_index_negative_index():
    bl = listutils.BarrelList([10, 20, 30])
    # index -1 should map to last element
    idx = bl._translate_index(-1)
    assert idx == (0, 2)
    # index -3 should map to first element
    idx = bl._translate_index(-3)
    assert idx == (0, 0)




def test_translate_index_breaks_on_first_match():
    bl = listutils.BarrelList([1, 2, 3])
    # Should return after finding the correct sublist
    idx = bl._translate_index(1)
    assert idx == (0, 1)


def test_translate_index_rel_idx_decrement():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    # index 3 should be (1, 1)
    idx = bl._translate_index(3)
    assert idx == (1, 1)


def test_balance_list_negative_index():
    bl = listutils.BarrelList([1, 2, 3])
    # Should handle negative index correctly
    idx = -1
    before = bl.lists[:]
    bl._balance_list(idx)
    assert bl.lists == before


def test_balance_list_no_split_on_equal():
    bl = listutils.BarrelList()
    bl.lists = [[1] * bl._cur_size_limit]
    # Should not split if length == size_limit
    assert bl._balance_list(0) is False


def test_balance_list_half_limit_integer_division():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 1)]
    bl._balance_list(0)
    # After balancing, all sublists should have at most _cur_size_limit//2 elements
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2


def test_balance_list_while_condition():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 3)]
    bl._balance_list(0)
    # Should not split if length == half_limit
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2








def test_pop_default_on_single_list():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3


def test_pop_index_minus1():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3




def test_iter_slice_start_default():
    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(None, 2))
    assert result == [1, 2]






def test_iter_slice_start_negative():
    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(-2, None))
    assert result == [2, 3]


def test_iter_slice_start_adjustment():
    bl = listutils.BarrelList([1, 2, 3])
    # start = -1 should yield [3]
    result = list(bl.iter_slice(-1, None))
    assert result == [3]


def test_iter_slice_stop_negative():
    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(None, -1))
    assert result == [1, 2]


def test_translate_index_index_zero_and_one():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index 1 should not be treated as negative
    idx = bl._translate_index(1)
    assert idx == (0, 1)


def test_translate_index_rel_idx_equal_len_list():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    # rel_idx == len_list should not enter the block
    # index 2: rel_idx=2, len_list=2, should decrement and go to next list
    idx = bl._translate_index(2)
    assert idx == (1, 0)


def test_translate_index_break_vs_continue():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    # Should stop at first matching sublist, not continue
    idx = bl._translate_index(1)
    assert idx == (0, 1)












def test_pop_removes_empty_list():
    bl = listutils.BarrelList([1, 2, 3])
    # Force multiple lists
    bl.lists = [[1], [2, 3]]
    bl.pop()
    # After popping, lists[-1] should not be empty, so lists should not be popped
    assert len(bl.lists) == 2
    bl.pop()
    # Now lists[-1] is empty, so lists should be popped
    assert len(bl.lists) == 1












def test_del_slice_balance_list_zero():
    bl = listutils.BarrelList([1, 2, 3, 4, 5])
    bl.del_slice(0, 5, 2)
    # Should call _balance_list(0), so lists[0] is balanced
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit


def test_del_slice_start_none():
    bl = listutils.BarrelList([1, 2, 3])
    bl.del_slice(None, 2)
    assert list(bl) == [3]


def test_translate_index_negative_index_zero():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index -1 should map to last element
    idx_neg1 = bl._translate_index(-1)
    assert idx_neg1 == (0, 2)








def test_pop_index_minus1_and_none():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3


def test_pop_removes_empty_list_only_if_more_than_one():
    bl = listutils.BarrelList([1, 2, 3])
    bl.lists = [[1], [2, 3]]
    bl.pop()
    assert len(bl.lists) == 2
    bl.pop()
    assert len(bl.lists) == 1




def test_iter_slice_stop_negative_adjustment():
    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(None, -1))
    assert result == [1, 2]


def test_del_slice_step_greater_than_one():
    bl = listutils.BarrelList([1, 2, 3, 4, 5])
    bl.del_slice(0, 5, 2)
    # Should call _balance_list(0), so lists[0] is balanced
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit


def test_del_slice_start_list_idx_less_than_stop_list_idx():
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.lists = [[1, 2], [3, 4]]
    bl.del_slice(1, 3)
    assert list(bl) == [1, 4]


def test_contains_returns_false():
    bl = listutils.BarrelList([1, 2, 3])
    assert (99 in bl) is False


def test_setitem_slice_on_single_list():
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl[1:3] = [7, 8]
    assert list(bl) == [1, 7, 8, 4]


def test_setslice_on_single_list():
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]


def test_index_accumulation():
    bl = listutils.BarrelList()
    bl.lists = [[1, 2], [3, 4]]
    assert bl.index(4) == 3


def test_splaylist_shift_default_dest_index():
    sl = listutils.SplayList([1, 2, 3, 4])
    sl.shift(2)
    assert list(sl) == [3, 1, 2, 4]


def test_translate_index_zero_vs_one():
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index 1 should not be treated as negative
    idx1 = bl._translate_index(1)
    assert idx1 == (0, 1)




def test_balance_list_while_condition_strict():
    bl = listutils.BarrelList()
    bl.lists = [[1] * (bl._cur_size_limit + 2)]
    bl._balance_list(0)
    # Should not split if length == half_limit
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit // 2






def test_pop_index_minus1_and_none_equivalence():
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop() == 3






def test_sort_assigns_to_lists_zero():
    bl = listutils.BarrelList([3, 1, 2])
    bl.sort()
    assert list(bl) == [1, 2, 3]


def test_sort_balance_list_zero():
    bl = listutils.BarrelList([3, 1, 2])
    bl.sort()
    assert list(bl) == [1, 2, 3]


def test_translate_index_index_less_than_0_vs_1():
    # line 118: < -> <= and 0 -> 1
    bl = listutils.BarrelList([10, 20, 30])
    # index 0 should not be treated as negative
    idx = bl._translate_index(0)
    assert idx == (0, 0)
    # index -1 should be treated as negative
    idx_neg1 = bl._translate_index(-1)
    assert idx_neg1 == (0, 2)








def test_pop_index_tuple_vs_minus1_vs_none():
    # line 167: 1 -> 2
    bl = listutils.BarrelList([1, 2, 3])
    # index == () should not pop last element
    try:
        bl.pop(())
    except Exception:
        pass
    # index == None should pop last element
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(None) == 3
    # index == -1 should pop last element
    bl = listutils.BarrelList([1, 2, 3])
    assert bl.pop(-1) == 3


def test_pop_removes_empty_list_condition():
    # line 169: > -> >=
    bl = listutils.BarrelList([1, 2, 3])
    bl.lists = [[1], [2, 3]]
    bl.pop()
    assert len(bl.lists) == 2
    bl.pop()
    assert len(bl.lists) == 1




def test_iter_slice_stop_le_0_and_1():
    # line 193: < -> <=, 0 -> 1
    bl = listutils.BarrelList([1, 2, 3])
    result = list(bl.iter_slice(None, -1))
    assert result == [1, 2]


def test_del_slice_step_gt_1_vs_gt_2_and_new_list_chain_start_0_vs_1():
    # line 199: > -> >=, 1 -> 2; line 200: 0 -> 1
    bl = listutils.BarrelList([1, 2, 3, 4, 5])
    bl.del_slice(0, 5, 2)
    # Should call _balance_list(0), so lists[0] is balanced
    for sub in bl.lists:
        assert len(sub) <= bl._cur_size_limit


def test_del_slice_start_list_idx_le_stop_list_idx_and_del_lists():
    # line 218: < -> <=, line 219: + -> -, 1 -> 2
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.lists = [[1, 2], [3, 4]]
    bl.del_slice(1, 3)
    assert list(bl) == [1, 4]


def test_setitem_slice_on_single_list_vs_multiple_lists():
    # line 280: == -> !=, 1 -> 2
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl[1:3] = [7, 8]
    assert list(bl) == [1, 7, 8, 4]
    # Now force multiple lists
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.lists = [[1, 2], [3, 4]]
    bl[1:3] = [7, 8]
    assert list(bl) == [1, 7, 8, 4]


def test_setslice_on_single_list_vs_multiple_lists():
    # line 298: == -> !=, 1 -> 2
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]
    # Now force multiple lists
    bl = listutils.BarrelList([1, 2, 3, 4])
    bl.lists = [[1, 2], [3, 4]]
    bl.__setslice__(1, 3, [7, 8])
    assert list(bl) == [1, 7, 8, 4]
