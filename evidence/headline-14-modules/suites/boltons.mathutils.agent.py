import mathutils
import pytest

def test_clamp_within_bounds_returns_value():
    assert mathutils.clamp(1.0, 0, 5) == 1.0
    assert mathutils.clamp(3, 1, 10) == 3
    assert mathutils.clamp(0, 0, 5) == 0
    assert mathutils.clamp(5, 0, 5) == 5

def test_clamp_below_lower_returns_lower():
    assert mathutils.clamp(-1.0, 0, 5) == 0
    assert mathutils.clamp(-100, -10, 10) == -10

def test_clamp_above_upper_returns_upper():
    assert mathutils.clamp(101.0, 0, 5) == 5
    assert mathutils.clamp(123, upper=5) == 5
    assert mathutils.clamp(1000, -100, 100) == 100

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-1e10, lower=-1e20) == -1e10
    assert mathutils.clamp(1e10, upper=1e20) == 1e10

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(4.0) == 4
    assert mathutils.ceil(-2.7) == -2

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(49, options=options) == 50

def test_ceil_with_options_no_gte_raises():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    assert "no ceil options greater than or equal to" in str(e.value)

def test_ceil_with_unsorted_options():
    options = [10, 1, 5]
    assert mathutils.ceil(2, options=options) == 5

def test_floor_no_options_behaves_like_math_floor():
    assert mathutils.floor(3.7) == 3
    assert mathutils.floor(4.0) == 4
    assert mathutils.floor(-2.7) == -3


def test_floor_with_options_no_lte_raises():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    assert "no floor options less than or equal to" in str(e.value)

def test_floor_with_unsorted_options():
    options = [10, 1, 5]
    assert mathutils.floor(6, options=options) == 5

def test_bits_init_from_int_and_len():
    b = mathutils.Bits(5, 4)
    assert b.val == 5
    assert b.len == 4
    assert b.as_bin() == '0101'

def test_bits_init_from_int_no_len():
    b = mathutils.Bits(5)
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'

def test_bits_init_from_bin_string():
    b = mathutils.Bits('1011')
    assert b.val == 11
    assert b.len == 4
    assert b.as_bin() == '1011'

def test_bits_init_from_hex_string():
    b = mathutils.Bits('0xA', 4)
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'

def test_bits_init_from_list_of_bools():
    b = mathutils.Bits([True, False, True])
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'


def test_bits_init_from_unicode():
    b = mathutils.Bits(u'1011')
    assert b.val == 11
    assert b.len == 4
    assert b.as_bin() == '1011'

def test_bits_init_bad_type_raises():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    assert "bad type" in str(e.value)

def test_bits_init_negative_raises():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    assert "cannot represent negative values" in str(e.value)

def test_bits_init_value_too_large_for_len_raises():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 2)
    assert "cannot be represented with" in str(e.value)

def test_bits_getitem_index_and_slice():
    b = mathutils.Bits('1011')
    assert b[0] is True
    assert b[1] is False
    assert b[2] is True
    assert b[3] is True
    with pytest.raises(IndexError):
        _ = b[4]
    # Slicing returns a Bits object
    s = b[1:3]
    assert isinstance(s, mathutils.Bits)
    assert s.as_bin() == '01'

def test_bits_getitem_bad_type_raises():
    b = mathutils.Bits('1011')
    with pytest.raises(TypeError):
        _ = b[1.5]

def test_bits_len():
    b = mathutils.Bits('1011')
    assert len(b) == 4

def test_bits_eq_and_not_eq():
    b1 = mathutils.Bits('1011')
    b2 = mathutils.Bits('1011')
    b3 = mathutils.Bits('1010')
    assert b1 == b2
    assert not (b1 == b3)
    assert b1 != b3

def test_bits_eq_notimplemented_for_other_type():
    b = mathutils.Bits('1011')
    assert (b == 11) is NotImplemented or (b == 11) is False

def test_bits_or_and():
    b1 = mathutils.Bits('1010')
    b2 = mathutils.Bits('1100')
    b_or = b1 | b2
    assert isinstance(b_or, mathutils.Bits)
    assert b_or.as_bin() == '1110'
    b_and = b1 & b2
    assert isinstance(b_and, mathutils.Bits)
    assert b_and.as_bin() == '1000'


def test_bits_lshift_and_rshift():
    b = mathutils.Bits('1011')
    b_l = b << 2
    assert b_l.as_bin() == '101100'
    assert b_l.len == 6
    b_r = b >> 2
    assert b_r.as_bin() == '10'
    assert b_r.len == 2

def test_bits_hash():
    b1 = mathutils.Bits('1011')
    b2 = mathutils.Bits('1011')
    assert hash(b1) == hash(b2)

def test_bits_as_list():
    b = mathutils.Bits('1011')
    assert b.as_list() == [True, False, True, True]

def test_bits_as_bin():
    b = mathutils.Bits(5, 4)
    assert b.as_bin() == '0101'


def test_bits_as_int():
    b = mathutils.Bits('1011')
    assert b.as_int() == 11

def test_bits_as_bytes():
    b = mathutils.Bits(255, 8)
    assert b.as_bytes() == b'\xff'
    b2 = mathutils.Bits(1, 8)
    assert b2.as_bytes() == b'\x01'
    b3 = mathutils.Bits(1, 16)
    assert b3.as_bytes() == b'\x00\x01'

