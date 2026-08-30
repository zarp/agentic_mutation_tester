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
    assert mathutils.clamp(1000, -10, 10) == 10

def test_clamp_with_infinite_bounds():
    assert mathutils.clamp(5) == 5
    assert mathutils.clamp(-100) == -100
    assert mathutils.clamp(100, lower=0) == 100
    assert mathutils.clamp(-100, upper=0) == -100

def test_clamp_upper_less_than_lower_raises():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    assert "expected upper bound" in str(e.value)

def test_ceil_no_options_behaves_like_math_ceil():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(-1.2) == -1
    assert mathutils.ceil(0) == 0
    assert mathutils.ceil(5) == 5

def test_ceil_with_options_returns_smallest_gte():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(0.5, options=options) == 1.5
    assert mathutils.ceil(25, options=options) == 25
    assert mathutils.ceil(26, options=options) == 35
    assert mathutils.ceil(50, options=options) == 50

def test_ceil_with_options_exact_match():
    options = [1, 2, 3]
    assert mathutils.ceil(2, options=options) == 2

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
    assert mathutils.floor(-1.2) == -2
    assert mathutils.floor(0) == 0
    assert mathutils.floor(5) == 5


def test_floor_with_options_exact_match():
    options = [1, 2, 3]
    assert mathutils.floor(2, options=options) == 2

def test_floor_with_options_no_lte_raises():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
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
    b = mathutils.Bits('0xA')
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'

def test_bits_init_from_list_of_bools():
    b = mathutils.Bits([True, False, True])
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'

def test_bits_init_from_bytes():
    b = mathutils.Bits(b'101')
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'

def test_bits_init_from_unicode():
    b = mathutils.Bits(u'101')
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'

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

def test_bits_getitem_index_returns_bool():
    b = mathutils.Bits(5, 4)  # 0101
    assert b[0] is False
    assert b[1] is True
    assert b[2] is False
    assert b[3] is True

def test_bits_getitem_slice_returns_bits():
    b = mathutils.Bits(13, 4)  # 1101
    s = b[1:3]
    assert isinstance(s, mathutils.Bits)
    assert s.as_bin() == '10'

def test_bits_getitem_index_out_of_range_raises():
    b = mathutils.Bits(1, 2)
    with pytest.raises(IndexError):
        _ = b[2]

def test_bits_getitem_bad_type_raises():
    b = mathutils.Bits(1, 2)
    with pytest.raises(TypeError):
        _ = b[1.5]

def test_bits_len_returns_len():
    b = mathutils.Bits(7, 4)
    assert len(b) == 4

def test_bits_eq_same_type_and_value():
    b1 = mathutils.Bits(5, 4)
    b2 = mathutils.Bits(5, 4)
    assert b1 == b2

def test_bits_eq_different_type_returns_notimplemented():
    class Dummy:
        pass
    b = mathutils.Bits(1)
    assert b.__eq__(Dummy()) is NotImplemented

def test_bits_or_and_bitwise():
    b1 = mathutils.Bits(0b1010, 4)
    b2 = mathutils.Bits(0b1100, 4)
    assert (b1 | b2) == mathutils.Bits(0b1110, 4)
    assert (b1 & b2) == mathutils.Bits(0b1000, 4)

def test_bits_or_and_different_len():
    b1 = mathutils.Bits(0b101, 3)
    b2 = mathutils.Bits(0b1100, 4)
    assert (b1 | b2) == mathutils.Bits(0b1101, 4)
    assert (b1 & b2) == mathutils.Bits(0b0100, 4)

def test_bits_or_and_not_bits_returns_notimplemented():
    b = mathutils.Bits(1)
    assert b.__or__(1) is NotImplemented
    assert b.__and__(1) is NotImplemented

def test_bits_lshift_and_rshift():
    b = mathutils.Bits(0b101, 3)
    assert (b << 2) == mathutils.Bits(0b10100, 5)
    assert (b >> 1) == mathutils.Bits(0b10, 2)

def test_bits_hash_is_hash_of_val():
    b = mathutils.Bits(7, 4)
    assert hash(b) == hash(7)

def test_bits_as_list():
    b = mathutils.Bits(0b1011, 4)
    assert b.as_list() == [True, False, True, True]

def test_bits_as_bin_and_as_hex():
    b = mathutils.Bits(0b1011, 4)
    assert b.as_bin() == '1011'
    assert b.as_hex() == '0B'

def test_bits_as_int():
    b = mathutils.Bits(0b1011, 4)
    assert b.as_int() == 11

def test_bits_as_bytes_and_from_bytes():
    b = mathutils.Bits(0xAB, 8)
    bytes_val = b.as_bytes()
    assert isinstance(bytes_val, bytes)
    b2 = mathutils.Bits.from_bytes(bytes_val)
    assert b2 == mathutils.Bits(0xAB, 8)

def test_bits_from_list():
    b = mathutils.Bits.from_list([True, False, True])
    assert b == mathutils.Bits(5, 3)

