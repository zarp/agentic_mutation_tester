import strutils
import pytest
import sys
import uuid

def test_camel2under_basic():
    assert strutils.camel2under('BasicParseTest') == 'basic_parse_test'
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('A') == 'a'
    assert strutils.camel2under('') == ''


def test_slugify_basic_and_ascii():
    assert strutils.slugify('First post! Hi!!!!~1    ') == 'first_post_hi_1'
    result = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    assert result == b'kurt_goedel_s_pretty_cool'
    assert strutils.slugify('', delim='-', lower=False) == ''
    assert strutils.slugify('A B', delim='-', lower=False) == 'A-B'
    assert strutils.slugify('A B', delim='-', lower=True) == 'a-b'

def test_split_punct_ws_various():
    assert strutils.split_punct_ws('First post! Hi!!!!~1    ') == ['First', 'post', 'Hi', '1']
    assert strutils.split_punct_ws('') == []
    assert strutils.split_punct_ws('abc') == ['abc']
    assert strutils.split_punct_ws('a,b.c!d') == ['a', 'b', 'c', 'd']

def test_unit_len_plural_and_zero():
    assert strutils.unit_len(range(10), 'number') == '10 numbers'
    assert strutils.unit_len('aeiou', 'vowel') == '5 vowels'
    assert strutils.unit_len([], 'worry') == 'No worries'
    assert strutils.unit_len([1], 'item') == '1 item'

def test_ordinalize_various():
    assert strutils.ordinalize(1) == '1st'
    assert strutils.ordinalize(2) == '2nd'
    assert strutils.ordinalize(3) == '3rd'
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(21) == '21st'
    assert strutils.ordinalize(22) == '22nd'
    assert strutils.ordinalize(23) == '23rd'
    assert strutils.ordinalize(101) == '101st'
    assert strutils.ordinalize('hi') == 'hi'
    assert strutils.ordinalize(1515) == '1515th'
    assert strutils.ordinalize(1, ext_only=True) == 'st'
    assert strutils.ordinalize(2, ext_only=True) == 'nd'
    assert strutils.ordinalize(11, ext_only=True) == 'th'
    assert strutils.ordinalize('', ext_only=True) == ''

def test_cardinalize_plural_and_singular():
    assert strutils.cardinalize('vowel', 5) == 'vowels'
    assert strutils.cardinalize('Wish', 3) == 'Wishes'
    assert strutils.cardinalize('item', 1) == 'item'
    assert strutils.cardinalize('item', 0) == 'items'


def test_find_hashtags_ascii_and_unicode():
    assert strutils.find_hashtags('#atag http://asite/#ananchor') == ['atag']
    assert strutils.find_hashtags('no hashtags here') == []
    assert strutils.find_hashtags('foo #bar #baz') == ['bar', 'baz']
    assert strutils.find_hashtags('foo ＃bar') == ['bar']
    # Unicode hashtag
    s = "can't get enough of that dignity chicken #肯德基 woo"
    tags = strutils.find_hashtags(s)
    assert any('\u80af' in tag or '\u57fa' in tag for tag in tags) or tags == ['肯德基']

def test_a10n_numeronym():
    assert strutils.a10n('abbreviation') == 'a10n'
    assert strutils.a10n('internationalization') == 'i18n'
    assert strutils.a10n('') == ''
    assert strutils.a10n('ab') == 'ab'
    assert strutils.a10n('abc') == 'a1c'

def test_strip_ansi_removes_codes_and_type():
    s = '\x1b[0m\x1b[1;36mart\x1b[46;34m'
    assert strutils.strip_ansi(s) == 'art'
    # bytes input
    b = b'\x1b[0m\x1b[1;36mart\x1b[46;34m'
    result = strutils.strip_ansi(b)
    assert isinstance(result, bytes)
    assert result == b'art'
    # bytearray input
    ba = bytearray(b'\x1b[0m\x1b[1;36mart\x1b[46;34m')
    result = strutils.strip_ansi(ba)
    assert isinstance(result, bytearray)
    assert result == bytearray(b'art')