def test_bits_from_list():
    b = mathutils.Bits.from_list([True, False, True])
    assert b.as_bin() == '101'

def test_bits_from_bin():
    b = mathutils.Bits.from_bin('1011')
    assert b.as_bin() == '1011'

def test_bits_from_hex():
    b = mathutils.Bits.from_hex('A')
    assert b.as_bin() == '1010'
    b2 = mathutils.Bits.from_hex('0xA')
    assert b2.as_bin() == '1010'
    b3 = mathutils.Bits.from_hex(b'A')
    assert b3.as_bin() == '1010'

def test_bits_from_int():
    b = mathutils.Bits.from_int(5, 4)
    assert b.as_bin() == '0101'

def test_bits_from_bytes():
    b = mathutils.Bits.from_bytes(b'\x0f')
    assert b.as_bin() == '00001111'

def test_bits_repr():
    b = mathutils.Bits('1011')
    assert repr(b) == "Bits('1011')"


def test_clamp_upper_equal_lower_allowed():
    # Should not raise when upper == lower
    assert mathutils.clamp(5, 5, 5) == 5


def test_bits_default_val_is_zero():
    b = mathutils.Bits()
    assert b.val == 0
    assert b.len == 1  # len('{0:b}'.format(0)) == 1
    assert b.as_bin() == '0'




def test_bits_init_zero_allowed_but_not_negative():
    b = mathutils.Bits(0)
    assert b.val == 0
    assert b.len == 1
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    assert "cannot represent negative values" in str(e.value)




def test_bits_eq_notimplemented_for_other_type_is_notimplemented():
    b = mathutils.Bits('1011')
    result = b.__eq__(11)
    assert result is NotImplemented


def test_bits_or_and_notimplemented_for_other_type():
    b = mathutils.Bits('1011')
    result_or = b.__or__(11)
    result_and = b.__and__(11)
    assert result_or is NotImplemented
    assert result_and is NotImplemented


def test_bits_as_hex_padding_and_byte_length():
    # 9 bits: needs 2 bytes (16 bits), so 4 hex digits
    b = mathutils.Bits(0x1FF, 9)
    # 9 bits: 2 bytes, so 4 hex digits, value is 0x01FF
    assert b.as_hex() == '01FF'
    # 16 bits: 2 bytes, so 4 hex digits, value is 0x1234
    b2 = mathutils.Bits(0x1234, 16)
    assert b2.as_hex() == '1234'
    # 8 bits: 1 byte, so 2 hex digits
    b3 = mathutils.Bits(0xAB, 8)
    assert b3.as_hex() == 'AB'


def test_clamp_upper_less_than_lower_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    # Ensure the error message is exactly as in the original code
    assert 'expected upper bound' in str(e.value)
    assert '>= lower bound' in str(e.value)


def test_ceil_with_options_no_gte_error_message_and_format():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    msg = str(e.value)
    assert "no ceil options greater than or equal to" in msg
    assert ": 4" in msg


def test_floor_with_options_no_lte_error_message_and_format():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    msg = str(e.value)
    assert "no floor options less than or equal to" in msg
    assert ": 5" in msg


def test_bits_init_from_bytes_decode_ascii():
    # This test ensures that val.decode('ascii') is used, not another encoding
    b = mathutils.Bits(b'1011')
    assert b.val == 11
    assert b.len == 4
    assert b.as_bin() == '1011'




def test_bits_init_bad_type_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    msg = str(e.value)
    assert "initialized with bad type" in msg
    assert "float" in msg


def test_bits_init_negative_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    msg = str(e.value)
    assert "Bits cannot represent negative values" in msg


def test_bits_init_value_too_large_for_len_comparison_and_message():
    # This test ensures the comparison is strictly >, not >=
    # 2 ** 2 = 4, so 4 is allowed, 5 is not
    mathutils.Bits(4, 2)  # Should not raise
    with pytest.raises(ValueError) as e:
        mathutils.Bits(5, 2)
    msg = str(e.value)
    assert "cannot be represented with" in msg
    assert "5" in msg and "2" in msg


def test_bits_init_from_empty_string_results_in_zero():
    b = mathutils.Bits('')
    assert b.val == 0
    assert b.len == 0


def test_bits_init_from_empty_unicode_results_in_zero():
    b = mathutils.Bits(u'')
    assert b.val == 0
    assert b.len == 0


def test_bits_init_from_empty_bytes_results_in_zero():
    b = mathutils.Bits(b'')
    assert b.val == 0
    assert b.len == 0


def test_clamp_upper_less_than_lower_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert str(e.value) == "expected upper bound (0) >= lower bound (5)"


def test_ceil_with_options_no_gte_exact_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    assert str(e.value) == "no ceil options greater than or equal to: 4"


def test_floor_with_options_no_lte_exact_error_message():
    options = [10, 20, 30]
    with pytest.raises(ValueError) as e:
        mathutils.floor(5, options=options)
    assert str(e.value) == "no floor options less than or equal to: 5"


def test_bits_init_bad_type_exact_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    assert str(e.value) == "initialized with bad type: float"


def test_bits_init_negative_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    assert str(e.value) == "Bits cannot represent negative values"


def test_bits_init_value_too_large_for_len_exact_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(5, 2)
    assert str(e.value) == "value 5 cannot be represented with 2 bits"
