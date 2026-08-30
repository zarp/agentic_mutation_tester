import pytest
import sys
import re
import types
import uuid

import strutils

def test_camel2under():
    assert strutils.camel2under('BasicParseTest') == 'basic_parse_test'
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('') == ''


def test_split_punct_ws():
    assert strutils.split_punct_ws('First post! Hi!!!!~1    ') == ['First', 'post', 'Hi', '1']
    assert strutils.split_punct_ws('Hello, world.') == ['Hello', 'world']
    assert strutils.split_punct_ws('') == []
    assert strutils.split_punct_ws('   ') == []


def test_slugify_ascii():
    s = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    # Accept both bytes and str for Python2/3 compatibility
    assert s == b'kurt_goedel_s_pretty_cool' or s == 'kurt_goedel_s_pretty_cool'

def test_unit_len():
    assert strutils.unit_len(range(10), 'number') == '10 numbers'
    assert strutils.unit_len('aeiou', 'vowel') == '5 vowels'
    assert strutils.unit_len([], 'worry') == 'No worries'
    assert strutils.unit_len([1], 'item') == '1 item'

def test_ordinalize():
    assert strutils.ordinalize(1) == '1st'
    assert strutils.ordinalize(2) == '2nd'
    assert strutils.ordinalize(3) == '3rd'
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(21) == '21st'
    assert strutils.ordinalize('hi') == 'hi'
    assert strutils.ordinalize(1515) == '1515th'
    assert strutils.ordinalize(1, ext_only=True) == 'st'
    assert strutils.ordinalize(12, ext_only=True) == 'th'

def test_cardinalize():
    assert strutils.cardinalize('vowel', 1) == 'vowel'
    assert strutils.cardinalize('Wish', 3) == 'Wishes'
    assert strutils.cardinalize('enemy', 2) == 'enemies'
    assert strutils.cardinalize('Sheep', 2) == 'Sheep'



def test_find_hashtags():
    assert strutils.find_hashtags('#atag http://asite/#ananchor') == ['atag']
    assert strutils.find_hashtags('no hashtags here') == []
    assert strutils.find_hashtags('multiple #tags #here') == ['tags', 'here']
    # Unicode full-width hash
    assert strutils.find_hashtags(u'＃タグ') == ['タグ']

def test_a10n():
    assert strutils.a10n('abbreviation') == 'a10n'
    assert strutils.a10n('internationalization') == 'i18n'
    assert strutils.a10n('hi') == 'hi'
    assert strutils.a10n('') == ''

def test_strip_ansi():
    s = '\x1b[0m\x1b[1;36mart\x1b[46;34m'
    assert strutils.strip_ansi(s) == 'art'
    # Test with bytes
    s_bytes = b'\x1b[0m\x1b[1;36mart\x1b[46;34m'
    result = strutils.strip_ansi(s_bytes)
    assert isinstance(result, (bytes, bytearray))
    assert result.decode('utf-8') == 'art'
    # Test with no ansi
    assert strutils.strip_ansi('plain text') == 'plain text'


def test_is_ascii():
    assert strutils.is_ascii('Beyonce') is True
    assert strutils.is_ascii(b'Beyonce') is True
    assert strutils.is_ascii('Beyoncé') is False
    assert strutils.is_ascii(b'Beyonc\xc3\xa9') is False
    with pytest.raises(ValueError):
        strutils.is_ascii(123)


def test_html2text():
    html = u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>'
    expected = u'Test &(\u0394\u03b7\u03bc\u03ce)'
    assert strutils.html2text(html) == expected
    # Test with unknown entity
    html = u'<p>&unknown;</p>'
    assert strutils.html2text(html) == '&unknown;'

def test_gunzip_bytes_and_gzip_bytes():
    # _EMPTY_GZIP_BYTES and _NON_EMPTY_GZIP_BYTES are module constants
    empty = strutils._EMPTY_GZIP_BYTES
    non_empty = strutils._NON_EMPTY_GZIP_BYTES
    assert strutils.gunzip_bytes(empty) == b''
    assert strutils.gunzip_bytes(non_empty).rstrip() == b'bytesahoy!'
    # Test gzip_bytes roundtrip
    data = b'a' * 10000
    gz = strutils.gzip_bytes(data)
    assert isinstance(gz, bytes)
    assert strutils.gunzip_bytes(gz) == data

def test_iter_splitlines():
    assert list(strutils.iter_splitlines('\nhi\nbye\n')) == ['', 'hi', 'bye', '']
    assert list(strutils.iter_splitlines('\r\nhi\rbye\r\n')) == ['', 'hi', 'bye', '']
    assert list(strutils.iter_splitlines('')) == []
    assert list(strutils.iter_splitlines('one line')) == ['one line']

def test_indent():
    text = 'a\nb\n\nc'
    expected = '  a\n  b\n\n  c'
    assert strutils.indent(text, '  ') == expected
    # Test with custom newline
    assert strutils.indent('a\nb', '>', newline='|') == '>a|>b'
    # Test with key that indents only lines with 'a'
    text = 'a\nb\nc'
    result = strutils.indent(text, '>', key=lambda l: 'a' in l)
    assert result == '>a\nb\nc'

def test_is_uuid():
    v4 = 'e682ccca-5a4c-4ef2-9711-73f9ad1e15ea'
    v1 = '0221f0d9-d4b9-11e5-a478-10ddb1c2feb9'
    assert strutils.is_uuid(v4)
    assert not strutils.is_uuid(v1)
    assert strutils.is_uuid(v1, version=1)
    assert strutils.is_uuid(uuid.UUID(v4))
    assert not strutils.is_uuid('not-a-uuid')
    assert not strutils.is_uuid(12345)

