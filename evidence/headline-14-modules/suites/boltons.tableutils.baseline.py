import pytest
import types
import sys
import tableutils

from collections import namedtuple

# Helper for Python 2/3 compatibility
try:
    unicode
except NameError:
    unicode = str


def test_to_text_maxlen():
    s = "abcdef"
    assert tableutils.to_text(s, maxlen=5) == "ab..."

def test_escape_html_basic():
    assert tableutils.escape_html("<b>") == "&lt;b&gt;"
    assert tableutils.escape_html('"') == "&quot;"


def test_DictInputType_check_type():
    d = {"a": 1}
    assert tableutils.DictInputType().check_type(d)
    assert not tableutils.DictInputType().check_type([1, 2])

def test_DictInputType_guess_headers():
    d = {"b": 2, "a": 1}
    headers = tableutils.DictInputType().guess_headers(d)
    assert headers == ["a", "b"]

def test_DictInputType_get_entry():
    d = {"a": 1, "b": 2}
    headers = ["a", "b", "c"]
    entry = tableutils.DictInputType().get_entry(d, headers)
    assert entry == [1, 2, None]

def test_DictInputType_get_entry_seq():
    seq = [{"a": 1, "b": 2}, {"a": 3, "b": 4}]
    headers = ["a", "b"]
    entries = tableutils.DictInputType().get_entry_seq(seq, headers)
    assert entries == [[1, 2], [3, 4]]

def test_ObjectInputType_check_type():
    class X: pass
    x = X()
    assert tableutils.ObjectInputType().check_type(x)
    assert not tableutils.ObjectInputType().check_type(None)
    assert not tableutils.ObjectInputType().check_type(1)
    assert not tableutils.ObjectInputType().check_type("abc")

def test_ObjectInputType_guess_headers():
    class X:
        def __init__(self):
            self.a = 1
            self.b = 2
        def method(self): pass
    x = X()
    headers = tableutils.ObjectInputType().guess_headers(x)
    # Should include 'a' and 'b', not 'method'
    assert "a" in headers and "b" in headers
    assert "method" not in headers

def test_ObjectInputType_get_entry():
    class X:
        def __init__(self):
            self.a = 1
    x = X()
    headers = ["a", "b"]
    entry = tableutils.ObjectInputType().get_entry(x, headers)
    assert entry == [1, None]

def test_ListInputType_check_type():
    assert tableutils.ListInputType().check_type([1, 2])
    assert not tableutils.ListInputType().check_type((1, 2))

def test_ListInputType_guess_headers():
    assert tableutils.ListInputType().guess_headers([1, 2]) is None

def test_ListInputType_get_entry():
    obj = [1, 2]
    assert tableutils.ListInputType().get_entry(obj, None) == obj

def test_ListInputType_get_entry_seq():
    seq = [[1, 2], [3, 4]]
    assert tableutils.ListInputType().get_entry_seq(seq, None) == seq

def test_TupleInputType_check_type():
    assert tableutils.TupleInputType().check_type((1, 2))
    assert not tableutils.TupleInputType().check_type([1, 2])

def test_TupleInputType_guess_headers():
    assert tableutils.TupleInputType().guess_headers((1, 2)) is None

def test_TupleInputType_get_entry():
    tup = (1, 2)
    assert tableutils.TupleInputType().get_entry(tup, None) == [1, 2]

def test_TupleInputType_get_entry_seq():
    seq = [(1, 2), (3, 4)]
    assert tableutils.TupleInputType().get_entry_seq(seq, None) == [[1, 2], [3, 4]]

def test_NamedTupleInputType_check_type():
    NT = namedtuple("NT", "a b")
    nt = NT(1, 2)
    assert tableutils.NamedTupleInputType().check_type(nt)
    assert not tableutils.NamedTupleInputType().check_type((1, 2))

def test_NamedTupleInputType_guess_headers():
    NT = namedtuple("NT", "a b")
    nt = NT(1, 2)
    assert tableutils.NamedTupleInputType().guess_headers(nt) == ["a", "b"]

def test_NamedTupleInputType_get_entry():
    NT = namedtuple("NT", "a b")
    nt = NT(1, 2)
    headers = ["a", "b", "c"]
    entry = tableutils.NamedTupleInputType().get_entry(nt, headers)
    assert entry == [1, 2, None]

def test_NamedTupleInputType_get_entry_seq():
    NT = namedtuple("NT", "a b")
    seq = [NT(1, 2), NT(3, 4)]
    headers = ["a", "b"]
    entries = tableutils.NamedTupleInputType().get_entry_seq(seq, headers)
    assert entries == [[1, 2], [3, 4]]