def test_is_ascii_true_false_and_error():
    assert strutils.is_ascii('Beyonce') is True
    assert strutils.is_ascii(b'Beyonce') is True
    assert strutils.is_ascii('Beyoncé') is False
    assert strutils.is_ascii(b'Beyonc\xc3\xa9') is False
    with pytest.raises(ValueError) as e:
        strutils.is_ascii(123)
    assert 'expected text or bytes' in str(e.value)


def test_html2text_removes_tags_and_entities():
    html = u'<a href="#">Test &amp;<em>(\u0394&#x03b7;&#956;&#x03CE;)</em></a>'
    r = strutils.html2text(html)
    assert r == u'Test &(\u0394\u03b7\u03bc\u03ce)'
    # Unknown entity
    html = u'<p>&unknown;</p>'
    assert strutils.html2text(html) == '&unknown;'

def test_gzip_bytes_and_gunzip_bytes_roundtrip():
    data = b'a' * 10000
    gz = strutils.gzip_bytes(data)
    assert isinstance(gz, bytes)
    # decompress
    out = strutils.gunzip_bytes(gz)
    assert out == data
    # decompress known empty and non-empty
    assert strutils.gunzip_bytes(strutils._EMPTY_GZIP_BYTES) == b''
    assert strutils.gunzip_bytes(strutils._NON_EMPTY_GZIP_BYTES).rstrip() == b'bytesahoy!'

def test_iter_splitlines_various_endings():
    assert list(strutils.iter_splitlines('\nhi\nbye\n')) == ['', 'hi', 'bye', '']
    assert list(strutils.iter_splitlines('\r\nhi\rbye\r\n')) == ['', 'hi', 'bye', '']
    assert list(strutils.iter_splitlines('')) == []
    assert list(strutils.iter_splitlines('one')) == ['one']
    assert list(strutils.iter_splitlines('one\ntwo')) == ['one', 'two']


def test_is_uuid_string_and_object():
    v4 = 'e682ccca-5a4c-4ef2-9711-73f9ad1e15ea'
    v1 = '0221f0d9-d4b9-11e5-a478-10ddb1c2feb9'
    assert strutils.is_uuid(v4) is True
    assert strutils.is_uuid(v1) is False
    assert strutils.is_uuid(v1, version=1) is True
    # UUID object
    u = uuid.UUID(v4)
    assert strutils.is_uuid(u) is True
    # Not a uuid
    assert strutils.is_uuid('not-a-uuid') is False
    assert strutils.is_uuid(123) is False

def test_escape_shell_args_sh_and_cmd_and_error():
    args = ['aa', '[bb]', "cc'cc", 'dd"dd']
    sh = strutils.escape_shell_args(args, style='sh')
    assert sh == "aa '[bb]' 'cc'\"'\"'cc' 'dd\"dd'"
    cmd = strutils.escape_shell_args(args, style='cmd')
    assert cmd == "aa [bb] cc'cc dd\\\"dd"
    # Default style
    result = strutils.escape_shell_args(args)
    if sys.platform == 'win32':
        assert result == cmd
    else:
        assert result == sh
    # Invalid style
    with pytest.raises(ValueError) as e:
        strutils.escape_shell_args(args, style='badstyle')
    assert "style expected one of" in str(e.value)

def test_args2sh_and_args2cmd_behavior():
    args = ['aa', '[bb]', "cc'cc", 'dd\"dd']
    assert strutils.args2sh(args) == "aa '[bb]' 'cc'\"'\"'cc' 'dd\"dd'"
    assert strutils.args2cmd(args) == 'aa [bb] cc\'cc dd\\"dd'
    # Empty arg
    assert strutils.args2sh(['']) == "''"
    assert strutils.args2cmd(['']) == '""'

