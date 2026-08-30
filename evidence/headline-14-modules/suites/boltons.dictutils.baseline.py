import pytest
import dictutils

from collections.abc import KeysView, ValuesView, ItemsView

OMD = dictutils.OrderedMultiDict
MultiDict = dictutils.MultiDict
OneToOne = dictutils.OneToOne
ManyToMany = dictutils.ManyToMany
subdict = dictutils.subdict
FrozenDict = dictutils.FrozenDict

def test_omd_basic_add_and_get():
    omd = OMD()
    omd['a'] = 1
    omd['b'] = 2
    omd.add('a', 3)
    assert omd['a'] == 3
    assert omd['b'] == 2
    assert omd.get('a') == 3
    assert omd.getlist('a') == [1, 3]
    assert omd.getlist('b') == [2]
    assert omd.getlist('c') == []

def test_omd_addlist():
    omd = OMD([('a', -1)])
    omd.addlist('a', range(3))
    assert omd.getlist('a') == [-1, 0, 1, 2]
    omd.addlist('b', [])
    assert 'b' not in omd

def test_omd_setdefault():
    omd = OMD()
    assert omd.setdefault('a', 10) == 10
    assert omd['a'] == 10
    omd['b'] = 20
    assert omd.setdefault('b', 30) == 20

def test_omd_clear():
    omd = OMD([('a', 1), ('b', 2)])
    omd.clear()
    assert list(omd.items(multi=True)) == []
    assert len(omd) == 0

def test_omd_copy():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    omd2 = omd.copy()
    assert omd2 == omd
    omd2.add('c', 4)
    assert omd != omd2

def test_omd_fromkeys():
    omd = OMD.fromkeys(['a', 'b'], 42)
    assert omd['a'] == 42
    assert omd['b'] == 42
    assert omd.getlist('a') == [42]

def test_omd_update_and_update_extend():
    omd = OMD([('a', 1), ('b', 2)])
    omd2 = OMD([('a', 3), ('c', 4)])
    omd.update(omd2)
    assert omd['a'] == 3
    assert omd['b'] == 2
    assert omd['c'] == 4
    omd3 = OMD([('d', 5)])
    omd3.update_extend([('d', 6), ('e', 7)])
    assert omd3.getlist('d') == [5, 6]
    assert omd3.getlist('e') == [7]

def test_omd_setitem_and_delitem():
    omd = OMD()
    omd['a'] = 1
    omd['a'] = 2
    assert omd.getlist('a') == [2]
    del omd['a']
    assert 'a' not in omd

def test_omd_eq_and_ne():
    omd1 = OMD([('a', 1), ('b', 2)])
    omd2 = OMD([('a', 1), ('b', 2)])
    omd3 = OMD([('a', 1), ('b', 3)])
    assert omd1 == omd2
    assert omd1 != omd3
    assert omd1 != {'a': 1, 'b': 2, 'c': 3}
    assert omd1 == {'a': 1, 'b': 2}

def test_omd_pop_and_popall_and_poplast():
    omd = OMD([('a', 1), ('a', 2), ('b', 3)])
    assert omd.pop('a') == 2
    assert omd.getlist('a') == []
    omd.add('a', 4)
    omd.add('a', 5)
    assert omd.popall('a') == [4, 5]
    omd.add('x', 10)
    omd.add('y', 20)
    assert omd.poplast() == 20
    assert omd.poplast('x') == 10
    with pytest.raises(KeyError):
        omd.pop('notfound')
    assert omd.pop('notfound', 123) == 123

def test_omd_iter_methods():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    assert list(omd.iteritems(multi=True)) == [('a', 1), ('b', 2), ('a', 3)]
    assert list(omd.iteritems()) == [('a', 3), ('b', 2)]
    assert list(omd.iterkeys(multi=True)) == ['a', 'b', 'a']
    assert list(omd.iterkeys()) == ['a', 'b']
    assert list(omd.itervalues(multi=True)) == [1, 2, 3]
    assert list(omd.itervalues()) == [3, 2]

