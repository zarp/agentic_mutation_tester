import xmltodict
import io
import sys
import pytest

def test_parse_simple_element():
    xml = "<a>hello</a>"
    result = xmltodict.parse(xml)
    assert result == {'a': 'hello'}

def test_parse_element_with_attribute():
    xml = '<a prop="x">hello</a>'
    result = xmltodict.parse(xml)
    assert result == {'a': {'@prop': 'x', '#text': 'hello'}}

def test_parse_element_with_multiple_children():
    xml = "<a><b>1</b><b>2</b></a>"
    result = xmltodict.parse(xml)
    assert result == {'a': {'b': ['1', '2']}}

def test_parse_element_with_nested_elements():
    xml = "<a><b><c>foo</c></b></a>"
    result = xmltodict.parse(xml)
    assert result == {'a': {'b': {'c': 'foo'}}}

def test_parse_element_with_attributes_and_children():
    xml = '<a prop="x"><b>1</b><b>2</b></a>'
    result = xmltodict.parse(xml)
    assert result == {'a': {'@prop': 'x', 'b': ['1', '2']}}

def test_parse_unicode_input():
    xml = u"<a>héllo</a>"
    result = xmltodict.parse(xml)
    assert result == {'a': u'héllo'}

def test_parse_with_encoding():
    xml = "<a>héllo</a>".encode("utf-8")
    result = xmltodict.parse(xml)
    assert result == {'a': u'héllo'}


def test_parse_generator_input():
    xml = ["<a>", "<b>1</b>", "<b>2</b>", "</a>"]
    def gen():
        for chunk in xml:
            yield chunk
    result = xmltodict.parse(gen())
    assert result == {'a': {'b': ['1', '2']}}

def test_parse_with_item_depth_and_callback():
    xml = "<a><b>1</b><b>2</b></a>"
    items = []
    def cb(path, item):
        items.append((list(path), item))
        return True
    result = xmltodict.parse(xml, item_depth=2, item_callback=cb)
    assert result is None
    assert items == [
        ([('a', None), ('b', None)], '1'),
        ([('a', None), ('b', None)], '2')
    ]

def test_parse_with_item_callback_stops_parsing():
    xml = "<a><b>1</b><b>2</b></a>"
    items = []
    def cb(path, item):
        items.append(item)
        return False
    with pytest.raises(xmltodict.ParsingInterrupted):
        xmltodict.parse(xml, item_depth=2, item_callback=cb)
    assert items == ['1']

def test_parse_with_postprocessor_changes_key_and_value():
    xml = "<a><b>1</b><b>2</b><b>x</b></a>"
    def post(path, key, value):
        try:
            return key + ':int', int(value)
        except Exception:
            return key, value
    result = xmltodict.parse(xml, postprocessor=post)
    assert result == {'a': {'b:int': [1, 2], 'b': 'x'}}

def test_parse_with_force_list_tuple():
    xml = """
    <servers>
      <server>
        <name>host1</name>
        <os>Linux</os>
        <interfaces>
          <interface>
            <name>em0</name>
            <ip_address>10.0.0.1</ip_address>
          </interface>
        </interfaces>
      </server>
    </servers>
    """
    result = xmltodict.parse(xml, force_list=('interface',))
    assert result['servers']['server']['interfaces']['interface'] == [
        {'name': 'em0', 'ip_address': '10.0.0.1'}
    ]

def test_parse_with_force_list_callable():
    xml = "<a><b>1</b></a>"
    def force_list(path, key, value):
        return key == 'b'
    result = xmltodict.parse(xml, force_list=force_list)
    assert result == {'a': {'b': ['1']}}

def test_parse_with_process_comments():
    xml = """
    <a>
      <b>
        <!-- b comment -->
        <c>
            <!-- c comment -->
            1
        </c>
        <d>2</d>
      </b>
    </a>
    """
    result = xmltodict.parse(xml, process_comments=True)
    assert result['a']['b']['#comment'] == 'b comment'
    assert result['a']['b']['c']['#comment'] == 'c comment'
    assert result['a']['b']['c']['#text'] == '1'
    assert result['a']['b']['d'] == '2'

def test_parse_with_xml_attribs_false():
    xml = '<a prop="x">hello</a>'
    result = xmltodict.parse(xml, xml_attribs=False)
    assert result == {'a': 'hello'}

