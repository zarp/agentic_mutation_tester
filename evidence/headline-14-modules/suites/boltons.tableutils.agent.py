import pytest
import tableutils

from collections import namedtuple

def test_to_text_str_and_repr():
    class Weird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): return "repr!"
    class VeryWeird:
        def __str__(self): raise Exception("fail str")
        def __repr__(self): raise Exception("fail repr")
    # Normal string
    assert tableutils.to_text("abc") == "abc"
    # Integer
    assert tableutils.to_text(123) == "123"
    # Object with broken __str__, working __repr__
    assert tableutils.to_text(Weird()) == "repr!"
    # Object with broken __str__ and __repr__
    result = tableutils.to_text(VeryWeird())
    assert result.startswith("<") and "VeryWeird" in result
    # maxlen truncates
    assert tableutils.to_text("abcdef", maxlen=5) == "ab..."

def test_escape_html_basic():
    assert tableutils.escape_html("<tag>") == "&lt;tag&gt;"
    assert tableutils.escape_html('"quote"') == "&quot;quote&quot;"
    # maxlen truncates before escaping
    assert tableutils.escape_html("<abcdef>", maxlen=5) == "&lt;a..."

def test_dictinputtype_check_type_and_guess_headers():
    d = {"b": 2, "a": 1}
    it = tableutils.DictInputType()
    assert it.check_type(d) is True
    assert it.check_type([1,2]) is False
    # headers are sorted
    assert it.guess_headers(d) == ["a", "b"]

def test_dictinputtype_get_entry_and_get_entry_seq():
    d = {"a": 1, "b": 2}
    it = tableutils.DictInputType()
    headers = ["a", "b", "c"]
    assert it.get_entry(d, headers) == [1, 2, None]
    seq = [{"a": 1, "b": 2}, {"a": 3, "c": 4}]
    assert it.get_entry_seq(seq, headers) == [[1, 2, None], [3, None, 4]]

def test_objectinputtype_check_type_and_guess_headers():
    class X:
        def __init__(self): self.a = 1; self.b = 2
        def method(self): pass
    x = X()
    it = tableutils.ObjectInputType()
    assert it.check_type(x) is True
    assert it.check_type(5) is False
    headers = it.guess_headers(x)
    # Should include 'a' and 'b', not 'method'
    assert "a" in headers and "b" in headers
    assert "method" not in headers

def test_objectinputtype_get_entry_missing_attr():
    class X: pass
    x = X()
    it = tableutils.ObjectInputType()
    headers = ["foo"]
    assert it.get_entry(x, headers) == [None]

def test_listinputtype_check_type_and_get_entry():
    it = tableutils.ListInputType()
    assert it.check_type([1,2]) is True
    assert it.check_type((1,2)) is False
    assert it.guess_headers([1,2]) is None
    assert it.get_entry([1,2], None) == [1,2]
    assert it.get_entry_seq([[1,2],[3,4]], None) == [[1,2],[3,4]]

def test_tupleinputtype_check_type_and_get_entry():
    it = tableutils.TupleInputType()
    assert it.check_type((1,2)) is True
    assert it.check_type([1,2]) is False
    assert it.guess_headers((1,2)) is None
    assert it.get_entry((1,2), None) == [1,2]
    assert it.get_entry_seq([(1,2),(3,4)], None) == [[1,2],[3,4]]

def test_namedtupleinputtype_check_type_and_get_entry():
    NT = namedtuple("NT", "a b")
    nt = NT(1,2)
    it = tableutils.NamedTupleInputType()
    assert it.check_type(nt) is True
    assert it.check_type((1,2)) is False
    assert it.guess_headers(nt) == ["a", "b"]
    assert it.get_entry(nt, ["a", "b", "c"]) == [1, 2, None]
    seq = [NT(1,2), NT(3,4)]
    assert it.get_entry_seq(seq, ["a", "b"]) == [[1,2],[3,4]]

def test_table_init_and_repr_with_headers():
    t = tableutils.Table([[1,2],[3,4]], headers=["x","y"])
    assert t.headers == ["x","y"]
    assert t._data == [[1,2],[3,4]]
    assert repr(t) == "Table(headers=['x', 'y'], data=[[1, 2], [3, 4]])"