def test_parse_int_list_and_format_int_list():
    s = '1,3,5-8,10-11,15'
    expected = [1, 3, 5, 6, 7, 8, 10, 11, 15]
    assert strutils.parse_int_list(s) == expected
    assert strutils.format_int_list(expected) == s
    # Empty string
    assert strutils.parse_int_list('') == []
    assert strutils.format_int_list([]) == ''
    # Single value
    assert strutils.parse_int_list('2') == [2]
    assert strutils.format_int_list([2]) == '2'
    # Repeated values
    assert strutils.format_int_list([1,1,2,2,3]) == '1-3'

def test_complement_int_list_various_cases():
    s = '1,3,5-8,10-11,15'
    assert strutils.complement_int_list(s) == '0,2,4,9,12-14'
    assert strutils.complement_int_list(s, range_start=0) == '0,2,4,9,12-14'
    assert strutils.complement_int_list(s, range_start=1) == '2,4,9,12-14'
    assert strutils.complement_int_list(s, range_start=2) == '2,4,9,12-14'
    assert strutils.complement_int_list(s, range_start=3) == '4,9,12-14'
    assert strutils.complement_int_list(s, range_end=15) == '0,2,4,9,12-14'
    assert strutils.complement_int_list(s, range_end=14) == '0,2,4,9,12-13'
    assert strutils.complement_int_list(s, range_end=13) == '0,2,4,9,12'
    assert strutils.complement_int_list(s, range_end=20) == '0,2,4,9,12-14,16-19'
    assert strutils.complement_int_list(s, range_end=0) == ''
    assert strutils.complement_int_list(s, range_start=-1) == '0,2,4,9,12-14'
    assert strutils.complement_int_list(s, range_end=-1) == ''
    assert strutils.complement_int_list('1,3,5-8', range_start=1, range_end=1) == ''
    assert strutils.complement_int_list('1,3,5-8', range_start=2, range_end=2) == ''
    assert strutils.complement_int_list('1,3,5-8', range_start=2, range_end=3) == '2'
    assert strutils.complement_int_list('1,3,5-8', range_start=-10, range_end=-5) == ''
    assert strutils.complement_int_list('1,3,5-8', range_start=20, range_end=10) == ''
    assert strutils.complement_int_list('') == ''

def test_int_ranges_from_int_list_various():
    s = '1,3,5-8,10-11,15'
    expected = ((1,1), (3,3), (5,8), (10,11), (15,15))
    assert strutils.int_ranges_from_int_list(s) == expected
    assert strutils.int_ranges_from_int_list('1') == ((1,1),)
    assert strutils.int_ranges_from_int_list('') == ()

def test_MultiReplace_dict_and_iterable():
    m = strutils.MultiReplace({'foo': 'baz', 'baz': 'bar'})
    assert m.sub('foo bar baz') in ('baz bar bar', 'bar bar baz')
    m2 = strutils.MultiReplace([('foo', 'zoo'), ('cat', 'hat'), ('bat', 'kraken')])
    assert m2.sub('The foo bar cat ate a bat') == 'The zoo bar hat ate a kraken'
    # regex mode
    m3 = strutils.MultiReplace([('f.o', 'zoo')], regex=True)
    assert m3.sub('foo fxo') == 'zoo zoo'

def test_multi_replace_shortcut():
    s = 'The foo bar cat ate a bat'
    sub_map = {'foo': 'zoo', 'cat': 'hat', 'bat': 'kraken'}
    result = strutils.multi_replace(s, sub_map)
    assert result == 'The zoo bar hat ate a kraken'

def test_unwrap_text_basic_and_ending_none():
    text = "Short \n lines  \nwrapped\nsmall.\n\nAnother\nparagraph."
    expected = 'Short lines wrapped small.\n\nAnother paragraph.'
    assert strutils.unwrap_text(text) == expected
    # ending=None returns list
    result = strutils.unwrap_text(text, ending=None)
    assert result == ['Short lines wrapped small.', 'Another paragraph.']
    # single paragraph
    assert strutils.unwrap_text('a\nb\nc') == 'a b c'
    # empty string
    assert strutils.unwrap_text('') == ''