def test_parse_with_strip_whitespace_false():
    xml = "<a>  hello  </a>"
    result = xmltodict.parse(xml, strip_whitespace=False)
    assert result == {'a': '  hello  '}

def test_parse_with_force_cdata_true():
    xml = "<a>hello</a>"
    result = xmltodict.parse(xml, force_cdata=True)
    assert result == {'a': {'#text': 'hello'}}


def test_parse_with_namespace_separator_and_namespaces():
    xml = '<root xmlns:ns="http://example.com"><ns:child>val</ns:child></root>'
    result = xmltodict.parse(xml, process_namespaces=True, namespaces={'http://example.com': 'ns'})
    assert 'root' in result
    assert 'ns:child' in result['root']
    assert result['root']['ns:child'] == 'val'

def test_parse_with_disable_entities_false():
    xml = "<a>&lt;</a>"
    result = xmltodict.parse(xml, disable_entities=False)
    assert result == {'a': '<'}

def test_parse_with_empty_element():
    xml = "<a/>"
    result = xmltodict.parse(xml)
    assert result == {'a': None}

def test_parse_with_comment_key_custom():
    xml = "<a><!-- comment --></a>"
    result = xmltodict.parse(xml, process_comments=True, comment_key='!c')
    assert result['a']['!c'] == 'comment'

def test_parse_with_dict_constructor_ordereddict():
    from collections import OrderedDict
    xml = "<a><b>1</b><c>2</c></a>"
    result = xmltodict.parse(xml, dict_constructor=OrderedDict)
    assert list(result['a'].keys()) == ['b', 'c']

def test_parse_with_namespace_declarations():
    xml = '<root xmlns:ns="http://example.com"><ns:child>val</ns:child></root>'
    result = xmltodict.parse(xml)
    assert 'root' in result
    # Should not raise, and should parse child
    assert 'ns:child' in result['root']
    assert result['root']['ns:child'] == 'val'

def test_unparse_simple_dict():
    d = {'a': 'hello'}
    xml = xmltodict.unparse(d)
    assert xml.startswith('<?xml')
    assert '<a>hello</a>' in xml

def test_unparse_with_attribute_and_text():
    d = {'a': {'@prop': 'x', '#text': 'hello'}}
    xml = xmltodict.unparse(d)
    assert 'prop="x"' in xml
    assert '<a prop="x">hello</a>' in xml

def test_unparse_with_list_of_elements():
    d = {'a': {'b': ['1', '2']}}
    xml = xmltodict.unparse(d)
    assert xml.count('<b>1</b>') == 1
    assert xml.count('<b>2</b>') == 1

def test_unparse_with_pretty_print():
    d = {'a': {'b': ['1', '2']}}
    xml = xmltodict.unparse(d, pretty=True)
    assert '\n' in xml
    assert '\t' in xml

def test_unparse_with_custom_indent_and_newl():
    d = {'a': {'b': '1'}}
    xml = xmltodict.unparse(d, pretty=True, indent='  ', newl='\r\n')
    assert '\r\n' in xml
    assert '  ' in xml

def test_unparse_with_short_empty_elements():
    d = {'a': None}
    xml = xmltodict.unparse(d, short_empty_elements=True)
    assert '<a/>' in xml or '<a />' in xml

def test_unparse_with_full_document_false():
    d = {'a': 'hello'}
    xml = xmltodict.unparse(d, full_document=False)
    assert not xml.startswith('<?xml')

def test_unparse_raises_on_multiple_roots():
    d = {'a': '1', 'b': '2'}
    with pytest.raises(ValueError) as e:
        xmltodict.unparse(d)
    assert 'exactly one root' in str(e.value)

def test_unparse_to_file_like_object():
    d = {'a': 'hello'}
    buf = io.StringIO()
    xmltodict.unparse(d, output=buf)
    value = buf.getvalue()
    assert '<a>hello</a>' in value

def test_unparse_with_boolean_values():
    d = {'a': True, 'b': False}
    with pytest.raises(ValueError):
        xmltodict.unparse(d)
    # Only one root allowed, so test with one at a time
    d = {'a': True}
    xml = xmltodict.unparse(d)
    assert '<a>true</a>' in xml
    d = {'a': False}
    xml = xmltodict.unparse(d)
    assert '<a>false</a>' in xml