def test_table_extend_and_fill():
    t = tableutils.Table([[1,2]], headers=["a","b","c"])
    t.extend([[3,4]])
    # Should fill with None to match width
    assert t._data == [[1,2,None],[3,4,None]]

def test_table_set_width_and_fill_behavior():
    t = tableutils.Table([[1,2,3],[4,5]], headers=["a","b","c"])
    t._width = 0
    t._set_width()
    assert t._width == 3
    t._data[1].pop()
    t._fill()
    assert t._data[1] == [4,5,None]

def test_table_from_dict_and_from_list_and_from_object():
    d = {"a": 1, "b": 2}
    t = tableutils.Table.from_dict([d])
    assert t.headers == ["a", "b"]
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_list([[1,2],[3,4]], headers=["x","y"])
    assert t2.headers == ["x","y"]
    assert t2._data == [[1,2],[3,4]]
    class X: pass
    x = X(); x.a = 1; x.b = 2
    t3 = tableutils.Table.from_object([x], headers=["a","b"])
    assert t3.headers == ["a","b"]
    assert t3._data == [[1,2]]


def test_table_from_data_max_depth_zero():
    t = tableutils.Table.from_data([[1,2]], max_depth=0)
    assert t._data == []

def test_table_from_data_nested_max_depth():
    d = {"a": [1,2], "b": [3,4]}
    t = tableutils.Table.from_data([d], max_depth=2)
    # The cells should be Table instances
    assert isinstance(t._data[0][0], tableutils.Table)
    assert isinstance(t._data[0][1], tableutils.Table)
    # The nested tables should have the correct data
    assert t._data[0][0]._data == [[1,2]]

def test_table_to_html_horizontal_and_vertical():
    t = tableutils.Table([[1,2],[3,4]], headers=["x","y"])
    html = t.to_html(orientation="horizontal", wrapped=True, with_headers=True, with_newlines=True)
    assert "<table>" in html and "<th>x</th>" in html and "<td>1</td>" in html
    html_v = t.to_html(orientation="vertical", wrapped=True, with_headers=True, with_newlines=True)
    assert "<table>" in html_v and "<th>x</th>" in html_v and "<td>1</td>" in html_v

def test_table_to_html_auto_orientation():
    t = tableutils.Table([[1,2]], headers=["x","y"])
    html = t.to_html(orientation="auto", wrapped=True, with_headers=True)
    # For one row, should be vertical
    assert "<th>x</th>" in html and "<td>1</td>" in html

def test_table_to_html_invalid_orientation():
    t = tableutils.Table([[1,2]], headers=["x","y"])
    with pytest.raises(ValueError) as e:
        t.to_html(orientation="sideways")
    assert "expected one of" in str(e.value)

def test_table_to_html_with_metadata_top_and_bottom():
    t = tableutils.Table([[1,2]], headers=["x","y"], metadata={"foo": "bar"})
    html_top = t.to_html(with_metadata=True)
    assert "<table>" in html_top and "foo" in html_top
    html_bottom = t.to_html(with_metadata="bottom")
    assert "<table>" in html_bottom and "foo" in html_bottom

def test_table_get_cell_html_escapes():
    t = tableutils.Table([[1, "<b>"]])
    assert t.get_cell_html("<b>") == "&lt;b&gt;"

def test_table_to_text_with_headers_and_maxlen():
    t = tableutils.Table([[123456, "abcdef"], [789, "ghijkl"]], headers=["num", "txt"])
    txt = t.to_text(with_headers=True, maxlen=5)
    # Should truncate cells to 5 chars
    assert "12..." in txt or "ab..." in txt
    # Should include headers
    assert "num" in txt and "txt" in txt

def test_table_to_text_without_headers():
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    txt = t.to_text(with_headers=False)
    assert "a" not in txt and "b" not in txt
    assert "1" in txt and "2" in txt

def test_table_vertical_html_lines_and_horizontal_html_lines():
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    lines = []
    t._add_horizontal_html_lines(lines, headers=["a","b"], max_depth=1)
    assert any("<td>1</td>" in l or "<td>2</td>" in l for l in lines)
    lines2 = []
    t._add_vertical_html_lines(lines2, headers=["a","b"], max_depth=1)
    assert any("<td>1</td>" in l or "<td>3</td>" in l for l in lines2)