def test_ordinalize_default_th():
    # 4th, 11th, 12th, 13th, 1515th
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(1515) == '1515th'




def test_pluralize_irregular_and_regular():
    # irregular plural
    assert strutils.pluralize('foot') == 'feet'
    # word ending with 'y' and previous letter not aeiou
    assert strutils.pluralize('party') == 'parties'
    # word ending with 'y' and previous letter is aeiou
    assert strutils.pluralize('boy') == 'boys'
    # word ending with 's'
    assert strutils.pluralize('bus') == 'buses'
    # word ending with 'ch'
    assert strutils.pluralize('match') == 'matches'
    # word ending with 'sh'
    assert strutils.pluralize('dish') == 'dishes'
    # already plural
    assert strutils.pluralize('sheep') == 'sheep'
    # regular
    assert strutils.pluralize('dog') == 'dogs'






def test_pluralize_empty_and_irregular_and_regular():
    # line 268: or -> and
    # line 273: string 'aeiou' -> 'XX...XX'
    # line 276: string 'es' -> 'XX...XX'
    # Test empty string
    assert strutils.pluralize('') == ''
    # Test irregular plural
    assert strutils.pluralize('foot') == 'feet'
    # Test word ending with 'y' and previous letter not in 'aeiou'
    assert strutils.pluralize('party') == 'parties'
    # Test word ending with 'y' and previous letter in 'aeiou'
    assert strutils.pluralize('boy') == 'boys'
    # Test word ending with 's'
    assert strutils.pluralize('bus') == 'buses'
    # Test word ending with 'ch'
    assert strutils.pluralize('match') == 'matches'
    # Test word ending with 'sh'
    assert strutils.pluralize('dish') == 'dishes'
    # Test already plural
    assert strutils.pluralize('sheep') == 'sheep'
    # Test regular
    assert strutils.pluralize('dog') == 'dogs'






def test_under2camel_multiple_underscores():
    # Should produce '_' for each empty segment
    assert strutils.under2camel('foo__bar') == 'Foo_Bar'


def test_singularize_empty_and_irregular():
    # line 237: removed not
    # line 238: return value replaced with None
    assert strutils.singularize('') == ''
    assert strutils.singularize('feet') == 'foot'


def test_singularize_non_plural():
    # line 243: removed not
    # line 244: return value replaced with None
    assert strutils.singularize('dog') == 'dog'


def test_singularize_two_letter_word():
    # line 245: 2 -> 3
    assert strutils.singularize('as') == 'a'






def test_singularize_regular_plural():
    # line 252: 1->2
    assert strutils.singularize('dogs') == 'dog'


def test_pluralize_y_rule():
    # line 273: 'aeiou'->'XX...XX'
    assert strutils.pluralize('party') == 'parties'
    assert strutils.pluralize('boy') == 'boys'


def test_pluralize_es_rule():
    # line 276: 'es'->'XX...XX'
    assert strutils.pluralize('bus') == 'buses'
    assert strutils.pluralize('match') == 'matches'
    assert strutils.pluralize('dish') == 'dishes'


def test_pluralize_regular():
    assert strutils.pluralize('dog') == 'dogs'


def test_pluralize_already_plural():
    assert strutils.pluralize('sheep') == 'sheep'


def test_pluralize_empty():
    # line 284: return value replaced with None
    assert strutils.pluralize('') == ''


def test_ordinalize_default_suffix():
    # For numbers ending in 4, 11, 12, 13, 1515, should get 'th'
    assert strutils.ordinalize(4) == '4th'
    assert strutils.ordinalize(11) == '11th'
    assert strutils.ordinalize(12) == '12th'
    assert strutils.ordinalize(13) == '13th'
    assert strutils.ordinalize(1515) == '1515th'