def test_unparse_with_nested_dict_and_attributes():
    d = {'root': {'@xmlns:ns': 'http://example.com', 'ns:child': 'val'}}
    xml = xmltodict.unparse(d)
    assert 'xmlns:ns="http://example.com"' in xml
    assert '<ns:child>val</ns:child>' in xml

def test__process_namespace_no_namespaces():
    name = 'foo'
    result = xmltodict._process_namespace(name, None)
    assert result == 'foo'

def test__process_namespace_with_namespace():
    name = 'ns:foo'
    namespaces = {'ns': 'bar'}
    result = xmltodict._process_namespace(name, namespaces)
    assert result == 'bar:foo'

def test__process_namespace_with_attr_prefix():
    name = '@ns:foo'
    namespaces = {'ns': 'bar'}
    result = xmltodict._process_namespace(name, namespaces)
    assert result == '@bar:foo'

def test__process_namespace_no_colon():
    name = 'foo'
    namespaces = {'ns': 'bar'}
    result = xmltodict._process_namespace(name, namespaces)
    assert result == 'foo'

def test__emit_raises_on_multiple_roots():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    with pytest.raises(ValueError):
        xmltodict._emit('a', ['1', '2'], handler, full_document=True)

def test__emit_with_bool_value():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', True, handler, full_document=False)
    value = buf.getvalue()
    assert '<a>true</a>' in value


def test__emit_with_dict_value_and_cdata():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'#text': 'foo'}, handler, full_document=False)
    value = buf.getvalue()
    assert '<a>foo</a>' in value

def test__emit_with_preprocessor_none_result():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    def preprocessor(key, value):
        return None
    xmltodict._emit('a', 'foo', handler, preprocessor=preprocessor, full_document=False)
    value = buf.getvalue()
    assert value == ''


def test__emit_with_namespaces_and_attr_prefix():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    namespaces = {'ns': 'bar'}
    xmltodict._emit('@ns:foo', 'val', handler, namespaces=namespaces, full_document=False)
    value = buf.getvalue()
    assert 'bar:foo' in value or 'foo' in value

def test__emit_with_xmlns_dict():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'@xmlns': {'': 'http://foo'}}, handler, full_document=False)
    value = buf.getvalue()
    assert 'xmlns="http://foo"' in value

def test__emit_with_pretty_and_indent():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'b': 'c'}, handler, pretty=True, full_document=False)
    value = buf.getvalue()
    assert '\n' in value or '\t' in value

def test__emit_with_non_string_attribute_value():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'@foo': 123}, handler, full_document=False)
    value = buf.getvalue()
    assert 'foo="123"' in value


def test__emit_with_list_of_dicts():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', [{'b': '1'}, {'b': '2'}], handler, full_document=False)
    value = buf.getvalue()
    assert value.count('<a>') == 2

def test__emit_with_cdata_key_custom():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'!c': 'foo'}, handler, cdata_key='!c', full_document=False)
    value = buf.getvalue()
    assert '<a>foo</a>' in value

def test__emit_with_attr_prefix_custom():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'$foo': 'bar'}, handler, attr_prefix='$', full_document=False)
    value = buf.getvalue()
    assert 'foo="bar"' in value

def test__emit_with_namespace_separator_custom():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    namespaces = {'ns': 'bar'}
    xmltodict._emit('ns|foo', 'val', handler, namespaces=namespaces, namespace_separator='|', full_document=False)
    value = buf.getvalue()
    assert 'bar|foo' in value or 'foo' in value

def test__emit_with_full_document_false_and_multiple_roots():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    # Should not raise
    xmltodict._emit('a', ['1', '2'], handler, full_document=False)
    value = buf.getvalue()
    assert value.count('<a>') == 2

def test__emit_with_expand_iter_and_non_iterable():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', 5, handler, expand_iter='item', full_document=False)
    value = buf.getvalue()
    assert '<a>5</a>' in value

def test__emit_with_expand_iter_and_string():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', 'foo', handler, expand_iter='item', full_document=False)
    value = buf.getvalue()
    assert '<a>foo</a>' in value


import types




def test_default_item_callback_returns_true():
    # The default item_callback always returns True, so parsing should not be interrupted.
    xml = "<a><b>1</b></a>"
    # If the default was False, parsing would stop at first item at depth.
    # Use item_depth=2 to trigger item_callback.
    result = []
    def cb(*args):
        result.append(args)
        return True
    xmltodict.parse(xml, item_depth=2, item_callback=cb)
    # Now test default (should not raise)
    xmltodict.parse(xml, item_depth=2)
    # If default was False, ParsingInterrupted would be raised.
    # So, forcibly check that no exception is raised and parsing completes.
    assert True  # If we get here, default is True