def test_omd_todict():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    d1 = omd.todict()
    d2 = omd.todict(multi=True)
    assert d1 == {'a': 3, 'b': 2}
    assert d2 == {'a': [1, 3], 'b': [2]}

def test_omd_sorted_and_sortedvalues():
    omd = OMD(zip(range(3), range(3)))
    omd2 = omd.sorted(reverse=True)
    assert list(omd2.items(multi=True)) == [(2, 2), (1, 1), (0, 0)]
    omd = OMD()
    omd.addlist('even', [6, 2])
    omd.addlist('odd', [1, 5])
    omd.add('even', 4)
    omd.add('odd', 3)
    somd = omd.sortedvalues()
    assert somd.getlist('even') == [2, 4, 6]
    assert somd.getlist('odd') == [1, 3, 5]
    assert somd.keys(multi=True) == omd.keys(multi=True)
    assert somd != omd

def test_omd_inverted_and_counts():
    omd = OMD([(0, 2), (1, 2)])
    inv = omd.inverted()
    assert inv.getlist(2) == [0, 1]
    assert inv.inverted() == omd
    omd = OMD([('a', 1), ('a', 2), ('b', 3)])
    counts = omd.counts()
    assert isinstance(counts, OMD)
    assert counts['a'] == 2
    assert counts['b'] == 1

def test_omd_keys_values_items_and_views():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    assert omd.keys() == ['a', 'b']
    assert omd.keys(multi=True) == ['a', 'b', 'a']
    assert omd.values() == [3, 2]
    assert omd.values(multi=True) == [1, 2, 3]
    assert omd.items() == [('a', 3), ('b', 2)]
    assert omd.items(multi=True) == [('a', 1), ('b', 2), ('a', 3)]
    assert isinstance(omd.viewkeys(), KeysView)
    assert isinstance(omd.viewvalues(), ValuesView)
    assert isinstance(omd.viewitems(), ItemsView)

def test_omd_iter_and_reversed():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    assert list(iter(omd)) == ['a', 'b']
    assert list(reversed(omd)) == ['b', 'a']

def test_omd_repr():
    omd = OMD([('a', 1), ('b', 2), ('a', 3)])
    s = repr(omd)
    assert s.startswith('OrderedMultiDict([')
    assert "('a', 1)" in s and "('b', 2)" in s and "('a', 3)" in s


def test_onetoone_basic_and_inv():
    oto = OneToOne({'a': 1, 'b': 2})
    assert oto['a'] == 1
    assert oto.inv[1] == 'a'
    oto.inv[1] = 'c'
    assert 'a' not in oto
    assert oto['c'] == 1
    assert oto.inv[1] == 'c'
    assert len(oto) == 2

def test_onetoone_unique_constructor():
    with pytest.raises(ValueError):
        OneToOne.unique({'a': 1, 'b': 1})
    d = {'a': 2}
    with pytest.raises(ValueError):
        OneToOne.unique(d, b=2)

def test_onetoone_setitem_and_delitem():
    oto = OneToOne({'a': 1, 'b': 2})
    oto['c'] = 3
    assert oto['c'] == 3
    assert oto.inv[3] == 'c'
    del oto['c']
    assert 'c' not in oto
    assert 3 not in oto.inv

def test_onetoone_clear_and_copy():
    oto = OneToOne({'a': 1, 'b': 2})
    oto2 = oto.copy()
    assert oto2 == oto
    oto.clear()
    assert len(oto) == 0
    assert len(oto.inv) == 0

def test_onetoone_pop_and_popitem_and_setdefault():
    oto = OneToOne({'a': 1, 'b': 2})
    assert oto.pop('a') == 1
    assert 'a' not in oto
    k, v = oto.popitem()
    assert (k, v) == ('b', 2)
    oto['x'] = 10
    assert oto.setdefault('y', 20) == 20
    assert oto['y'] == 20


def test_onetoone_repr():
    oto = OneToOne({'a': 1})
    s = repr(oto)
    assert s.startswith('OneToOne({')