def test_escape_shell_args_sh():
    args = ['aa', '[bb]', "cc'cc", 'dd"dd']
    expected = "aa '[bb]' 'cc'\"'\"'cc' 'dd\"dd'"
    assert strutils.escape_shell_args(args, style='sh') == expected
    # Default style on non-win32 should be sh
    if sys.platform != 'win32':
        assert strutils.escape_shell_args(args) == expected

def test_escape_shell_args_cmd():
    args = ['aa', '[bb]', "cc'cc", 'dd\"dd']
    expected = 'aa [bb] cc\'cc dd\\"dd'
    assert strutils.escape_shell_args(args, style='cmd') == expected
    # Default style on win32 should be cmd
    if sys.platform == 'win32':
        assert strutils.escape_shell_args(args) == expected

def test_escape_shell_args_invalid():
    with pytest.raises(ValueError):
        strutils.escape_shell_args(['foo'], style='invalid')

def test_args2sh():
    args = ['aa', '[bb]', "cc'cc", 'dd"dd']
    expected = "aa '[bb]' 'cc'\"'\"'cc' 'dd\"dd'"
    assert strutils.args2sh(args) == expected
    # Empty arg
    assert strutils.args2sh(['']) == "''"
    # No special chars
    assert strutils.args2sh(['abc', 'def']) == 'abc def'

def test_args2cmd():
    args = ['aa', '[bb]', "cc'cc", 'dd"dd']
    expected = 'aa [bb] cc\'cc dd\\"dd'
    assert strutils.args2cmd(args) == expected
    # Arg with spaces
    assert strutils.args2cmd(['foo bar']) == '"foo bar"'
    # Arg with tab
    assert strutils.args2cmd(['foo\tbar']) == '"foo\tbar"'
    # Empty arg
    assert strutils.args2cmd(['']) == '""'

def test_parse_int_list():
    assert strutils.parse_int_list('1,3,5-8,10-11,15') == [1, 3, 5, 6, 7, 8, 10, 11, 15]
    assert strutils.parse_int_list('') == []
    assert strutils.parse_int_list('2-4') == [2, 3, 4]
    assert strutils.parse_int_list('1,,2') == [1, 2]
    assert strutils.parse_int_list('5') == [5]


def test_complement_int_list():
    # Examples from docstring
    assert strutils.complement_int_list('1,3,5-8,10-11,15') == '0,2,4,9,12-14'
    assert strutils.complement_int_list('1,3,5-8,10-11,15', range_start=1) == '2,4,9,12-14'
    assert strutils.complement_int_list('1,3,5-8,10-11,15', range_end=15) == '0,2,4,9,12-14'
    assert strutils.complement_int_list('1,3,5-8,10-11,15', range_end=13) == '0,2,4,9,12'
    assert strutils.complement_int_list('1,3,5-8', range_start=2, range_end=3) == '2'
    assert strutils.complement_int_list('1,3,5-8', range_start=-10, range_end=-5) == ''
    assert strutils.complement_int_list('1,3,5-8', range_start=20, range_end=10) == ''
    assert strutils.complement_int_list('') == ''

def test_int_ranges_from_int_list():
    assert strutils.int_ranges_from_int_list('1,3,5-8,10-11,15') == ((1,1),(3,3),(5,8),(10,11),(15,15))
    assert strutils.int_ranges_from_int_list('1') == ((1,1),)
    assert strutils.int_ranges_from_int_list('') == ()
    assert strutils.int_ranges_from_int_list('2-4') == ((2,4),)

def test_MultiReplace_dict():
    m = strutils.MultiReplace({'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'})
    s = 'The foo bar cat ate a bat'
    assert m.sub(s) == 'The zoo bar hat ate a kraken'
    # Order is not guaranteed for dict, but all should be replaced

def test_MultiReplace_list():
    m = strutils.MultiReplace([
        ('foo', 'zoo'),
        ('cat', 'hat'),
        ('bat', 'kraken')
    ])
    s = 'The foo bar cat ate a bat'
    assert m.sub(s) == 'The zoo bar hat ate a kraken'

def test_MultiReplace_regex():
    m = strutils.MultiReplace([
        (r'\bfoo\b', 'zoo'),
        (r'\bcat\b', 'hat'),
        (r'\bbat\b', 'kraken')
    ], regex=True)
    s = 'The foo bar cat ate a bat'
    assert m.sub(s) == 'The zoo bar hat ate a kraken'
    # Should not replace 'food'
    s2 = 'food batcat'
    assert m.sub(s2) == 'food batcat'

def test_multi_replace():
    s = 'The foo bar cat ate a bat'
    result = strutils.multi_replace(
        s,
        {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
    )
    assert result == 'The zoo bar hat ate a kraken'

def test_unwrap_text():
    text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    expected = 'Short lines wrapped small.\n\nAnother paragraph.'
    assert strutils.unwrap_text(text) == expected
    # Test with ending=None
    result = strutils.unwrap_text(text, ending=None)
    assert result == ['Short lines wrapped small.', 'Another paragraph.']
    # Test with only one paragraph
    text2 = "One\nparagraph\nonly."
    assert strutils.unwrap_text(text2) == 'One paragraph only.'
    # Test with empty string
    assert strutils.unwrap_text('') == ''