import pytest
import namedutils

def test_namedtuple_basic_usage_and_repr():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, tuple)
    assert p.x == 1
    assert p.y == 2
    assert p[0] == 1
    assert p[1] == 2
    assert repr(p) == "Point(x=1, y=2)"
    assert p.__class__.__name__ == "Point"
    assert p.__doc__ == "Point(x, y)"
    assert p._fields == ('x', 'y')

def test_namedtuple_unpacking_and_asdict():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point(11, 22)
    x, y = p
    assert (x, y) == (11, 22)
    d = p._asdict()
    assert d == {'x': 11, 'y': 22}
    assert list(d.keys()) == ['x', 'y']
    assert list(d.values()) == [11, 22]

def test_namedtuple_make_and_replace():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    p = Point._make([5, 6])
    assert isinstance(p, Point)
    assert p.x == 5
    assert p.y == 6
    p2 = p._replace(x=100)
    assert isinstance(p2, Point)
    assert p2.x == 100
    assert p2.y == 6
    # _replace with unknown field
    with pytest.raises(ValueError) as e:
        p._replace(z=1)
    assert "Got unexpected field names" in str(e.value)

def test_namedtuple_make_wrong_length():
    Point = namedutils.namedtuple('Point', ['x', 'y'])
    with pytest.raises(TypeError) as e:
        Point._make([1])
    assert "Expected 2 arguments, got 1" in str(e.value)
    with pytest.raises(TypeError) as e:
        Point._make([1, 2, 3])
    assert "Expected 2 arguments, got 3" in str(e.value)

def test_namedtuple_invalid_typename_and_fieldnames():
    # Invalid typename: contains dash
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Bad-Type', ['x', 'y'])
    assert "alphanumeric characters and underscores" in str(e.value)
    # Invalid fieldname: is a keyword
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['for'])
    assert "cannot be a keyword" in str(e.value)
    # Invalid fieldname: starts with digit
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['1x'])
    assert "cannot start with a number" in str(e.value)
    # Invalid fieldname: starts with underscore
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['_x'])
    assert "cannot start with an underscore" in str(e.value)
    # Duplicate fieldname
    with pytest.raises(ValueError) as e:
        namedutils.namedtuple('Point', ['x', 'x'])
    assert "duplicate field name" in str(e.value)

def test_namedtuple_rename_option():
    # Should rename invalid and duplicate fields
    T = namedutils.namedtuple('T', ['x', 'x', 'for', '_y', '1z'], rename=True)
    assert T._fields == ('x', '_1', '_2', '_3', '_4')
    t = T(1, 2, 3, 4, 5)
    assert t._asdict() == {'x': 1, '_1': 2, '_2': 3, '_3': 4, '_4': 5}

def test_namedtuple_from_string_fieldnames():
    T = namedutils.namedtuple('T', 'a, b c')
    t = T(1, 2, 3)
    assert t.a == 1
    assert t.b == 2
    assert t.c == 3

def test_namedtuple_kwargs_instantiation():
    T = namedutils.namedtuple('T', ['a', 'b'])
    t = T(a=10, b=20)
    assert t.a == 10
    assert t.b == 20
    t2 = T(30, b=40)
    assert t2.a == 30
    assert t2.b == 40

def test_namedtuple_getnewargs_and_dict_property():
    T = namedutils.namedtuple('T', ['a', 'b'])
    t = T(1, 2)
    assert t.__getnewargs__() == (1, 2)
    assert t.__dict__ == {'a': 1, 'b': 2}

def test_namedtuple_repr_inheritance():
    class MyTuple(namedutils.namedtuple('MyTuple', ['a', 'b'])):
        pass
    m = MyTuple(1, 2)
    assert repr(m) == "MyTuple(a=1, b=2)"

def test_namedtuple_asdict_order():
    T = namedutils.namedtuple('T', ['a', 'b', 'c'])
    t = T(1, 2, 3)
    d = t._asdict()
    assert list(d.keys()) == ['a', 'b', 'c']
    assert list(d.values()) == [1, 2, 3]

def test_namedlist_basic_usage_and_repr():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(1, 2)
    assert isinstance(p, list)
    assert p.x == 1
    assert p.y == 2
    assert p[0] == 1
    assert p[1] == 2
    assert repr(p) == "Point(x=1, y=2)"
    assert p.__class__.__name__ == "Point"
    assert p.__doc__ == "Point(x, y)"
    assert p._fields == ('x', 'y')