def test_Table_init_and_repr():
    data = [[1, 2], [3, 4]]
    headers = ["a", "b"]
    t = tableutils.Table(data, headers)
    assert t.headers == headers
    assert len(t) == 2
    assert repr(t).startswith("Table(headers=")
    t2 = tableutils.Table(data)
    assert isinstance(repr(t2), str)

def test_Table_extend_and_fill():
    t = tableutils.Table([[1], [2, 3]], headers=["a", "b"])
    # Should fill first row to [1, None]
    assert t[0] == [1, None]
    assert t[1] == [2, 3]

def test_Table_set_width_and_fill():
    t = tableutils.Table([[1], [2, 3]], headers=["a", "b"])
    t._width = 0
    t._set_width(reset=True)
    assert t._width == 2
    t._data[0] = [1]
    t._fill()
    assert t._data[0] == [1, None]

def test_Table_from_dict():
    d = {"a": 1, "b": 2}
    t = tableutils.Table.from_dict([d])
    assert t.headers == ["a", "b"]
    assert t[0] == [1, 2]

def test_Table_from_list():
    data = [[1, 2], [3, 4]]
    t = tableutils.Table.from_list(data, headers=["x", "y"])
    assert t.headers == ["x", "y"]
    assert t[1] == [3, 4]

def test_Table_from_object():
    class X:
        def __init__(self):
            self.a = 1
            self.b = 2
    x = X()
    t = tableutils.Table.from_object([x])
    assert "a" in t.headers and "b" in t.headers


def test_Table_from_data_empty_seq():
    t = tableutils.Table.from_data([])
    assert len(t) == 0


def test_Table_from_data_max_depth():
    d = {"a": {"b": 2}}
    t = tableutils.Table.from_data([d], max_depth=2)
    # Should nest a Table in cell
    cell = t[0][t.headers.index("a")]
    assert isinstance(cell, tableutils.Table)


def test_Table_to_html_horizontal():
    t = tableutils.Table([[1, 2], [3, 4]], headers=["a", "b"])
    html = t.to_html(orientation="horizontal", with_newlines=True)
    assert "<table>" in html
    assert "<th>1</th>" not in html
    assert "<th>a</th>" in html
    assert "<td>1</td>" in html

def test_Table_to_html_vertical():
    t = tableutils.Table([[1, 2], [3, 4]], headers=["a", "b"])
    html = t.to_html(orientation="vertical", with_newlines=True)
    assert "<th>a</th>" in html
    assert "<td>1</td>" in html

def test_Table_to_html_auto_orientation():
    t = tableutils.Table([[1, 2]], headers=["a", "b"])
    html = t.to_html(orientation="auto")
    # Should use vertical for single row
    assert "<th>a</th>" in html

    t2 = tableutils.Table([[1, 2], [3, 4]], headers=["a", "b"])
    html2 = t2.to_html(orientation="auto")
    # Should use horizontal for multiple rows
    assert "<th>a</th>" in html2

def test_Table_to_html_with_metadata():
    t = tableutils.Table([[1, 2]], headers=["a", "b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=True)
    assert "<table>" in html
    assert "foo" in html

def test_Table_to_html_with_metadata_bottom():
    t = tableutils.Table([[1, 2]], headers=["a", "b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata="bottom")
    assert html.strip().endswith("</table>")

def test_Table_to_html_invalid_orientation():
    t = tableutils.Table([[1, 2]], headers=["a", "b"])
    with pytest.raises(ValueError):
        t.to_html(orientation="sideways")

def test_Table_get_cell_html():
    t = tableutils.Table([[1, "<b>"]], headers=["a", "b"])
    assert t.get_cell_html("<b>") == "&lt;b&gt;"

def test_Table_to_text_basic():
    t = tableutils.Table([[1, 2], [3, 4]], headers=["a", "b"])
    txt = t.to_text()
    assert "a" in txt and "b" in txt
    assert "1" in txt and "4" in txt

def test_Table_to_text_no_headers():
    t = tableutils.Table([[1, 2], [3, 4]], headers=None)
    txt = t.to_text(with_headers=False)
    assert "a" not in txt and "b" not in txt

def test_Table_to_text_maxlen():
    t = tableutils.Table([["abcdef", "ghijkl"]], headers=["a", "b"])
    txt = t.to_text(maxlen=5)
    assert "ab..." in txt

def test_Table_repr_no_headers():
    t = tableutils.Table([[1, 2]])
    assert repr(t).startswith("Table(")