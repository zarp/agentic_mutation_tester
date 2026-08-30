import pytest
import namedutils

import sys

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_basic_creation_and_access(factory):
    Point = factory('Point', ['x', 'y'])
    p = Point(1, 2)
    # Index access
    assert p[0] == 1
    assert p[1] == 2
    # Attribute access
    assert p.x == 1
    assert p.y == 2
    # Unpacking
    x, y = p
    assert (x, y) == (1, 2)
    # _fields attribute
    assert p._fields == ('x', 'y')
    # __repr__ format
    assert repr(p) == "Point(x=1, y=2)"
    # _asdict
    d = p._asdict()
    assert d == {'x': 1, 'y': 2}
    # _make from iterable
    p2 = Point._make([3, 4])
    assert p2.x == 3 and p2.y == 4
    # _replace
    p3 = p._replace(x=10)
    assert p3.x == 10 and p3.y == 2
    # _replace with unknown field
    with pytest.raises(ValueError):
        p._replace(z=5)
    # _asdict returns OrderedDict or dict
    assert list(d.keys()) == ['x', 'y']
    # __dict__ property
    assert p.__dict__ == d

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_kwargs_instantiation(factory):
    Point = factory('Point', ['x', 'y'])
    p = Point(x=5, y=6)
    assert p.x == 5
    assert p.y == 6

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_make_wrong_length(factory):
    Point = factory('Point', ['x', 'y'])
    with pytest.raises(TypeError):
        Point._make([1])  # too short
    with pytest.raises(TypeError):
        Point._make([1, 2, 3])  # too long

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_duplicate_field_names(factory):
    with pytest.raises(ValueError):
        factory('Point', ['x', 'x'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_name_starts_with_underscore(factory):
    with pytest.raises(ValueError):
        factory('Point', ['_x', 'y'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_name_is_keyword(factory):
    with pytest.raises(ValueError):
        factory('Point', ['for', 'y'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_name_starts_with_digit(factory):
    with pytest.raises(ValueError):
        factory('Point', ['1x', 'y'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_name_invalid_characters(factory):
    with pytest.raises(ValueError):
        factory('Point', ['x$', 'y'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_type_name_invalid(factory):
    with pytest.raises(ValueError):
        factory('1Point', ['x', 'y'])
    with pytest.raises(ValueError):
        factory('for', ['x', 'y'])
    with pytest.raises(ValueError):
        factory('Point$', ['x', 'y'])

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_names_as_string(factory):
    Point = factory('Point', 'x y')
    p = Point(1, 2)
    assert p.x == 1 and p.y == 2
    Point2 = factory('Point2', 'x, y')
    p2 = Point2(3, 4)
    assert p2.x == 3 and p2.y == 4

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_field_names_rename(factory):
    # Should rename invalid names to _0, _1, etc.
    Point = factory('Point', ['x', 'for', 'x', '_foo', '1bar'], rename=True)
    p = Point(1, 2, 3, 4, 5)
    # The field names should be: x, _1, _2, _3, _4
    assert p._fields == ('x', '_1', '_2', '_3', '_4')
    assert p.x == 1
    assert getattr(p, '_1') == 2
    assert getattr(p, '_2') == 3
    assert getattr(p, '_3') == 4
    assert getattr(p, '_4') == 5

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_asdict_is_ordered(factory):
    # Order should be preserved
    Point = factory('Point', ['a', 'b', 'c'])
    p = Point(1, 2, 3)
    d = p._asdict()
    assert list(d.keys()) == ['a', 'b', 'c']

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_getnewargs(factory):
    Point = factory('Point', ['x', 'y'])
    p = Point(1, 2)
    args = p.__getnewargs__()
    assert args == (1, 2)

@pytest.mark.parametrize("factory", [namedutils.namedtuple, namedutils.namedlist])
def test_repr_inheritance(factory):
    # Subclass and check __repr__ still works
    Point = factory('Point', ['x', 'y'])
    class MyPoint(Point):
        pass
    p = MyPoint(1, 2)
    assert repr(p) == "MyPoint(x=1, y=2)"

def test_namedlist_mutability():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    # Attribute access
    assert p.x == 1
    p.x = 10
    assert p.x == 10
    # Index access
    p[1] = 20
    assert p.y == 20
    # List methods
    p.append(30)
    assert p[2] == 30
    # _fields should not include appended value
    assert p._fields == ('x', 'y')
    # _asdict should only include fields
    d = p._asdict()
    assert d == {'x': 10, 'y': 20}

def test_namedtuple_immutable():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    with pytest.raises(AttributeError):
        p.x = 10
    with pytest.raises(TypeError):
        p[0] = 10

def test_namedlist_replace_and_make():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    p2 = p._replace(x=100)
    assert isinstance(p2, Point)
    assert p2.x == 100 and p2.y == 2
    # _make with correct length
    p3 = Point._make([5, 6])
    assert p3.x == 5 and p3.y == 6
    # _make with wrong length
    with pytest.raises(TypeError):
        Point._make([1])
    with pytest.raises(TypeError):
        Point._make([1, 2, 3])

def test_namedlist_setattr_and_delattr():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    # setattr
    p.x = 42
    assert p.x == 42
    # delattr should raise AttributeError
    with pytest.raises(AttributeError):
        del p.x

def test_namedtuple_make_from_dict():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    d = {'x': 7, 'y': 8}
    p = Point(**d)
    assert p.x == 7 and p.y == 8

def test_namedlist_make_from_dict():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    d = {'x': 7, 'y': 8}
    p = Point(**d)
    assert p.x == 7 and p.y == 8

def test_namedtuple_repr_with_inheritance():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    class SubPoint(Point):
        pass
    p = SubPoint(1, 2)
    assert repr(p) == "SubPoint(x=1, y=2)"

def test_namedlist_repr_with_inheritance():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    class SubPoint(Point):
        pass
    p = SubPoint(1, 2)
    assert repr(p) == "SubPoint(x=1, y=2)"

def test_namedtuple_slots():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    assert hasattr(Point, '__slots__')
    assert Point.__slots__ == ()

def test_namedlist_slots():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    assert hasattr(Point, '__slots__')
    assert Point.__slots__ == ()

def test_namedtuple_module_set():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    assert Point.__module__ == __name__

def test_namedlist_module_set():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    assert Point.__module__ == __name__

def test_namedtuple_asdict_is_property():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p.__dict__, dict)
    assert p.__dict__ == {'x': 1, 'y': 2}

def test_namedlist_asdict_is_property():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p.__dict__, dict)
    assert p.__dict__ == {'x': 1, 'y': 2}

def test_namedtuple_getstate_is_none():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert p.__getstate__() is None

def test_namedlist_getstate_is_none():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    assert p.__getstate__() is None

def test_namedtuple_verbose_prints(capsys):
    Point = namedutils.namedtuple('Point', ['x', 'y'], verbose=True)
    captured = capsys.readouterr()
    assert "class Point(tuple):" in captured.out

def test_namedlist_verbose_prints(capsys):
    Point = namedutils.namedlist('Point', ['x', 'y'], verbose=True)
    captured = capsys.readouterr()
    assert "class Point(list):" in captured.out



def test_namedlist_extra_list_methods():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    p.append(3)
    assert p[2] == 3
    p.extend([4, 5])
    assert p[3] == 4 and p[4] == 5
    p.pop()
    assert len(p) == 4

def test_namedtuple_is_tuple():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, tuple)
    assert not isinstance(p, list)

def test_namedlist_is_list():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, list)
    assert not isinstance(p, tuple)