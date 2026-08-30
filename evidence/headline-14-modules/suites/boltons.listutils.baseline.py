import pytest
import listutils

from math import log as math_log

BarrelList = listutils.BarrelList
BList = listutils.BList
SplayList = listutils.SplayList

def test_barrellist_init_and_len():
    bl = BarrelList()
    assert isinstance(bl, BarrelList)
    assert len(bl) == 0
    assert bl.lists == [[]]

    bl2 = BarrelList([1, 2, 3])
    assert list(bl2) == [1, 2, 3]
    assert len(bl2) == 3

def test_barrellist_append_and_extend():
    bl = BarrelList()
    bl.append(1)
    bl.append(2)
    assert list(bl) == [1, 2]
    bl.extend([3, 4])
    assert list(bl) == [1, 2, 3, 4]

def test_barrellist_insert_and_balance():
    bl = BarrelList()
    for i in range(10):
        bl.append(i)
    bl.insert(5, 100)
    assert bl[5] == 100
    assert list(bl)[:6] == [0, 1, 2, 3, 4, 100]

def test_barrellist_pop_default_and_index():
    bl = BarrelList([1, 2, 3, 4])
    val = bl.pop()
    assert val == 4
    assert list(bl) == [1, 2, 3]
    val2 = bl.pop(0)
    assert val2 == 1
    assert list(bl) == [2, 3]

def test_barrellist_pop_negative_index():
    bl = BarrelList([10, 20, 30])
    val = bl.pop(-1)
    assert val == 30
    assert list(bl) == [10, 20]

def test_barrellist_contains():
    bl = BarrelList([1, 2, 3])
    assert 2 in bl
    assert 4 not in bl

def test_barrellist_getitem_and_setitem():
    bl = BarrelList([10, 20, 30])
    assert bl[1] == 20
    bl[1] = 99
    assert bl[1] == 99

def test_barrellist_getitem_slice():
    bl = BarrelList(range(10))
    s = bl[2:5]
    assert isinstance(s, BarrelList)
    assert list(s) == [2, 3, 4]

def test_barrellist_setitem_slice():
    bl = BarrelList([1, 2, 3, 4, 5])
    bl[1:4] = [20, 30]
    assert list(bl) == [1, 20, 30, 5]

def test_barrellist_delitem_and_delitem_slice():
    bl = BarrelList([1, 2, 3, 4, 5])
    del bl[1]
    assert list(bl) == [1, 3, 4, 5]
    del bl[1:3]
    assert list(bl) == [1, 5]

def test_barrellist_iter_and_reversed():
    bl = BarrelList([1, 2, 3])
    assert list(iter(bl)) == [1, 2, 3]
    assert list(reversed(bl)) == [3, 2, 1]

def test_barrellist_count_and_index():
    bl = BarrelList([1, 2, 2, 3, 2])
    assert bl.count(2) == 3
    assert bl.index(3) == 3
    with pytest.raises(ValueError):
        bl.index(99)

def test_barrellist_repr():
    bl = BarrelList([1, 2, 3])
    r = repr(bl)
    assert r.startswith("BarrelList([1, 2, 3])")

def test_barrellist_sort_and_reverse():
    bl = BarrelList([3, 1, 2])
    bl.sort()
    assert list(bl) == [1, 2, 3]
    bl.reverse()
    assert list(bl) == [3, 2, 1]

def test_barrellist_from_iterable():
    bl = BarrelList.from_iterable([1, 2, 3])
    assert isinstance(bl, BarrelList)
    assert list(bl) == [1, 2, 3]

def test_barrellist_iter_slice():
    bl = BarrelList(range(10))
    it = bl.iter_slice(2, 7)
    assert list(it) == [2, 3, 4, 5, 6]

def test_barrellist_del_slice():
    bl = BarrelList([0, 1, 2, 3, 4, 5])
    bl.del_slice(2, 5)
    assert list(bl) == [0, 1, 5]


def test_barrellist_getslice_and_setslice():
    bl = BarrelList([1, 2, 3, 4, 5])
    s = bl.__getslice__(1, 4)
    assert list(s) == [2, 3, 4]
    bl.__setslice__(1, 3, [20, 30])
    assert list(bl) == [1, 20, 30, 4, 5]

def test_barrellist_translate_index_negative():
    bl = BarrelList([1, 2, 3])
    idx, rel = bl._translate_index(-1)
    assert (idx, rel) == (0, 2)


def test_barrellist_balance_list_noop():
    bl = BarrelList([1, 2, 3])
    # Should not split, returns False
    assert bl._balance_list(0) is False



def test_barrellist_slice_negative_indices():
    bl = BarrelList([1, 2, 3, 4, 5])
    s = bl[-3:-1]
    assert list(s) == [3, 4]

def test_barrellist_slice_with_step():
    bl = BarrelList([0, 1, 2, 3, 4, 5])
    s = bl[1:5:2]
    assert list(s) == [1, 3]

def test_barrellist_setitem_slice_multiple_lists():
    bl = BarrelList(range(100))
    # Force multiple sublists
    bl.lists = [list(range(50)), list(range(50, 100))]
    bl[10:90] = [0] * 80
    assert list(bl)[10:90] == [0] * 80

def test_barrellist_setitem_index_multiple_lists():
    bl = BarrelList(range(100))
    bl.lists = [list(range(50)), list(range(50, 100))]
    bl[55] = 999
    assert bl[55] == 999

def test_barrellist_reverse_multiple_lists():
    bl = BarrelList(range(10))
    bl.lists = [list(range(5)), list(range(5, 10))]
    bl.reverse()
    assert list(bl) == list(range(9, -1, -1))

def test_blist_is_barrellist():
    bl = BList([1, 2, 3])
    assert isinstance(bl, BarrelList)
    assert list(bl) == [1, 2, 3]

def test_splaylist_shift_and_swap():
    sl = SplayList([1, 2, 3, 4])
    sl.shift(2, 0)
    assert list(sl) == [3, 1, 2, 4]
    sl.swap(0, 3)
    assert list(sl) == [4, 1, 2, 3]

def test_splaylist_shift_noop():
    sl = SplayList([1, 2, 3])
    sl.shift(1, 1)
    assert list(sl) == [1, 2, 3]

def test_splaylist_swap():
    sl = SplayList([1, 2, 3])
    sl.swap(0, 2)
    assert list(sl) == [3, 2, 1]