def test_to_text_maxlen_boundary():
    # Kills: line 109: comparison > -> >=
    # If maxlen == len(text), original does not truncate, mutant does.
    s = "abcde"
    # maxlen == len(s): should NOT truncate
    assert tableutils.to_text(s, maxlen=5) == "abcde"
    # maxlen < len(s): should truncate
    assert tableutils.to_text(s, maxlen=4) == "a..."


def test_objectinputtype_guess_headers_skips_property_exception():
    # Kills: line 165: continue -> break
    class X:
        @property
        def bad(self):
            raise Exception("fail")
        a = 1
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # Should still include 'a' even if 'bad' property raises
    assert "a" in headers


def test_table_init_headers_infer_one_row():
    # Kills: line 284: 1 -> 2
    # Should infer headers from first row, and data from rest
    t = tableutils.Table([[1,2,3], [4,5,6], [7,8,9]])
    # First row becomes headers, rest is data
    assert t.headers == [1,2,3]
    assert list(t._data) == [[4,5,6],[7,8,9]]


def test_table_set_width_reset_flag():
    # Kills: line 302: False -> True, line 304: 0 -> 1
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99 or 1
    assert t._width == 3


def test_table_fill_no_extend_when_full():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])
    # Already full, should not extend
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before


def test_table_from_dict_max_depth_arg():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d], max_depth=1)
    # Should include the data, not empty
    assert t._data == [[1]]


def test_table_from_list_max_depth_arg():
    # Kills: line 333: 1 -> 2
    t = tableutils.Table.from_list([[1,2]], max_depth=1)
    assert t._data == [[1,2]]


def test_table_from_object_max_depth_arg():
    # Kills: line 343: 1 -> 2
    class X: pass
    x = X(); x.a = 1
    t = tableutils.Table.from_object([x], headers=["a"], max_depth=1)
    assert t._data == [[1]]


def test_table_from_data_max_depth_arg():
    # Kills: line 354: 1 -> 2
    t = tableutils.Table.from_data([[1,2]], max_depth=1)
    assert t._data == [[1,2]]


def test_table_from_data_max_depth_zero_returns_empty():
    # Kills: line 386: return value replaced with None
    t = tableutils.Table.from_data([[1,2]], max_depth=0)
    assert isinstance(t, tableutils.Table)
    assert t._data == []








def test_table_from_data_max_depth_nested():
    # Kills: line 417: > -> >=, line 418: - -> +
    d = {"a": [1,2]}
    t = tableutils.Table.from_data([d], max_depth=2)
    # Should nest one level, not two
    assert isinstance(t._data[0][0], tableutils.Table)
    # The nested table should have the correct data
    assert t._data[0][0]._data == [[1,2]]


def test_table_from_data_nested_breaks_continue():
    # Kills: line 423: continue -> break, line 428: continue -> break
    # If a cell is in _DNR or raises UnsupportedData, should skip just that cell, not break the whole row
    d = {"a": [1,2], "b": 5}
    t = tableutils.Table.from_data([d], max_depth=2)
    # "a" should be a Table, "b" should be 5
    assert isinstance(t._data[0][0], tableutils.Table)
    assert t._data[0][1] == 5




def test_table_repr_with_headers_and_without():
    # Kills: line 442: return value replaced with None
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    assert "headers" in repr(t)
    t2 = tableutils.Table([[1,2],[3,4]])
    assert "Table" in repr(t2)


def test_table_to_html_with_headers_and_newlines_defaults():
    # Kills: line 445: True -> False, line 446: False -> True, line 446: 1 -> 2
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    html = t.to_html()
    # Should include headers and newlines by default
    assert "<th>a</th>" in html and "<th>b</th>" in html
    assert "\n" in html


def test_table_to_html_with_metadata_default_false():
    # Kills: line 446: False -> True
    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    # Should NOT include metadata
    assert "foo" not in html


def test_objectinputtype_guess_headers_break_vs_continue():
    # Kills: line 165: continue -> break
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers


def test_table_set_width_reset_true():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    t._width = 99
    t._set_width(reset=True)
    assert t._width == 2