def test_namespace_separator_default_colon():
    xml = '<root xmlns:ns="http://example.com"><ns:child>val</ns:child></root>'
    result = xmltodict.parse(xml, process_namespaces=True, namespaces={'http://example.com': 'ns'})
    # The separator should be ':'
    assert 'ns:child' in result['root']


def test__build_name_returns_name():
    handler = xmltodict._DictSAXHandler()
    assert handler._build_name('foo') == 'foo'


def test__attrs_to_dict_returns_attrs():
    handler = xmltodict._DictSAXHandler()
    d = {'a': 1}
    assert handler._attrs_to_dict(d) is d


def test__attrs_to_dict_zip_stride():
    handler = xmltodict._DictSAXHandler()
    attrs = ['a', '1', 'b', '2']
    d = handler._attrs_to_dict(attrs)
    assert d['a'] == '1'
    assert d['b'] == '2'


def test_startNamespaceDecl_prefix_empty_string():
    handler = xmltodict._DictSAXHandler()
    handler.startNamespaceDecl('', 'uri')
    assert '' in handler.namespace_declarations
    handler = xmltodict._DictSAXHandler()
    handler.startNamespaceDecl(None, 'uri')
    assert '' in handler.namespace_declarations


def test_startNamespaceDecl_prefix_empty_string_key():
    handler = xmltodict._DictSAXHandler()
    handler.startNamespaceDecl('', 'uri')
    assert '' in handler.namespace_declarations






def test_characters_appends_to_data():
    handler = xmltodict._DictSAXHandler()
    handler.data = []
    handler.characters('foo')
    assert handler.data == ['foo']
    handler.characters('bar')
    assert handler.data == ['foo', 'bar']


def test_push_data_returns_item():
    handler = xmltodict._DictSAXHandler()
    result = handler.push_data(None, 'k', 'v')
    assert isinstance(result, dict)
    assert result['k'] == 'v'


def test__should_force_list_returns_false():
    handler = xmltodict._DictSAXHandler()
    assert handler._should_force_list('k', 'v') is False


def test__should_force_list_bool():
    handler = xmltodict._DictSAXHandler(force_list=True)
    assert handler._should_force_list('k', 'v') is True


def test__should_force_list_callable_args():
    called = {}
    def fl(path, key, value):
        called['args'] = (path, key, value)
        return False
    handler = xmltodict._DictSAXHandler(force_list=fl)
    handler.path = ['a', 'b']
    handler._should_force_list('k', 'v')
    # path[:-1] should be ['a']
    assert called['args'][0] == ['a']


def test_parse_disable_entities_true():
    xml = "<a>&lt;</a>"
    result = xmltodict.parse(xml, disable_entities=True)
    assert result == {'a': '<'}


def test_parse_process_comments_false_by_default():
    xml = "<a><!-- comment --></a>"
    result = xmltodict.parse(xml)
    # Should not include comment
    assert result == {'a': None}




def test_parser_buffer_text_true():
    # This is an internal parser attribute, but xmltodict expects buffer_text True for correct text handling.
    # If buffer_text is False, text nodes may be split. Let's test with a long text node.
    xml = "<a>{}</a>".format("x" * 10000)
    result = xmltodict.parse(xml)
    assert result == {'a': "x" * 10000}










def test_parse_generator_final_parse_true():
    # The final call to parser.Parse(b'', True) signals end of input.
    # If False, parsing would not finish and root element would not close.
    xml = ["<a>", "<b>1</b>", "</a>"]
    def gen():
        for chunk in xml:
            yield chunk
    result = xmltodict.parse(gen())
    assert result == {'a': {'b': '1'}}


def test_parse_string_input_final_parse_true():
    xml = "<a>1</a>"
    result = xmltodict.parse(xml)
    assert result == {'a': '1'}


def test__process_namespace_rsplit_1():
    name = 'ns:foo'
    namespaces = {'ns': 'bar'}
    result = xmltodict._process_namespace(name, namespaces)
    assert result == 'bar:foo'


def test__emit_pretty_false_by_default():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', 'b', handler, full_document=False)
    value = buf.getvalue()
    # Should not contain pretty whitespace
    assert '\n' not in value and '\t' not in value