def test___all___contains_expected_names():
    # These names must be present in __all__ as per the original module.
    expected = [
        'camel2under', 'under2camel', 'slugify', 'split_punct_ws',
        'unit_len', 'ordinalize', 'cardinalize', 'pluralize', 'singularize',
        'asciify', 'is_ascii', 'is_uuid', 'html2text', 'strip_ansi',
        'bytes2human', 'find_hashtags', 'a10n', 'gzip_bytes', 'gunzip_bytes',
        'iter_splitlines', 'indent', 'escape_shell_args',
        'args2cmd', 'args2sh', 'parse_int_list', 'format_int_list',
        'int_list_complement', 'int_list_to_int_tuples', 'MultiReplace',
        'multi_replace', 'unwrap_text'
    ]
    for name in expected:
        assert name in strutils.__all__


def test_ordinalize_default_suffix_is_th():
    # For a number ending in 0, 4, 5, 6, 7, 8, 9, should get 'th'
    for n in [0, 4, 5, 6, 7, 8, 9, 10, 14, 111, 112, 113]:
        result = strutils.ordinalize(n)
        assert result.endswith('th'), f"ordinalize({n}) = {result}"


def test_singularize_two_letter_word_as():
    # 'as' is two letters, should become 'a'
    assert strutils.singularize('as') == 'a'




def test_singularize_es_rule():
    # 'buses' -> 'bus'
    assert strutils.singularize('buses') == 'bus'
    # 'bosses' -> 'boss'
    assert strutils.singularize('bosses') == 'boss'
    # 'kisses' -> 'kiss'
    assert strutils.singularize('kisses') == 'kiss'


def test_pluralize_y_rule_vowel_and_consonant():
    # consonant before 'y'
    assert strutils.pluralize('party') == 'parties'
    # vowel before 'y'
    assert strutils.pluralize('boy') == 'boys'
    # consonant before 'y'
    assert strutils.pluralize('fly') == 'flies'
    # vowel before 'y'
    assert strutils.pluralize('key') == 'keys'


def test__match_case_lower_returns_disciple():
    # master is lower, disciple is returned lower
    assert strutils._match_case('dog', 'cat') == 'cat'


def test__match_case_upper_returns_disciple_upper():
    # master is upper, disciple is returned upper
    assert strutils._match_case('DOG', 'cat') == 'CAT'


def test__match_case_title_returns_disciple_title():
    # master is title, disciple is returned title
    assert strutils._match_case('Dog', 'cat') == 'Cat'


def test_irregular_plural_and_singular_variants():
    # 'alga' -> 'algae'
    assert strutils.pluralize('alga') == 'algae'
    assert strutils.singularize('algae') == 'alga'
    # 'addendum' -> 'addenda'
    assert strutils.pluralize('addendum') == 'addenda'
    assert strutils.singularize('addenda') == 'addendum'
    # 'alumna' -> 'alumnae'
    assert strutils.pluralize('alumna') == 'alumnae'
    assert strutils.singularize('alumnae') == 'alumna'
    # 'analysis' -> 'analyses'
    assert strutils.pluralize('analysis') == 'analyses'
    assert strutils.singularize('analyses') == 'analysis'
    # 'appendix' -> 'appendices'
    assert strutils.pluralize('appendix') == 'appendices'
    assert strutils.singularize('appendices') == 'appendix'
    # 'axis' -> 'axes'
    assert strutils.pluralize('axis') == 'axes'
    assert strutils.singularize('axes') == 'axis'
    # 'bacillus' -> 'bacilli'
    assert strutils.pluralize('bacillus') == 'bacilli'
    assert strutils.singularize('bacilli') == 'bacillus'


def test_pluralize_and_singularize_preserve_case():
    assert strutils.pluralize('Dog') == 'Dogs'
    assert strutils.pluralize('DOG') == 'DOGS'
    assert strutils.singularize('Dogs') == 'Dog'
    assert strutils.singularize('DOGS') == 'DOG'


def test_pluralize_and_singularize_empty_string():
    assert strutils.pluralize('') == ''
    assert strutils.singularize('') == ''




