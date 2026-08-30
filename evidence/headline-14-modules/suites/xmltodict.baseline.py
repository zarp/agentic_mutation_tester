import xmltodict
import pytest
from io import StringIO, BytesIO

# --- Fixtures and helpers ---

@pytest.fixture
def simple_xml():
    return "<a prop='x'><b>1</b><b>2</b></a>"

@pytest.fixture
def simple_dict():
    return {'a': {'@prop': 'x', 'b': ['1', '2']}}

@pytest.fixture
def xml_with_namespaces():
    return (
        '<root xmlns:ns="http://example.com/ns">'
        '<ns:child ns:attr="val">text</ns:child>'
        '</root>'
    )

@pytest.fixture
def xml_with_comments():
    return (
        "<a>"
        "<b>"
        "<!-- b comment -->"
        "<c><!-- c comment -->1</c>"
        "<d>2</d>"
        "</b>"
        "</a>"
    )

@pytest.fixture
def xml_with_force_list():
    return (
        "<servers>"
        "<server>"
        "<name>host1</name>"
        "<os>Linux</os>"
        "<interfaces>"
        "<interface><name>em0</name><ip_address>10.0.0.1</ip_address></interface>"
        "</interfaces>"
        "</server>"
        "</servers>"
    )

@pytest.fixture
def xml_with_unicode():
    return u"<root><greeting>Привет</greeting></root>"

@pytest.fixture
def xml_with_empty():
    return "<root><empty/></root>"

@pytest.fixture
def xml_with_bool():
    return "<root><flag>true</flag><flag>false</flag></root>"

@pytest.fixture
def xml_with_attrs_and_text():
    return "<root><item id='1'>foo</item><item id='2'>bar</item></root>"

@pytest.fixture
def xml_with_multiple_roots():
    return "<a>1</a><b>2</b>"

# --- Tests for parse ---

def test_parse_simple(simple_xml, simple_dict):
    doc = xmltodict.parse(simple_xml)
    assert doc == simple_dict


def test_parse_bytes_input(simple_xml, simple_dict):
    doc = xmltodict.parse(simple_xml.encode('utf-8'))
    assert doc == simple_dict

def test_parse_unicode_input(xml_with_unicode):
    doc = xmltodict.parse(xml_with_unicode)
    assert doc['root']['greeting'] == 'Привет'

def test_parse_with_encoding(simple_xml):
    doc = xmltodict.parse(simple_xml, encoding='utf-8')
    assert doc['a']['@prop'] == 'x'

def test_parse_with_item_depth_callback(simple_xml):
    items = []
    def cb(path, item):
        items.append((path, item))
        return True
    xmltodict.parse(simple_xml, item_depth=2, item_callback=cb)
    # Should be called twice for <b>1</b> and <b>2</b>
    assert len(items) == 2
    assert items[0][1] == '1'
    assert items[1][1] == '2'

def test_parse_with_postprocessor(simple_xml):
    def postproc(path, key, value):
        if key == '@prop':
            return (key, value.upper())
        return (key, value)
    doc = xmltodict.parse(simple_xml, postprocessor=postproc)
    assert doc['a']['@prop'] == 'X'

def test_parse_with_force_list(xml_with_force_list):
    doc = xmltodict.parse(xml_with_force_list, force_list=('interface',))
    assert isinstance(doc['servers']['server']['interfaces']['interface'], list)
    assert doc['servers']['server']['interfaces']['interface'][0]['name'] == 'em0'

def test_parse_with_force_list_callable(xml_with_force_list):
    def force_list(path, key, value):
        return key == 'interface'
    doc = xmltodict.parse(xml_with_force_list, force_list=force_list)
    assert isinstance(doc['servers']['server']['interfaces']['interface'], list)

def test_parse_with_process_comments(xml_with_comments):
    doc = xmltodict.parse(xml_with_comments, process_comments=True)
    assert '#comment' in doc['a']['b']
    assert doc['a']['b']['#comment'] == 'b comment'
    assert '#comment' in doc['a']['b']['c']
    assert doc['a']['b']['c']['#comment'] == 'c comment'

def test_parse_with_no_attribs(simple_xml):
    doc = xmltodict.parse(simple_xml, xml_attribs=False)
    assert '@prop' not in doc['a']

def test_parse_with_strip_whitespace():
    xml = "<root>   foo   </root>"
    doc = xmltodict.parse(xml, strip_whitespace=True)
    assert doc['root'] == 'foo'

def test_parse_with_no_strip_whitespace():
    xml = "<root>   foo   </root>"
    doc = xmltodict.parse(xml, strip_whitespace=False)
    assert doc['root'] == '   foo   '

def test_parse_with_namespace(xml_with_namespaces):
    nsmap = {'http://example.com/ns': 'ns'}
    doc = xmltodict.parse(xml_with_namespaces, namespaces=nsmap, process_namespaces=True)
    # The key should be 'ns:child'
    assert 'ns:child' in doc['root']
    assert doc['root']['ns:child']['@ns:attr'] == 'val'
    assert doc['root']['ns:child']['#text'] == 'text'

def test_parse_generator(simple_xml, simple_dict):
    def gen():
        yield simple_xml[:10]
        yield simple_xml[10:]
    doc = xmltodict.parse(gen())
    assert doc == simple_dict

def test_parse_empty_element(xml_with_empty):
    doc = xmltodict.parse(xml_with_empty)
    assert doc['root']['empty'] is None

def test_parse_bool_values(xml_with_bool):
    doc = xmltodict.parse(xml_with_bool)
    assert doc['root']['flag'] == ['true', 'false']