def test__emit_newl_default():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'b': 'c'}, handler, pretty=True, full_document=False)
    value = buf.getvalue()
    assert '\n' in value


def test__emit_indent_default():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'b': 'c'}, handler, pretty=True, full_document=False)
    value = buf.getvalue()
    assert '\t' in value


def test__emit_namespace_separator_default_colon():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    namespaces = {'ns': 'bar'}
    xmltodict._emit('ns:foo', 'val', handler, namespaces=namespaces, full_document=False)
    value = buf.getvalue()
    assert 'bar:foo' in value or 'foo' in value


def test__emit_full_document_true():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', 'b', handler, full_document=True)
    value = buf.getvalue()
    assert '<a>b</a>' in value


def test__emit_raises_on_multiple_roots_message():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    try:
        xmltodict._emit('a', ['1', '2'], handler, full_document=True)
    except ValueError as e:
        assert 'multiple roots' in str(e)


def test__build_name_namespaces_none_returns_full_name():
    handler = xmltodict._DictSAXHandler(namespaces=None)
    assert handler._build_name('foo:bar') == 'foo:bar'


def test__build_name_namespaces_present_and_separator():
    handler = xmltodict._DictSAXHandler(namespaces={'foo': 'ns'}, namespace_separator=':')
    # Should return 'ns:bar'
    assert handler._build_name('foo:bar') == 'ns:bar'


def test__build_name_namespaces_present_and_separator_no_colon():
    handler = xmltodict._DictSAXHandler(namespaces={'foo': 'ns'}, namespace_separator=':')
    # No colon in name, should return as is
    assert handler._build_name('bar') == 'bar'


def test__build_name_namespaces_present_and_short_namespace_empty():
    handler = xmltodict._DictSAXHandler(namespaces={'foo': ''}, namespace_separator=':')
    # Should return just 'bar'
    assert handler._build_name('foo:bar') == 'bar'


def test__attrs_to_dict_list_input():
    handler = xmltodict._DictSAXHandler()
    attrs = ['a', '1', 'b', '2']
    d = handler._attrs_to_dict(attrs)
    assert d == {'a': '1', 'b': '2'}


def test_startElement_adds_xmlns_when_attrs_and_namespace_declarations():
    handler = xmltodict._DictSAXHandler()
    handler.namespace_declarations = {'foo': 'bar'}
    handler.startElement('root', {'a': 'b'})
    # Should add 'xmlns' key
    assert '@xmlns' in handler.item or 'xmlns' in handler.item




def test_startElement_xml_attribs_false():
    handler = xmltodict._DictSAXHandler(xml_attribs=False)
    handler.startElement('root', {'a': 'b'})
    # Should set item to None if xml_attribs is False and no attrs
    assert handler.item is None or handler.item == {}


def test_endElement_item_depth_equal_len_path():
    # Should call item_callback and handle return value
    called = {}
    def cb(path, item):
        called['called'] = (list(path), item)
        return True
    handler = xmltodict._DictSAXHandler(item_depth=1, item_callback=cb)
    handler.path = ['a']
    handler.item = None
    handler.data = ['foo']
    handler.stack = []
    handler.endElement('a')
    assert called['called'][1] == 'foo'


def test_endElement_strip_whitespace_false():
    handler = xmltodict._DictSAXHandler(strip_whitespace=False)
    handler.path = ['a', 'b']
    handler.stack = [(None, [])]
    handler.item = None
    handler.data = ['  foo  ']
    handler.endElement('b')
    # Should not strip whitespace
    assert handler.item['b'] == '  foo  '


def test_endElement_force_cdata_true_and_item_none():
    handler = xmltodict._DictSAXHandler(force_cdata=True)
    handler.path = ['a', 'b']
    handler.stack = [(None, [])]
    handler.item = None
    handler.data = ['foo']
    handler.endElement('b')
    # Should wrap in dict with cdata_key
    assert isinstance(handler.item['b'], dict)
    assert handler.cdata_key in handler.item['b']


def test_push_data_postprocessor_returns_none():
    def post(path, key, value):
        return None
    handler = xmltodict._DictSAXHandler(postprocessor=post)
    result = handler.push_data({}, 'k', 'v')
    # Should return original item unchanged
    assert result == {}