def test_split_punct_ws_various_new():
    assert strutils.split_punct_ws('a,b.c!d') == ['a', 'b', 'c', 'd']
    assert strutils.split_punct_ws('hello...world') == ['hello', 'world']
    assert strutils.split_punct_ws('foo\tbar\nbaz') == ['foo', 'bar', 'baz']


def test_camel2under_edge_cases():
    assert strutils.camel2under('HTTPRequest') == 'http_request'
    assert strutils.camel2under('CamelCase') == 'camel_case'
    assert strutils.camel2under('lowercase') == 'lowercase'
    assert strutils.camel2under('A') == 'a'
    assert strutils.camel2under('') == ''


def test_slugify_ascii_and_non_ascii():
    assert strutils.slugify('First post! Hi!!!!~1    ') == 'first_post_hi_1'
    result = strutils.slugify("Kurt Gödel's pretty cool.", ascii=True)
    assert result == b'kurt_goedel_s_pretty_cool'
    assert strutils.slugify('', delim='-', lower=False) == ''
    assert strutils.slugify('A B', delim='-', lower=False) == 'A-B'
    assert strutils.slugify('A B', delim='-', lower=True) == 'a-b'


def test_ordinalize_default_suffix_th_vs_xx():
    # line 197: string 'th' -> 'XX...XX'
    # For a number ending in 0, 4, 5, 6, 7, 8, 9, should get 'th'
    for n in [0, 4, 5, 6, 7, 8, 9, 10, 14, 111, 112, 113]:
        result = strutils.ordinalize(n)
        assert result.endswith('th'), f"ordinalize({n}) = {result}"


def test_singularize_two_letter_word_len2():
    # line 245: 2 -> 3
    # 'as' is two letters, should become 'a'
    assert strutils.singularize('as') == 'a'


def test_singularize_ies_rule_and_aeiou_check():
    # line 247: string 'ies' -> 'XX...XX'
    # line 247: 4 -> 5
    # line 247: string 'aeiou' -> 'XX...XX'
    # line 248: 3 -> 4
    # line 248: string 'y' -> 'XX...XX'
    # 'parties' -> 'party' (consonant before 'ies')
    assert strutils.singularize('parties') == 'party'
    # 'flies' -> 'fly' (consonant before 'ies')
    assert strutils.singularize('flies') == 'fly'
    # 'boys' -> 'boy' (should not match 'ies' rule)
    assert strutils.singularize('boys') == 'boy'


def test_pluralize_y_rule_aeiou_check():
    # line 273: string 'aeiou' -> 'XX...XX'
    # consonant before 'y'
    assert strutils.pluralize('party') == 'parties'
    # vowel before 'y'
    assert strutils.pluralize('boy') == 'boys'
    # consonant before 'y'
    assert strutils.pluralize('fly') == 'flies'
    # vowel before 'y'
    assert strutils.pluralize('key') == 'keys'


def test_irregular_plural_and_singular_variants_alumnus():
    # line 296: string 'alumnus' -> 'XX...XX'
    # 'alumnus' -> 'alumni'
    assert strutils.pluralize('alumnus') == 'alumni'
    assert strutils.singularize('alumni') == 'alumnus'


def test_irregular_plural_and_singular_variants_basis_beau_bacteria_beaux():
    # line 298: string 'basis' -> 'XX...XX'
    # line 298: string 'beau' -> 'XX...XX'
    # line 298: string 'bacteria' -> 'XX...XX'
    # line 298: string 'beaux' -> 'XX...XX'
    assert strutils.pluralize('basis') == 'bases'
    assert strutils.singularize('bases') == 'basis'
    assert strutils.pluralize('beau') == 'beaux'
    assert strutils.singularize('beaux') == 'beau'
    assert strutils.pluralize('bacterium') == 'bacteria'
    assert strutils.singularize('bacteria') == 'bacterium'