def test_table_fill_no_extend_when_full_boundary():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2]], headers=["a","b"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before


def test_table_from_dict_max_depth_default():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d])
    assert t._data == [[1]]


def test_table_from_list_max_depth_default():
    # Kills: line 333: 1 -> 2
    t = tableutils.Table.from_list([[1,2]])
    assert t._data == [[1,2]]


def test_table_from_object_max_depth_default():
    # Kills: line 343: 1 -> 2
    class X: pass
    x = X(); x.a = 1
    t = tableutils.Table.from_object([x], headers=["a"])
    assert t._data == [[1]]


def test_table_from_data_max_depth_default():
    # Kills: line 354: 1 -> 2
    t = tableutils.Table.from_data([[1,2]])
    assert t._data == [[1,2]]


def test_table_from_data_max_depth_zero_returns_empty_none():
    # Kills: line 386: return value replaced with None
    t = tableutils.Table.from_data([[1,2]], max_depth=0)
    assert isinstance(t, tableutils.Table)
    assert t._data == []








def test_table_from_data_max_depth_nested_boundary():
    # Kills: line 417: > -> >=, line 418: - -> +
    d = {"a": [1,2]}
    t = tableutils.Table.from_data([d], max_depth=2)
    # Should nest one level, not two
    assert isinstance(t._data[0][0], tableutils.Table)
    assert t._data[0][0]._data == [[1,2]]


def test_table_getitem_returns_row():
    # Kills: line 435: return value replaced with None
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    assert t[0] == [1,2]
    assert t[1] == [3,4]


def test_table_repr_with_headers_and_without_none():
    # Kills: line 442: return value replaced with None
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    r = repr(t)
    assert isinstance(r, str)
    t2 = tableutils.Table([[1,2],[3,4]])
    r2 = repr(t2)
    assert isinstance(r2, str)


def test_table_to_html_with_metadata_and_newlines_defaults():
    # Kills: line 446: False -> True, line 446: 1 -> 2
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html()
    assert "<th>a</th>" in html and "<th>b</th>" in html
    assert "\n" in html
    assert "foo" not in html  # metadata should not be included by default


def test_table_to_html_with_metadata_false():
    # Kills: line 481: False -> True
    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html


def test_objectinputtype_guess_headers_continue_vs_break():
    # Kills: line 165: continue -> break
    # If 'break' is used, headers collection stops at first exception property.
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers


def test_table_set_width_reset_true_vs_false():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99
    assert t._width == 3


def test_table_fill_no_extend_when_full_vs_ge():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before


def test_table_from_dict_max_depth_default_and_arg():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d])
    assert t._data == [[1]]
    t2 = tableutils.Table.from_dict([d], max_depth=1)
    assert t2._data == [[1]]


def test_table_from_list_max_depth_default_and_arg():
    # Kills: line 333: 1 -> 2
    t = tableutils.Table.from_list([[1,2]])
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_list([[1,2]], max_depth=1)
    assert t2._data == [[1,2]]


def test_table_from_object_max_depth_default_and_arg():
    # Kills: line 343: 1 -> 2
    class X: pass
    x = X(); x.a = 1
    t = tableutils.Table.from_object([x], headers=["a"])
    assert t._data == [[1]]
    t2 = tableutils.Table.from_object([x], headers=["a"], max_depth=1)
    assert t2._data == [[1]]


def test_table_from_data_max_depth_default_and_arg():
    # Kills: line 354: 1 -> 2
    t = tableutils.Table.from_data([[1,2]])
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_data([[1,2]], max_depth=1)
    assert t2._data == [[1,2]]


def test_table_from_data_max_depth_zero_returns_empty_and_none():
    # Kills: line 386: return value replaced with None
    t = tableutils.Table.from_data([[1,2]], max_depth=0)
    assert isinstance(t, tableutils.Table)
    assert t._data == []


def test_table_from_data_max_depth_nested_and_boundary():
    # Kills: line 417: > -> >=, line 418: - -> +
    d = {"a": [1,2]}
    t = tableutils.Table.from_data([d], max_depth=2)
    # Should nest one level, not two
    assert isinstance(t._data[0][0], tableutils.Table)
    assert t._data[0][0]._data == [[1,2]]