def test_bits_from_bin():
    b = mathutils.Bits.from_bin('101')
    assert b == mathutils.Bits(5, 3)

def test_bits_from_hex():
    b = mathutils.Bits.from_hex('A')
    assert b == mathutils.Bits(10, 4)
    b2 = mathutils.Bits.from_hex('0xA')
    assert b2 == mathutils.Bits(10, 4)
    b3 = mathutils.Bits.from_hex(b'A')
    assert b3 == mathutils.Bits(10, 4)

def test_bits_from_int():
    b = mathutils.Bits.from_int(7, 4)
    assert b == mathutils.Bits(7, 4)

def test_bits_repr():
    b = mathutils.Bits(5, 4)
    assert repr(b) == "Bits('0101')"


def test_clamp_upper_equal_lower_allowed():
    # Should not raise when upper == lower
    assert mathutils.clamp(5, 5, 5) == 5


def test_ceil_with_options_no_gte_error_message_contains_x():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # The error message should contain the value of x (4)
    assert "4" in str(e.value)


def test_bits_default_init_is_zero():
    b = mathutils.Bits()
    assert b.val == 0
    # Should be length 1 (since 0 in binary is '0')
    assert b.len == 1
    assert b.as_bin() == '0'


def test_bits_len_is_none_sets_len():
    b = mathutils.Bits(3)
    # 3 in binary is '11', so len should be 2
    assert b.len == 2


def test_bits_init_from_empty_bin_string_gives_zero():
    b = mathutils.Bits('')
    assert b.val == 0
    assert b.len == 0


def test_bits_init_zero_allowed():
    b = mathutils.Bits(0)
    assert b.val == 0
    assert b.len == 1




def test_bits_eq_requires_both_val_and_len_equal():
    b1 = mathutils.Bits(5, 4)
    b2 = mathutils.Bits(5, 3)
    b3 = mathutils.Bits(4, 4)
    assert not (b1 == b2)
    assert not (b1 == b3)


def test_bits_as_hex_padding_and_length():
    # 8 bits: should be 2 hex digits
    b = mathutils.Bits(0xA, 8)
    assert b.as_hex() == '0A'
    # 12 bits: should be 4 hex digits (2 bytes)
    b2 = mathutils.Bits(0xABC, 12)
    assert b2.as_hex() == '0ABC'
    # 16 bits: should be 4 hex digits
    b3 = mathutils.Bits(0xABCD, 16)
    assert b3.as_hex() == 'ABCD'
    # 1 bit: should be 2 hex digits (1 byte)
    b4 = mathutils.Bits(1, 1)
    assert b4.as_hex() == '01'


def test_clamp_upper_less_than_lower_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    # The error message should contain 'expected upper bound'
    assert "expected upper bound" in str(e.value)


def test_ceil_with_options_no_gte_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # The error message should contain 'no ceil options greater than or equal to'
    assert "no ceil options greater than or equal to" in str(e.value)


def test_floor_with_options_no_lte_error_message():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
    # The error message should contain 'no floor options less than or equal to'
    assert "no floor options less than or equal to" in str(e.value)


def test_bits_init_bad_type_error_message():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    # The error message should contain 'bad type'
    assert "bad type" in str(e.value)


def test_bits_init_negative_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    # The error message should contain 'Bits cannot represent negative values'
    assert "Bits cannot represent negative values" in str(e.value)


def test_bits_init_value_too_large_for_len_error_message():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 2)
    # The error message should contain 'cannot be represented with'
    assert "cannot be represented with" in str(e.value)


def test_clamp_upper_less_than_lower_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.clamp(1, 5, 0)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('expected upper bound')


def test_ceil_with_options_no_gte_error_message_exact():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.ceil(4, options=options)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('no ceil options greater than or equal to')


def test_floor_with_options_no_lte_error_message_exact():
    options = [1, 2, 3]
    with pytest.raises(ValueError) as e:
        mathutils.floor(0, options=options)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('no floor options less than or equal to')


def test_bits_init_bad_type_error_message_exact():
    with pytest.raises(TypeError) as e:
        mathutils.Bits(3.14)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('initialized with bad type')


def test_bits_init_negative_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(-1)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('Bits cannot represent negative values')


def test_bits_init_value_too_large_for_len_error_message_exact():
    with pytest.raises(ValueError) as e:
        mathutils.Bits(8, 2)
    # Must match the exact error message, not just contain the substring
    assert str(e.value).startswith('value 8 cannot be represented with 2 bits')


def test_bits_init_value_equal_to_2_pow_len_allowed():
    # Original: if val > 2 ** len_: raise
    # Mutant:   if val >= 2 ** len_: raise
    # So val == 2 ** len_ should be allowed in original, but not in mutant.
    # For len_ = 3, val = 8 (2 ** 3)
    b = mathutils.Bits(8, 3)
    assert b.val == 8
    assert b.len == 3
    assert b.as_bin() == '1000'