def test_irregular_plural_and_singular_variants_bureau_bureaus_cacti():
    # line 299: string 'bureau' -> 'XX...XX'
    # line 299: string 'bureaus' -> 'XX...XX'
    # line 299: string 'cacti' -> 'XX...XX'
    assert strutils.pluralize('bureau') == 'bureaus'
    assert strutils.singularize('bureaus') == 'bureau'
    assert strutils.pluralize('cactus') == 'cacti'
    assert strutils.singularize('cacti') == 'cactus'


def test_irregular_plural_and_singular_variants_calf_corps_children():
    # line 300: string 'calf' -> 'XX...XX'
    # line 300: string 'corps' -> 'XX...XX'
    # line 300: string 'children' -> 'XX...XX'
    assert strutils.pluralize('calf') == 'calves'
    assert strutils.singularize('calves') == 'calf'
    assert strutils.pluralize('corps') == 'corps'
    assert strutils.singularize('corps') == 'corps'
    assert strutils.pluralize('child') == 'children'
    assert strutils.singularize('children') == 'child'


def test_irregular_plural_and_singular_variants_corpus_criterion_corpora_criteria():
    # line 301: string 'corpus' -> 'XX...XX'
    # line 301: string 'criterion' -> 'XX...XX'
    # line 301: string 'corpora' -> 'XX...XX'
    # line 301: string 'criteria' -> 'XX...XX'
    assert strutils.pluralize('corpus') == 'corpora'
    assert strutils.singularize('corpora') == 'corpus'
    assert strutils.pluralize('crisis') == 'crises'
    assert strutils.singularize('crises') == 'crisis'
    assert strutils.pluralize('criterion') == 'criteria'
    assert strutils.singularize('criteria') == 'criterion'


def test_irregular_plural_and_singular_variants_datum_curricula_deer():
    # line 302: string 'datum' -> 'XX...XX'
    # line 302: string 'curricula' -> 'XX...XX'
    # line 302: string 'deer' -> 'XX...XX'
    assert strutils.pluralize('datum') == 'data'
    assert strutils.singularize('data') == 'datum'
    assert strutils.pluralize('curriculum') == 'curricula'
    assert strutils.singularize('curricula') == 'curriculum'
    assert strutils.pluralize('deer') == 'deer'
    assert strutils.singularize('deer') == 'deer'


def test_irregular_plural_and_singular_variants_diagnosis_die_dice():
    # line 303: string 'diagnosis' -> 'XX...XX'
    # line 303: string 'die' -> 'XX...XX'
    # line 303: string 'dice' -> 'XX...XX'
    assert strutils.pluralize('diagnosis') == 'diagnoses'
    assert strutils.singularize('diagnoses') == 'diagnosis'
    assert strutils.pluralize('die') == 'dice'
    assert strutils.singularize('dice') == 'die'


def test_irregular_plural_and_singular_variants_echo_ellipsis_echoes_elves():
    # line 304: string 'echo' -> 'XX...XX'
    # line 304: string 'ellipsis' -> 'XX...XX'
    # line 304: string 'echoes' -> 'XX...XX'
    # line 304: string 'elves' -> 'XX...XX'
    assert strutils.pluralize('echo') == 'echoes'
    assert strutils.singularize('echoes') == 'echo'
    assert strutils.pluralize('elf') == 'elves'
    assert strutils.singularize('elves') == 'elf'
    assert strutils.pluralize('ellipsis') == 'ellipses'
    assert strutils.singularize('ellipses') == 'ellipsis'


def test_irregular_plural_and_singular_variants_embargo_erratum_embargoes_errata():
    # line 305: string 'embargo' -> 'XX...XX'
    # line 305: string 'erratum' -> 'XX...XX'
    # line 305: string 'embargoes' -> 'XX...XX'
    # line 305: string 'errata' -> 'XX...XX'
    assert strutils.pluralize('embargo') == 'embargoes'
    assert strutils.singularize('embargoes') == 'embargo'
    assert strutils.pluralize('erratum') == 'errata'
    assert strutils.singularize('errata') == 'erratum'