def test_objectinputtype_guess_headers_continue_vs_break_killer():
    # Kills: line 165: continue -> break
    class X:
        a = 1
        @property
        def bad(self):
            raise Exception("fail")
        b = 2
    it = tableutils.ObjectInputType()
    headers = it.guess_headers(X())
    # If 'break' is used, 'b' will not be included after 'bad'
    assert "a" in headers and "b" in headers


def test_table_set_width_reset_true_killer():
    # Kills: line 302: False -> True
    t = tableutils.Table([[1,2,3],[4,5,6]], headers=["a","b","c"])
    t._width = 99
    t._set_width(reset=True)
    # Should recalculate width to 3, not leave at 99
    assert t._width == 3


def test_table_fill_no_extend_when_full_vs_ge_killer():
    # Kills: line 318: > -> >=
    t = tableutils.Table([[1,2,3]], headers=["a","b","c"])
    before = list(t._data[0])
    t._fill()
    assert t._data[0] == before


def test_table_from_dict_max_depth_default_and_arg_killer():
    # Kills: line 323: 1 -> 2
    d = {"a": 1}
    t = tableutils.Table.from_dict([d])
    assert t._data == [[1]]
    t2 = tableutils.Table.from_dict([d], max_depth=1)
    assert t2._data == [[1]]


def test_table_from_list_max_depth_default_and_arg_killer():
    # Kills: line 333: 1 -> 2
    t = tableutils.Table.from_list([[1,2]])
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_list([[1,2]], max_depth=1)
    assert t2._data == [[1,2]]


def test_table_from_object_max_depth_default_and_arg_killer():
    # Kills: line 343: 1 -> 2
    class X: pass
    x = X(); x.a = 1
    t = tableutils.Table.from_object([x], headers=["a"])
    assert t._data == [[1]]
    t2 = tableutils.Table.from_object([x], headers=["a"], max_depth=1)
    assert t2._data == [[1]]


def test_table_from_data_max_depth_default_and_arg_killer():
    # Kills: line 354: 1 -> 2
    t = tableutils.Table.from_data([[1,2]])
    assert t._data == [[1,2]]
    t2 = tableutils.Table.from_data([[1,2]], max_depth=1)
    assert t2._data == [[1,2]]


def test_table_from_data_max_depth_zero_returns_empty_and_none_killer():
    # Kills: line 386: return value replaced with None
    t = tableutils.Table.from_data([[1,2]], max_depth=0)
    assert isinstance(t, tableutils.Table)
    assert t._data == []


def test_table_from_data_max_depth_nested_and_boundary_killer():
    # Kills: line 417: > -> >=, line 418: - -> +
    d = {"a": [1,2]}
    t = tableutils.Table.from_data([d], max_depth=2)
    # Should nest one level, not two
    assert isinstance(t._data[0][0], tableutils.Table)
    assert t._data[0][0]._data == [[1,2]]


def test_table_from_data_nested_breaks_continue_killer():
    # Kills: line 423: continue -> break, line 428: continue -> break
    d = {"a": [1,2], "b": 5}
    t = tableutils.Table.from_data([d], max_depth=2)
    # "a" should be a Table, "b" should be 5
    assert isinstance(t._data[0][0], tableutils.Table)
    assert t._data[0][1] == 5


def test_table_repr_with_headers_and_without_none_killer():
    # Kills: line 442: return value replaced with None
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"])
    r = repr(t)
    assert isinstance(r, str)
    t2 = tableutils.Table([[1,2],[3,4]])
    r2 = repr(t2)
    assert isinstance(r2, str)


def test_table_to_html_with_metadata_and_newlines_defaults_killer():
    # Kills: line 446: False -> True, line 446: 1 -> 2
    t = tableutils.Table([[1,2],[3,4]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html()
    assert "<th>a</th>" in html and "<th>b</th>" in html
    assert "\n" in html
    assert "foo" not in html  # metadata should not be included by default


def test_table_to_html_with_metadata_false_killer():
    # Kills: line 481: False -> True
    t = tableutils.Table([[1,2]], headers=["a","b"], metadata={"foo": "bar"})
    html = t.to_html(with_metadata=False)
    assert "foo" not in html