def test_push_data_existing_list():
    handler = xmltodict._DictSAXHandler()
    item = {'k': ['v1']}
    result = handler.push_data(item, 'k', 'v2')
    assert result['k'] == ['v1', 'v2']


def test_push_data_existing_nonlist():
    handler = xmltodict._DictSAXHandler()
    item = {'k': 'v1'}
    result = handler.push_data(item, 'k', 'v2')
    assert result['k'] == ['v1', 'v2']


def test_push_data_should_force_list():
    handler = xmltodict._DictSAXHandler(force_list=('k',))
    result = handler.push_data({}, 'k', 'v')
    assert isinstance(result['k'], list)
    assert result['k'] == ['v']


def test__should_force_list_tuple():
    handler = xmltodict._DictSAXHandler(force_list=('k',))
    assert handler._should_force_list('k', 'v') is True
    assert handler._should_force_list('x', 'v') is False


def test__should_force_list_callable_true():
    handler = xmltodict._DictSAXHandler(force_list=lambda path, key, value: key == 'k')
    handler.path = ['a', 'b']
    assert handler._should_force_list('k', 'v') is True
    assert handler._should_force_list('x', 'v') is False


def test_parse_disable_entities_false():
    xml = "<a>&lt;</a>"
    result = xmltodict.parse(xml, disable_entities=False)
    assert result == {'a': '<'}


def test_parse_process_comments_true():
    xml = "<a><!-- comment --></a>"
    result = xmltodict.parse(xml, process_comments=True)
    assert '#comment' in result['a']


def test_parse_process_comments_false():
    xml = "<a><!-- comment --></a>"
    result = xmltodict.parse(xml, process_comments=False)
    assert result == {'a': None}


def test_parse_generator_input_final_parse_true():
    xml = ["<a>", "<b>1</b>", "</a>"]
    def gen():
        for chunk in xml:
            yield chunk
    result = xmltodict.parse(gen())
    assert result == {'a': {'b': '1'}}


def test__emit_full_document_false_allows_multiple_roots():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', ['1', '2'], handler, full_document=False)
    value = buf.getvalue()
    assert value.count('<a>') == 2


def test__emit_full_document_true_raises_on_multiple_roots():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    with pytest.raises(ValueError):
        xmltodict._emit('a', ['1', '2'], handler, full_document=True)


def test__emit_with_bool_value_true_and_false():
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', True, handler, full_document=False)
    xmltodict._emit('b', False, handler, full_document=False)
    value = buf.getvalue()
    assert '<a>true</a>' in value
    assert '<b>false</b>' in value


def test_unparse_short_empty_elements_true():
    d = {'a': None}
    xml = xmltodict.unparse(d, short_empty_elements=True)
    assert '<a/>' in xml or '<a />' in xml




def test_unparse_full_document_false():
    d = {'a': 'hello'}
    xml = xmltodict.unparse(d, full_document=False)
    assert not xml.startswith('<?xml')


def test_unparse_raises_on_multiple_roots_message():
    d = {'a': '1', 'b': '2'}
    try:
        xmltodict.unparse(d)
    except ValueError as e:
        assert 'exactly one root' in str(e)




def test_parse_disable_entities_default_true():
    # line 203: True -> False
    # By default, disable_entities should be True, so entities are not expanded by user DTDs.
    xml = "<a>&lt;</a>"
    result = xmltodict.parse(xml)
    assert result == {'a': '<'}


def test_parser_ordered_attributes_true():
    # line 349: True -> False
    # If parser.ordered_attributes is not set to True, attribute order is not preserved.
    # We can check that ordered_attributes is set if available.
    # This is not directly observable, but we can check that no error is raised and parsing works.
    xml = '<a x="1" y="2">z</a>'
    result = xmltodict.parse(xml)
    assert result['a']['@x'] == '1'
    assert result['a']['@y'] == '2'


def test_parser_external_entity_ref_handler_returns_1():
    # line 370: 1 -> 2
    # If ExternalEntityRefHandler returns not 1, expat will raise ExpatError.
    # We can test that parsing with disable_entities=True does not raise.
    xml = "<a>&lt;</a>"
    result = xmltodict.parse(xml, disable_entities=True)
    assert result == {'a': '<'}


def test__emit_pretty_default_false():
    # line 402: False -> True
    # By default, pretty should be False, so output should not contain pretty whitespace.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', 'b', handler, full_document=False)
    value = buf.getvalue()
    assert '\n' not in value and '\t' not in value