def test_namedlist_unpacking_and_asdict():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point(11, 22)
    x, y = p
    assert (x, y) == (11, 22)
    d = p._asdict()
    assert d == {'x': 11, 'y': 22}
    assert list(d.keys()) == ['x', 'y']
    assert list(d.values()) == [11, 22]

def test_namedlist_make_and_replace():
    Point = namedutils.namedlist('Point', ['x', 'y'])
    p = Point._make([5, 6])
    assert isinstance(p, Point)
    assert p.x == 5
    assert p.y == 6
    p2 = p._replace(x=100)
    assert isinstance(p2, Point)
    assert p2.x == 100
    assert p2.y == 6
    # _replace with unknown field
    with pytest.raises(ValueError) as e:
        p._replace(z=1)
    assert "Got unexpected field names" in str(e.value)


def test_namedlist_invalid_typename_and_fieldnames():
    # Invalid typename: contains dash
    with pytest.raises(ValueError) as e:
        namedutils.namedlist('Bad-Type', ['x', 'y'])
    assert "alphanumeric characters and underscores" in str(e.value)
    # Invalid fieldname: is a keyword
    with pytest.raises(ValueError) as e:
        namedutils.namedlist('Point', ['for'])
    assert "cannot be a keyword" in str(e.value)
    # Invalid fieldname: starts with digit
    with pytest.raises(ValueError) as e:
        namedutils.namedlist('Point', ['1x'])
    assert "cannot start with a number" in str(e.value)
    # Invalid fieldname: starts with underscore
    with pytest.raises(ValueError) as e:
        namedutils.namedlist('Point', ['_x'])
    assert "cannot start with an underscore" in str(e.value)
    # Duplicate fieldname
    with pytest.raises(ValueError) as e:
        namedutils.namedlist('Point', ['x', 'x'])
    assert "duplicate field name" in str(e.value)

def test_namedlist_rename_option():
    # Should rename invalid and duplicate fields
    T = namedutils.namedlist('T', ['x', 'x', 'for', '_y', '1z'], rename=True)
    assert T._fields == ('x', '_1', '_2', '_3', '_4')
    t = T(1, 2, 3, 4, 5)
    assert t._asdict() == {'x': 1, '_1': 2, '_2': 3, '_3': 4, '_4': 5}

def test_namedlist_from_string_fieldnames():
    T = namedutils.namedlist('T', 'a, b c')
    t = T(1, 2, 3)
    assert t.a == 1
    assert t.b == 2
    assert t.c == 3

def test_namedlist_kwargs_instantiation():
    T = namedutils.namedlist('T', ['a', 'b'])
    t = T(a=10, b=20)
    assert t.a == 10
    assert t.b == 20
    t2 = T(30, b=40)
    assert t2.a == 30
    assert t2.b == 40

def test_namedlist_getnewargs_and_dict_property():
    T = namedutils.namedlist('T', ['a', 'b'])
    t = T(1, 2)
    assert t.__getnewargs__() == (1, 2)
    assert t.__dict__ == {'a': 1, 'b': 2}

def test_namedlist_repr_inheritance():
    class MyList(namedutils.namedlist('MyList', ['a', 'b'])):
        pass
    m = MyList(1, 2)
    assert repr(m) == "MyList(a=1, b=2)"

def test_namedlist_asdict_order():
    T = namedutils.namedlist('T', ['a', 'b', 'c'])
    t = T(1, 2, 3)
    d = t._asdict()
    assert list(d.keys()) == ['a', 'b', 'c']
    assert list(d.values()) == [1, 2, 3]

def test_namedlist_mutability_and_setters():
    T = namedutils.namedlist('T', ['a', 'b'])
    t = T(1, 2)
    t.a = 10
    t.b = 20
    assert t.a == 10
    assert t.b == 20
    assert t[0] == 10
    assert t[1] == 20
    t[0] = 100
    t[1] = 200
    assert t.a == 100
    assert t.b == 200

def test_namedlist_and_namedtuple_are_distinct_types():
    T1 = namedutils.namedtuple('T', ['a', 'b'])
    T2 = namedutils.namedlist('T', ['a', 'b'])
    t1 = T1(1, 2)
    t2 = T2(1, 2)
    assert isinstance(t1, tuple)
    assert not isinstance(t1, list)
    assert isinstance(t2, list)
    assert not isinstance(t2, tuple)
    assert t1._fields == t2._fields
    assert t1._asdict() == t2._asdict()
    assert repr(t1) == repr(t2)