def test_manytomany_basic_add_and_inv():
    m2m = ManyToMany()
    m2m.add('a', 1)
    m2m.add('a', 2)
    m2m.add('b', 2)
    assert m2m['a'] == frozenset([1, 2])
    assert m2m['b'] == frozenset([2])
    assert m2m.inv[2] == frozenset(['a', 'b'])
    assert m2m.inv[1] == frozenset(['a'])

def test_manytomany_setitem_and_delitem():
    m2m = ManyToMany()
    m2m['a'] = [1, 2]
    assert m2m['a'] == frozenset([1, 2])
    m2m['a'] = [2, 3]
    assert m2m['a'] == frozenset([2, 3])
    del m2m['a']
    assert 'a' not in m2m
    assert 2 not in m2m.inv.data or 'a' not in m2m.inv.data.get(2, set())

def test_manytomany_update_and_remove():
    m2m = ManyToMany()
    m2m.update([('a', 1), ('a', 2), ('b', 2)])
    m2m.remove('a', 1)
    assert m2m['a'] == frozenset([2])
    m2m.remove('a', 2)
    assert 'a' not in m2m

def test_manytomany_replace():
    m2m = ManyToMany()
    m2m.add('a', 1)
    m2m.add('a', 2)
    m2m.replace('a', 'b')
    assert 'a' not in m2m
    assert 'b' in m2m
    assert m2m['b'] == frozenset([1, 2])
    assert m2m.inv[1] == frozenset(['b'])

def test_manytomany_iter_and_eq():
    m2m = ManyToMany()
    m2m.add('a', 1)
    m2m.add('b', 2)
    items = list(m2m.iteritems())
    assert ('a', 1) in items and ('b', 2) in items
    m2m2 = ManyToMany()
    m2m2.add('a', 1)
    m2m2.add('b', 2)
    assert m2m == m2m2

def test_manytomany_repr():
    m2m = ManyToMany()
    m2m.add('a', 1)
    s = repr(m2m)
    assert s.startswith('ManyToMany([')

def test_subdict_basic():
    d = {'a': 1, 'b': 2, 'c': 3}
    assert subdict(d) == d
    assert subdict(d, drop=['b', 'c']) == {'a': 1}
    assert subdict(d, keep=['a', 'c']) == {'a': 1, 'c': 3}
    assert subdict(d, keep=['a', 'c'], drop=['c']) == {'a': 1}

def test_frozendict_basic_and_hash():
    fd = FrozenDict({'a': 1, 'b': 2})
    assert fd['a'] == 1
    assert isinstance(hash(fd), int)
    fd2 = fd.updated({'c': 3})
    assert fd2['c'] == 3
    assert fd2['a'] == 1
    assert fd != fd2

def test_frozendict_fromkeys_and_repr():
    fd = FrozenDict.fromkeys(['a', 'b'], 42)
    assert fd['a'] == 42
    assert fd['b'] == 42
    s = repr(fd)
    assert s.startswith('FrozenDict({')

def test_frozendict_reduce_and_copy():
    fd = FrozenDict({'a': 1})
    t, args = fd.__reduce_ex__(2)
    assert t is FrozenDict
    assert args == ({'a': 1},)
    assert fd.__copy__() is fd

def test_frozendict_immutable_methods():
    fd = FrozenDict({'a': 1})
    with pytest.raises(TypeError):
        fd['b'] = 2
    with pytest.raises(TypeError):
        fd.update({'b': 2})
    with pytest.raises(TypeError):
        fd.setdefault('b', 2)
    with pytest.raises(TypeError):
        fd.pop('a')
    with pytest.raises(TypeError):
        fd.popitem()
    with pytest.raises(TypeError):
        fd.clear()
    with pytest.raises(TypeError):
        fd |= {'c': 3}

def test_frozendict_unhashable_value():
    fd = FrozenDict({'a': []})
    with pytest.raises(TypeError):
        hash(fd)