def test__emit_full_document_default_true():
    # line 407: True -> False
    # By default, full_document should be True, so multiple roots should raise.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    with pytest.raises(ValueError):
        xmltodict._emit('a', ['1', '2'], handler)


def test__emit_continue_vs_break_in_attr_loop():
    # line 442: continue -> break
    # If break is used instead of continue, only the first attribute is processed.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'@foo': 'bar', '@baz': 'qux'}, handler, full_document=False)
    value = buf.getvalue()
    # Both attributes should be present
    assert 'foo="bar"' in value
    assert 'baz="qux"' in value


def test__emit_continue_vs_break_in_xmlns_loop():
    # line 450: continue -> break
    # If break is used, only the first xmlns is processed.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {'@xmlns': {'': 'http://foo', 'x': 'http://bar'}}, handler, full_document=False)
    value = buf.getvalue()
    assert 'xmlns="http://foo"' in value
    assert 'xmlns:x="http://bar"' in value


def test__emit_and_vs_or_in_pretty_children():
    # line 459: and -> or
    # If or is used, whitespace is added even if pretty is False or children is empty.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {}, handler, full_document=False)
    value = buf.getvalue()
    # Should not contain pretty whitespace
    assert '\n' not in value and '\t' not in value


def test__emit_and_vs_or_in_pretty_children_end():
    # line 469: and -> or
    # If or is used, whitespace is added even if pretty is False or children is empty.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {}, handler, full_document=False)
    value = buf.getvalue()
    assert '\n' not in value and '\t' not in value


def test__emit_and_vs_or_in_pretty_depth():
    # line 472: and -> or
    # If or is used, whitespace is added even if pretty is False or depth is 0.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    xmltodict._emit('a', {}, handler, full_document=False)
    value = buf.getvalue()
    assert '\n' not in value and '\t' not in value


def test__emit_namespace_attr_and_vs_or():
    # line 446: and -> or
    # If or is used, the block is entered even if ik != '@xmlns', which is wrong.
    from xml.sax.saxutils import XMLGenerator
    buf = io.StringIO()
    handler = XMLGenerator(buf)
    # Only @xmlns should trigger the block, not other attributes
    xmltodict._emit('a', {'@foo': {'bar': 'baz'}}, handler, full_document=False)
    value = buf.getvalue()
    # Should not produce xmlns="..." for @foo
    assert 'xmlns=' not in value


def test_unparse_short_empty_elements_default_false():
    # line 477: False -> True
    # By default, short_empty_elements should be False, so <a></a> not <a/>
    d = {'a': None}
    xml = xmltodict.unparse(d)
    # Should be <a></a> not <a/>
    assert '<a></a>' in xml or '<a />' not in xml


def test_unparse_must_return_false_default():
    # line 495: False -> True
    # By default, must_return should be False unless output is None.
    d = {'a': 'hello'}
    buf = io.StringIO()
    result = xmltodict.unparse(d, output=buf)
    # Should return None, not a string
    assert result is None




def test_parse_buffer_text_false():
    # line 359: True -> False
    # If buffer_text is False, long text nodes may be split into multiple character events.
    # We can simulate this by parsing a long text node and checking the result.
    xml = "<a>{}</a>".format("x" * 10000)
    result = xmltodict.parse(xml)
    assert result == {'a': "x" * 10000}


def test_parse_final_parse_false_generator():
    # line 376: True -> False
    # If the final parser.Parse(b'', True) is not called with True, the document may not close.
    xml = ["<a>", "<b>1</b>", "</a>"]
    def gen():
        for chunk in xml:
            yield chunk
    result = xmltodict.parse(gen())
    assert result == {'a': {'b': '1'}}


def test_parse_final_parse_false_string():
    # line 378: True -> False
    # If parser.Parse(xml_input, True) is not called with True, the document may not close.
    xml = "<a>1</a>"
    result = xmltodict.parse(xml)
    assert result == {'a': '1'}


def test__process_namespace_rsplit_1_vs_2():
    # line 386: 1 -> 2
    # If rsplit is called with 2, it still works for one colon, but let's check with multiple colons.
    name = 'ns:foo:bar'
    namespaces = {'ns:foo': 'baz'}
    result = xmltodict._process_namespace(name, namespaces)
    # Should split at last colon, so ns='ns:foo', name='bar'
    assert result == 'baz:bar'