def test_namedtuple_verbose_flag_prints_class_definition(capsys):
    # line 138: verbose=False -> True
    # If verbose=True, the class definition should be printed to stdout.
    T = namedutils.namedtuple('VerbosePoint', ['x', 'y'], verbose=True)
    out = capsys.readouterr().out
    assert "class VerbosePoint(tuple):" in out
    assert "def __new__(_cls, x, y):" in out
    # The returned class should still work
    t = T(1, 2)
    assert t.x == 1
    assert t.y == 2


def test_namedlist_verbose_flag_prints_class_definition(capsys):
    # line 297: verbose=False -> True
    T = namedutils.namedlist('VerboseList', ['a', 'b'], verbose=True)
    out = capsys.readouterr().out
    assert "class VerboseList(list):" in out
    assert "def __new__(_cls, a, b):" in out
    t = T(3, 4)
    assert t.a == 3
    assert t.b == 4


def test_namedtuple_invalid_fieldname_character():
    # line 169: comparison == -> !=
    # Should reject field names with invalid characters (e.g., dash)
    try:
        namedutils.namedtuple('Point', ['x-y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid field name"


def test_namedtuple_invalid_fieldname_character_underscore():
    # line 169: string '_' -> 'XX...XX'
    # Should still allow underscores in field names
    try:
        namedutils.namedtuple('Point', ['x_y'])
    except ValueError:
        assert False, "Underscore should be allowed in field names"


def test_namedtuple_invalid_typename_message():
    # line 179: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Bad-Type', ['x', 'y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid typename"


def test_namedtuple_keyword_fieldname_message():
    # line 183: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Point', ['for'])
    except ValueError as e:
        assert "cannot be a keyword" in str(e)
    else:
        assert False, "Expected ValueError for keyword field name"


def test_namedtuple_digit_fieldname_message():
    # line 186: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Point', ['1x'])
    except ValueError as e:
        assert "cannot start with a number" in str(e)
    else:
        assert False, "Expected ValueError for digit-start field name"


def test_namedtuple_underscore_fieldname_message():
    # line 191: string 'Field names cannot s...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Point', ['_x'])
    except ValueError as e:
        assert "cannot start with an underscore" in str(e)
    else:
        assert False, "Expected ValueError for underscore field name"


def test_namedtuple_duplicate_fieldname_message():
    # line 194: string 'Encountered duplicat...' -> 'XX...XX'
    try:
        namedutils.namedtuple('Point', ['x', 'x'])
    except ValueError as e:
        assert "duplicate field name" in str(e)
    else:
        assert False, "Expected ValueError for duplicate field name"




def test_namedlist_invalid_fieldname_character():
    # line 328: comparison == -> !=
    try:
        namedutils.namedlist('Point', ['x-y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid field name"


def test_namedlist_invalid_fieldname_character_underscore():
    # line 328: string '_' -> 'XX...XX'
    try:
        namedutils.namedlist('Point', ['x_y'])
    except ValueError:
        assert False, "Underscore should be allowed in field names"


def test_namedlist_invalid_typename_message():
    # line 338: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedlist('Bad-Type', ['x', 'y'])
    except ValueError as e:
        assert "alphanumeric characters and underscores" in str(e)
    else:
        assert False, "Expected ValueError for invalid typename"


def test_namedlist_keyword_fieldname_message():
    # line 342: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedlist('Point', ['for'])
    except ValueError as e:
        assert "cannot be a keyword" in str(e)
    else:
        assert False, "Expected ValueError for keyword field name"


def test_namedlist_digit_fieldname_message():
    # line 345: string 'Type names and field...' -> 'XX...XX'
    try:
        namedutils.namedlist('Point', ['1x'])
    except ValueError as e:
        assert "cannot start with a number" in str(e)
    else:
        assert False, "Expected ValueError for digit-start field name"


def test_namedlist_underscore_fieldname_message():
    # line 350: string 'Field names cannot s...' -> 'XX...XX'
    try:
        namedutils.namedlist('Point', ['_x'])
    except ValueError as e:
        assert "cannot start with an underscore" in str(e)
    else:
        assert False, "Expected ValueError for underscore field name"


def test_namedlist_duplicate_fieldname_message():
    # line 353: string 'Encountered duplicat...' -> 'XX...XX'
    try:
        namedutils.namedlist('Point', ['x', 'x'])
    except ValueError as e:
        assert "duplicate field name" in str(e)
    else:
        assert False, "Expected ValueError for duplicate field name"