def test_parse_multiple_roots_raises(xml_with_multiple_roots):
    with pytest.raises(Exception):
        xmltodict.parse(xml_with_multiple_roots)

def test_parse_disable_entities(monkeypatch, simple_xml):
    # Should not raise, disables entities
    doc = xmltodict.parse(simple_xml, disable_entities=True)
    assert doc['a']['@prop'] == 'x'

def test_parse_with_custom_dict_constructor(simple_xml):
    class MyDict(dict):
        pass
    doc = xmltodict.parse(simple_xml, dict_constructor=MyDict)
    assert isinstance(doc, MyDict)

def test_parse_with_namespace_separator(xml_with_namespaces):
    nsmap = {'http://example.com/ns': 'ns'}
    doc = xmltodict.parse(xml_with_namespaces, namespaces=nsmap, process_namespaces=True, namespace_separator=':')
    assert 'ns:child' in doc['root']

# --- Tests for unparse ---

def test_unparse_simple(simple_dict, simple_xml):
    xml = xmltodict.unparse(simple_dict)
    # Should contain root and both <b> elements
    assert '<a' in xml
    assert '<b>1</b>' in xml
    assert '<b>2</b>' in xml

def test_unparse_and_parse_roundtrip(simple_dict):
    xml = xmltodict.unparse(simple_dict)
    doc2 = xmltodict.parse(xml)
    # The roundtrip may not preserve order, but should be equivalent
    assert doc2['a']['@prop'] == 'x'
    assert set(doc2['a']['b']) == set(['1', '2'])

def test_unparse_with_output(simple_dict):
    buf = StringIO()
    xmltodict.unparse(simple_dict, output=buf)
    val = buf.getvalue()
    assert '<a' in val

def test_unparse_with_encoding(simple_dict):
    xml = xmltodict.unparse(simple_dict, encoding='utf-8')
    assert isinstance(xml, str)
    assert '<a' in xml

def test_unparse_with_pretty(simple_dict):
    xml = xmltodict.unparse(simple_dict, pretty=True)
    assert '\n' in xml or '\t' in xml

def test_unparse_with_short_empty_elements():
    d = {'root': {'empty': None}}
    xml = xmltodict.unparse(d, short_empty_elements=True)
    assert '<empty/>' in xml or '<empty />' in xml

def test_unparse_with_full_document_false():
    d = {'root': {'a': 'b'}}
    xml = xmltodict.unparse(d, full_document=False)
    assert '<?xml' not in xml

def test_unparse_with_multiple_roots_raises():
    d = {'a': 1, 'b': 2}
    with pytest.raises(ValueError):
        xmltodict.unparse(d)

def test_unparse_with_attrs_and_text(xml_with_attrs_and_text):
    d = xmltodict.parse(xml_with_attrs_and_text)
    xml = xmltodict.unparse(d)
    assert '<item id="1">foo</item>' in xml
    assert '<item id="2">bar</item>' in xml

def test_unparse_with_namespace():
    d = {'root': {'ns:child': {'@ns:attr': 'val', '#text': 'text'}}}
    xml = xmltodict.unparse(d, namespaces={'ns': 'http://example.com/ns'})
    assert 'ns:child' in xml or 'ns:attr' in xml

def test_unparse_with_preprocessor():
    d = {'root': {'item': '1'}}
    def preproc(key, value):
        if key == 'item':
            return ('item', str(int(value) + 1))
        return (key, value)
    xml = xmltodict.unparse(d, preprocessor=preproc)
    assert '<item>2</item>' in xml

def test_unparse_and_parse_with_comments(xml_with_comments):
    doc = xmltodict.parse(xml_with_comments, process_comments=True)
    xml = xmltodict.unparse({'a': doc['a']})
    # Comments are not preserved in unparse, but should not error
    assert '<a>' in xml

def test_unparse_with_bool_values():
    d = {'root': {'flag': [True, False]}}
    xml = xmltodict.unparse(d)
    assert '<flag>true</flag>' in xml
    assert '<flag>false</flag>' in xml

def test_unparse_with_unicode():
    d = {'root': {'greeting': 'Привет'}}
    xml = xmltodict.unparse(d)
    assert 'Привет' in xml



def test_unparse_with_custom_cdata_key():
    d = {'root': {'@id': '1', 'text': 'foo'}}
    xml = xmltodict.unparse(d, cdata_key='text')
    assert '>foo<' in xml

def test_emit_multiple_roots_raises():
    d = {'a': 1, 'b': 2}
    with pytest.raises(ValueError):
        xmltodict.unparse(d)

# --- Internal helpers ---

def test__process_namespace_no_ns():
    name = xmltodict._process_namespace('foo', None)
    assert name == 'foo'

def test__process_namespace_with_ns():
    nsmap = {'ns': 'http://example.com/ns'}
    name = xmltodict._process_namespace('ns:foo', {'ns': 'bar'}, ns_sep=':')
    assert name == 'bar:foo'

def test__process_namespace_with_attr_prefix():
    name = xmltodict._process_namespace('@ns:foo', {'ns': 'bar'}, ns_sep=':', attr_prefix='@')
    assert name == '@bar:foo'

def test__process_namespace_no_colon():
    name = xmltodict._process_namespace('foo', {'ns': 'bar'}, ns_sep=':')
    assert name == 'foo'

# --- Exception coverage ---

def test_parsing_interrupted_exception():
    with pytest.raises(xmltodict.ParsingInterrupted):
        def cb(path, item):
            return False
        xmltodict.parse("<a><b>1</b></a>", item_depth=2, item_callback=cb)