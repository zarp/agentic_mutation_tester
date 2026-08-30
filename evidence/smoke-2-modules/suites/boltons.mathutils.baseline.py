import pytest
import mathutils

import sys

# Helper for Python 2/3 compatibility
PY2 = sys.version_info[0] == 2

def test_clamp_basic():
    assert mathutils.clamp(1.0, 0, 5) == 1.0
    assert mathutils.clamp(-1.0, 0, 5) == 0
    assert mathutils.clamp(101.0, 0, 5) == 5
    assert mathutils.clamp(123, upper=5) == 5
    assert mathutils.clamp(3, lower=2) == 3
    assert mathutils.clamp(1, lower=2) == 2
    assert mathutils.clamp(10, lower=2, upper=8) == 8

def test_clamp_mixed_types():
    assert mathutils.clamp(3, 2.5, 5.5) == 3
    assert mathutils.clamp(2.0, 2, 5) == 2.0

def test_clamp_infinite_bounds():
    assert mathutils.clamp(5, lower=float('-inf')) == 5
    assert mathutils.clamp(5, upper=float('inf')) == 5
    assert mathutils.clamp(5) == 5

def test_clamp_upper_lower_error():
    with pytest.raises(ValueError):
        mathutils.clamp(1, lower=5, upper=2)

def test_ceil_no_options():
    assert mathutils.ceil(3.2) == 4
    assert mathutils.ceil(4.0) == 4
    assert mathutils.ceil(-1.2) == -1

def test_ceil_with_options():
    options = [1.5, 2.5, 4, 6, 10, 25, 35, 50]
    assert mathutils.ceil(3.5, options=options) == 4
    assert mathutils.ceil(4, options=options) == 4
    assert mathutils.ceil(2.5, options=options) == 2.5
    assert mathutils.ceil(0.5, options=options) == 1.5

def test_ceil_with_options_no_ceil():
    options = [1, 2, 3]
    with pytest.raises(ValueError):
        mathutils.ceil(4, options=options)

def test_ceil_options_unsorted():
    options = [10, 1, 5]
    assert mathutils.ceil(2, options=options) == 5

def test_floor_no_options():
    assert mathutils.floor(3.2) == 3
    assert mathutils.floor(4.0) == 4
    assert mathutils.floor(-1.2) == -2


def test_floor_with_options_no_floor():
    options = [5, 10, 15]
    with pytest.raises(ValueError):
        mathutils.floor(3, options=options)

def test_floor_options_unsorted():
    options = [10, 1, 5]
    assert mathutils.floor(6, options=options) == 5

# --- Bits class tests ---

def test_bits_init_int():
    b = mathutils.Bits(5, 4)
    assert b.val == 5
    assert b.len == 4
    assert b.as_bin() == '0101'

def test_bits_init_int_no_len():
    b = mathutils.Bits(5)
    assert b.val == 5
    assert b.len == 3
    assert b.as_bin() == '101'

def test_bits_init_list():
    b = mathutils.Bits([True, False, True, False])
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'
    assert b.as_list() == [True, False, True, False]

def test_bits_init_bin_str():
    b = mathutils.Bits('1010')
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'

def test_bits_init_hex_str():
    b = mathutils.Bits('0xA', 4)
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'


def test_bits_init_bytes():
    b = mathutils.Bits(b'1010')
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'

def test_bits_init_unicode():
    # Only relevant for Python 2, but should work in Python 3 as well
    b = mathutils.Bits(u'1010')
    assert b.val == 10
    assert b.len == 4
    assert b.as_bin() == '1010'

def test_bits_init_invalid_type():
    with pytest.raises(TypeError):
        mathutils.Bits(object())

def test_bits_init_negative():
    with pytest.raises(ValueError):
        mathutils.Bits(-1)

def test_bits_init_value_too_large():
    with pytest.raises(ValueError):
        mathutils.Bits(8, 2)  # 8 cannot be represented with 2 bits

def test_bits_getitem_int():
    b = mathutils.Bits('1010')
    assert b[0] is True
    assert b[1] is False
    assert b[2] is True
    assert b[3] is False

def test_bits_getitem_slice():
    b = mathutils.Bits('1010')
    s = b[1:3]
    assert isinstance(s, mathutils.Bits)
    assert s.as_bin() == '01'

def test_bits_getitem_indexerror():
    b = mathutils.Bits('1010')
    with pytest.raises(IndexError):
        _ = b[4]

def test_bits_getitem_typeerror():
    b = mathutils.Bits('1010')
    with pytest.raises(TypeError):
        _ = b[1.5]

def test_bits_len():
    b = mathutils.Bits('1010')
    assert len(b) == 4

def test_bits_eq():
    b1 = mathutils.Bits('1010')
    b2 = mathutils.Bits('1010')
    b3 = mathutils.Bits('0101')
    assert b1 == b2
    assert not (b1 == b3)
    assert b1 != b3

def test_bits_eq_notimplemented():
    b = mathutils.Bits('1010')
    assert (b == 5) is False

def test_bits_or_and():
    b1 = mathutils.Bits('1010')
    b2 = mathutils.Bits('0101')
    b_or = b1 | b2
    b_and = b1 & b2
    assert b_or.as_bin() == '1111'
    assert b_and.as_bin() == '0000'


def test_bits_lshift():
    b = mathutils.Bits('1010')
    b2 = b << 2
    assert b2.as_bin() == '101000'

def test_bits_rshift():
    b = mathutils.Bits('1010')
    b2 = b >> 2
    assert b2.as_bin() == '10'

def test_bits_hash():
    b1 = mathutils.Bits('1010')
    b2 = mathutils.Bits('1010')
    assert hash(b1) == hash(b2)

def test_bits_as_list():
    b = mathutils.Bits('1010')
    assert b.as_list() == [True, False, True, False]

def test_bits_as_bin():
    b = mathutils.Bits(10, 4)
    assert b.as_bin() == '1010'


def test_bits_as_int():
    b = mathutils.Bits(10, 4)
    assert b.as_int() == 10

def test_bits_as_bytes():
    b = mathutils.Bits(255, 8)
    assert b.as_bytes() == b'\xff'
    b = mathutils.Bits(1, 8)
    assert b.as_bytes() == b'\x01'
    b = mathutils.Bits(1, 9)
    assert b.as_bytes() == b'\x00\x01'

def test_bits_from_list():
    b = mathutils.Bits.from_list([True, False, True, False])
    assert b.as_bin() == '1010'

def test_bits_from_bin():
    b = mathutils.Bits.from_bin('1010')
    assert b.as_bin() == '1010'

def test_bits_from_hex():
    b = mathutils.Bits.from_hex('A')
    assert b.as_bin() == '1010'
    b = mathutils.Bits.from_hex('0xA')
    assert b.as_bin() == '1010'
    b = mathutils.Bits.from_hex(b'A')
    assert b.as_bin() == '1010'

def test_bits_from_int():
    b = mathutils.Bits.from_int(10, 4)
    assert b.as_bin() == '1010'


def test_bits_repr():
    b = mathutils.Bits('1010')
    assert repr(b) == "Bits('1010')"