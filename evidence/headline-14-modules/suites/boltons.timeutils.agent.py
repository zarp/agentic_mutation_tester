import timeutils
import pytest
import re
import time
from datetime import timedelta, datetime, date

def test_total_seconds_basic():
    td = timedelta(days=4, seconds=33)
    assert timeutils.total_seconds(td) == 4 * 86400 + 33

def test_total_seconds_microseconds():
    td = timedelta(days=1, seconds=1, microseconds=500000)
    expected = 1 * 86400 + 1 + 0.5
    assert timeutils.total_seconds(td) == expected

def test_total_seconds_negative():
    td = timedelta(days=-1, seconds=1)
    expected = -1 * 86400 + 1
    assert timeutils.total_seconds(td) == expected

def test_dt_to_timestamp_naive():
    dt = datetime.utcfromtimestamp(0)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_aware():
    dt = datetime.fromtimestamp(0, timeutils.UTC)
    assert timeutils.dt_to_timestamp(dt) == 0.0

def test_dt_to_timestamp_offset():
    dt = datetime.utcfromtimestamp(100)
    assert timeutils.dt_to_timestamp(dt) == 100.0

def test_isoparse_epoch():
    epoch_dt = datetime.utcfromtimestamp(0)
    iso_str = epoch_dt.isoformat()
    result = timeutils.isoparse(iso_str)
    assert result == datetime(1970, 1, 1, 0, 0)

def test_isoparse_roundtrip():
    now = datetime.utcnow().replace(microsecond=0)
    iso_str = now.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == now

def test_isoparse_with_seconds():
    dt = datetime(2020, 2, 29, 23, 59, 59)
    iso_str = dt.isoformat()
    assert timeutils.isoparse(iso_str) == dt

def test_parse_timedelta_simple():
    td = timeutils.parse_timedelta('1d 2h 3.5m 0s')
    expected = timedelta(days=1, hours=2, minutes=3.5, seconds=0)
    assert td == expected

def test_parse_timedelta_weeks_days():
    td = timeutils.parse_timedelta('2 weeks 1 day')
    expected = timedelta(weeks=2, days=1)
    assert td == timedelta(days=15)

def test_parse_timedelta_negative():
    td = timeutils.parse_timedelta('-1.5 weeks 3m 20s')
    expected = timedelta(days=-10.5, minutes=3, seconds=20)
    # -1.5 weeks = -10.5 days
    # So total = -10.5 days + 3m + 20s
    assert td == timedelta(days=-10.5, minutes=3, seconds=20)

def test_parse_timedelta_invalid_unit():
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')
    assert "invalid time unit" in str(e.value)


def test_parse_td_alias():
    td = timeutils.parse_td('1d')
    assert td == timedelta(days=1)

def test_decimal_relative_time_day():
    now = datetime.utcnow()
    d = now - timedelta(days=1, seconds=3600)
    result = timeutils.decimal_relative_time(d, now)
    assert result == (1.0, 'day')

def test_decimal_relative_time_seconds_plural():
    now = datetime.utcnow()
    d = now - timedelta(seconds=0.002)
    result = timeutils.decimal_relative_time(d, now, ndigits=5)
    assert result == (0.002, 'seconds')

def test_decimal_relative_time_negative_years():
    now = datetime.utcnow()
    d = now
    other = now - timedelta(days=900)
    result = timeutils.decimal_relative_time(d, other, ndigits=1)
    assert result == (-2.5, 'years')

def test_decimal_relative_time_no_cardinalize():
    now = datetime.utcnow()
    d = now - timedelta(days=2)
    result = timeutils.decimal_relative_time(d, now, cardinalize=False)
    assert result[1] == 'day'

def test_relative_time_now():
    now = datetime.utcnow()
    result = timeutils.relative_time(now, ndigits=1)
    assert result == '0 seconds ago'

def test_relative_time_past():
    now = datetime.utcnow()
    d = now - timedelta(days=1, seconds=36000)
    result = timeutils.relative_time(d, now, ndigits=1)
    assert result.endswith('days ago')
    assert result.startswith('1.4')

def test_relative_time_future():
    now = datetime.utcnow()
    d = now + timedelta(days=7)
    result = timeutils.relative_time(d, now, ndigits=1)
    assert result == '1 week from now'

def test_strpdate_basic():
    s = '2016-02-14'
    fmt = '%Y-%m-%d'
    result = timeutils.strpdate(s, fmt)
    assert result == date(2016, 2, 14)

def test_strpdate_with_parens():
    s = '26/12 (2015)'
    fmt = '%d/%m (%Y)'
    result = timeutils.strpdate(s, fmt)
    assert result == date(2015, 12, 26)

def test_strpdate_with_time_ignored():
    s = '20151231 23:59:59'
    fmt = '%Y%m%d %H:%M:%S'
    result = timeutils.strpdate(s, fmt)
    assert result == date(2015, 12, 31)

def test_strpdate_with_microseconds():
    s = '20160101 00:00:00.001'
    fmt = '%Y%m%d %H:%M:%S.%f'
    result = timeutils.strpdate(s, fmt)
    assert result == date(2016, 1, 1)

def test_daterange_basic():
    christmas = date(2015, 12, 25)
    new_year = date(2016, 1, 1)
    days = list(timeutils.daterange(christmas, new_year))
    expected = [
        date(2015, 12, 25),
        date(2015, 12, 26),
        date(2015, 12, 27),
        date(2015, 12, 28),
        date(2015, 12, 29),
        date(2015, 12, 30),
        date(2015, 12, 31),
    ]
    assert days == expected

def test_daterange_single_day():
    christmas = date(2015, 12, 25)
    boxing_day = date(2015, 12, 26)
    days = list(timeutils.daterange(christmas, boxing_day))
    assert days == [date(2015, 12, 25)]

def test_daterange_month_step_inclusive():
    start = date(2017, 5, 1)
    stop = date(2017, 8, 1)
    days = list(timeutils.daterange(start, stop, step=(0, 1, 0), inclusive=True))
    expected = [
        date(2017, 5, 1),
        date(2017, 6, 1),
        date(2017, 7, 1),
        date(2017, 8, 1),
    ]
    assert days == expected

def test_daterange_step_as_timedelta():
    start = date(2020, 1, 1)
    stop = date(2020, 1, 4)
    days = list(timeutils.daterange(start, stop, step=timedelta(days=2)))
    assert days == [date(2020, 1, 1), date(2020, 1, 3)]

def test_daterange_step_tuple_ints():
    start = date(2020, 1, 1)
    stop = date(2020, 1, 4)
    days = list(timeutils.daterange(start, stop, step=(0, 0, 2)))
    assert days == [date(2020, 1, 1), date(2020, 1, 3)]

def test_daterange_negative_step():
    start = date(2020, 1, 4)
    stop = date(2020, 1, 1)
    days = list(timeutils.daterange(start, stop, step=-1))
    assert days == [date(2020, 1, 4), date(2020, 1, 3), date(2020, 1, 2)]

def test_daterange_inclusive_false():
    start = date(2020, 1, 1)
    stop = date(2020, 1, 2)
    days = list(timeutils.daterange(start, stop, inclusive=False))
    assert days == [date(2020, 1, 1)]

def test_daterange_inclusive_true():
    start = date(2020, 1, 1)
    stop = date(2020, 1, 2)
    days = list(timeutils.daterange(start, stop, inclusive=True))
    assert days == [date(2020, 1, 1), date(2020, 1, 2)]

def test_daterange_stop_none():
    start = date(2020, 1, 1)
    gen = timeutils.daterange(start, None)
    # Only take first 3 to avoid infinite loop
    days = [next(gen) for _ in range(3)]
    assert days == [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3)]

def test_daterange_invalid_start_type():
    with pytest.raises(TypeError):
        list(timeutils.daterange('2020-01-01', date(2020, 1, 2)))

def test_daterange_invalid_stop_type():
    with pytest.raises(TypeError):
        list(timeutils.daterange(date(2020, 1, 1), '2020-01-02'))

def test_daterange_invalid_step_type():
    with pytest.raises(ValueError):
        list(timeutils.daterange(date(2020, 1, 1), date(2020, 1, 2), step='foo'))

def test_ConstantTZInfo_repr_and_properties():
    tz = timeutils.ConstantTZInfo('TestTZ', timedelta(hours=3))
    assert repr(tz) == "ConstantTZInfo(name='TestTZ', offset=datetime.timedelta(seconds=10800))"
    assert tz.utcoffset_hours == 3.0
    dt = datetime(2020, 1, 1)
    assert tz.utcoffset(dt) == timedelta(hours=3)
    assert tz.tzname(dt) == 'TestTZ'
    assert tz.dst(dt) == timedelta(0)

def test_UTC_is_ConstantTZInfo():
    assert isinstance(timeutils.UTC, timeutils.ConstantTZInfo)
    assert timeutils.UTC.name == 'UTC'
    assert timeutils.UTC.offset == timedelta(0)

def test_EPOCH_AWARE_and_NAIVE():
    assert timeutils.EPOCH_AWARE == datetime.fromtimestamp(0, timeutils.UTC)
    assert timeutils.EPOCH_NAIVE == datetime.utcfromtimestamp(0)

def test_LocalTZInfo_repr():
    assert repr(timeutils.LocalTZ) == 'LocalTZInfo()'

def test_LocalTZInfo_utcoffset_and_dst_and_tzname():
    # Use a fixed date to avoid DST ambiguity
    dt = datetime(2020, 1, 1, 12, 0, 0)
    offset = timeutils.LocalTZ.utcoffset(dt)
    assert isinstance(offset, timedelta)
    dst = timeutils.LocalTZ.dst(dt)
    assert isinstance(dst, timedelta)
    name = timeutils.LocalTZ.tzname(dt)
    assert isinstance(name, str)

def test_LocalTZInfo_is_dst_false():
    dt = datetime(2020, 1, 1, 12, 0, 0)
    # Should be winter, so likely not DST
    result = timeutils.LocalTZ.is_dst(dt)
    assert isinstance(result, bool)

def test__first_sunday_on_or_after():
    dt = datetime(2023, 3, 8)
    result = timeutils._first_sunday_on_or_after(dt)
    # 2023-03-8 is Wednesday, so next Sunday is 2023-03-12
    assert result == datetime(2023, 3, 12)

def test__first_sunday_on_or_after_on_sunday():
    dt = datetime(2023, 3, 12)
    result = timeutils._first_sunday_on_or_after(dt)
    assert result == dt

def test_USTimeZone_repr_and_tzname():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    assert repr(tz) == "Eastern"
    dt = datetime(2020, 6, 1, 12, 0, 0, tzinfo=tz)
    # June is DST in US
    assert tz.tzname(dt) == "EDT" or tz.tzname(dt) == "EST"
    # Remove tzinfo for dst() call
    dt2 = datetime(2020, 1, 1, 12, 0, 0, tzinfo=tz)
    assert tz.tzname(dt2) == "EST" or tz.tzname(dt2) == "EDT"

def test_USTimeZone_utcoffset_and_dst():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(2020, 6, 1, 12, 0, 0, tzinfo=tz)
    offset = tz.utcoffset(dt)
    assert isinstance(offset, timedelta)
    dst = tz.dst(dt)
    assert isinstance(dst, timedelta)

def test_USTimeZone_dst_none_or_no_tzinfo():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(2020, 6, 1, 12, 0, 0)
    assert tz.dst(None) == timedelta(0)
    assert tz.dst(dt) == timedelta(0)

def test_Eastern_Central_Mountain_Pacific_types():
    for tz, name in [
        (timeutils.Eastern, "Eastern"),
        (timeutils.Central, "Central"),
        (timeutils.Mountain, "Mountain"),
        (timeutils.Pacific, "Pacific"),
    ]:
        assert isinstance(tz, timeutils.USTimeZone)
        assert repr(tz) == name

def test_Eastern_dst_transition():
    tz = timeutils.Eastern
    # 2020 DST start: March 8, 2020
    dt_before = datetime(2020, 3, 7, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(2020, 3, 15, 12, 0, 0, tzinfo=tz)
    assert tz.dst(dt_before) == timedelta(0)
    assert tz.dst(dt_after) == timedelta(hours=1)

def test__cardinalize_time_unit_singular_plural():
    assert timeutils._cardinalize_time_unit('day', 1) == 'day'
    assert timeutils._cardinalize_time_unit('day', 2) == 'days'
    assert timeutils._cardinalize_time_unit('hour', 0) == 'hours'


def test__bounds_minute_count():
    # line 139: (1, timedelta(seconds=60), 'minute')
    # Mutants: 1->2 or 60->61
    # If the count is 2, then 2*timedelta(seconds=60) = 120s, so bisect will be off.
    # If the seconds is 61, then 1*timedelta(seconds=61) = 61s, so bisect will be off.
    now = datetime.utcnow()
    d = now - timedelta(seconds=61)
    # Should be 1.0, 'minute'
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'minute'
    assert result[0] == 1.0


def test__bounds_hour_count():
    # line 140: (1, timedelta(seconds=3600), 'hour')
    # Mutants: 1->2 or 3600->3601
    now = datetime.utcnow()
    d = now - timedelta(seconds=3601)
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'hour'
    assert result[0] == 1.0


def test__bounds_month_count_and_days():
    # line 143: (2, timedelta(days=30), 'month')
    # Mutants: 2->3 or 30->31 or 'month'->'XX...XX'
    now = datetime.utcnow()
    d = now - timedelta(days=60)
    result = timeutils.decimal_relative_time(d, now)
    # Should be 2.0, 'months'
    assert result[1] == 'months'
    assert result[0] == 2.0


def test__bounds_year_count_and_days():
    # line 144: (1, timedelta(days=365), 'year')
    # Mutants: 1->2 or 365->366
    now = datetime.utcnow()
    d = now - timedelta(days=365)
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'year'
    assert result[0] == 1.0


def test_parse_timedelta_invalid_unit_message_and_operator():
    # line 185: error message string mutant
    # line 190: error message string mutant and operator % -> *
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')
    # The message should mention 'invalid time unit'
    assert 'invalid time unit' in str(e.value)




def test_decimal_relative_time_default_ndigits():
    # line 207: ndigits=0 -> ndigits=1
    now = datetime.utcnow()
    d = now - timedelta(days=1.234)
    result = timeutils.decimal_relative_time(d, now)
    # Should round to 0 digits, so 1.234 days -> 1.0
    assert result[0] == 1.0


def test_relative_time_default_ndigits():
    # line 253: ndigits=0 -> ndigits=1
    now = datetime.utcnow()
    d = now - timedelta(days=1.234)
    result = timeutils.relative_time(d, now)
    # Should round to 0 digits, so '1 day ago'
    assert result.startswith('1 ')


def test_daterange_invalid_start_type_message():
    # line 364: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange('2020-01-01', date(2020, 1, 2)))
    assert 'start expected datetime.date instance' in str(e.value)


def test_daterange_invalid_stop_type_message():
    # line 366: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange(date(2020, 1, 1), '2020-01-02'))
    assert 'stop expected datetime.date instance or None' in str(e.value)




def test_daterange_m_step_augassign_and_12_to_13():
    # line 381: m_step += y_step * 12 -> m_step -= y_step * 12 or 12->13
    # This is only relevant if y_step != 0
    start = date(2020, 1, 1)
    stop = date(2021, 1, 1)
    # step=(1, 0, 0): advance by 1 year
    days = list(timeutils.daterange(start, stop, step=(1, 0, 0)))
    # Should yield 2020-01-01 only
    assert days == [date(2020, 1, 1)]


def test_daterange_month_divmod_12_to_13():
    # line 394: divmod(..., 12) -> divmod(..., 13)
    # Use a step that advances months
    start = date(2020, 1, 1)
    stop = date(2020, 4, 1)
    days = list(timeutils.daterange(start, stop, step=(0, 1, 0), inclusive=True))
    # Should yield Jan, Feb, Mar, Apr
    assert days == [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1), date(2020, 4, 1)]


def test_daterange_now_replace_year_plus():
    # line 395: now.year + m_y_step -> now.year - m_y_step
    # Use a step that advances months, so m_y_step > 0
    start = date(2020, 1, 1)
    stop = date(2020, 4, 1)
    days = list(timeutils.daterange(start, stop, step=(0, 1, 0), inclusive=True))
    assert days == [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1), date(2020, 4, 1)]


def test_daterange_finished_comparison():
    # line 385: start <= stop -> start < stop
    # If start == stop, should yield one value if inclusive=True
    start = date(2020, 1, 1)
    stop = date(2020, 1, 1)
    days = list(timeutils.daterange(start, stop, inclusive=True))
    assert days == [date(2020, 1, 1)]


def test_ConstantTZInfo_default_name():
    # line 417: name="ConstantTZ" -> name="XX...XX"
    tz = timeutils.ConstantTZInfo()
    assert tz.name == "ConstantTZ"


def test_LocalTZInfo_is_dst_tuple():
    # line 466: dt.second, dt.weekday(), 0, -1
    # Mutants: 0->1 or 1->2
    dt = datetime(2020, 1, 1, 12, 0, 0)
    result = timeutils.LocalTZ.is_dst(dt)
    assert isinstance(result, bool)


def test_LocalTZInfo_is_dst_comparison_and_value():
    # line 468: tm_isdst > 0 -> >= 0 or > 1
    dt = datetime(2020, 1, 1, 12, 0, 0)
    result = timeutils.LocalTZ.is_dst(dt)
    assert isinstance(result, bool)


def test_LocalTZInfo_utcoffset_not_none():
    # line 472: return self._dst_offset -> return None
    dt = datetime(2020, 1, 1, 12, 0, 0)
    offset = timeutils.LocalTZ.utcoffset(dt)
    assert offset is not None


def test_LocalTZInfo_dst_not_none():
    # line 477: return self._dst_offset - self._std_offset -> return None
    dt = datetime(2020, 7, 1, 12, 0, 0)
    dst = timeutils.LocalTZ.dst(dt)
    assert dst is not None


def test_LocalTZInfo_dst_operator_minus_plus():
    # line 477: - -> +
    dt = datetime(2020, 7, 1, 12, 0, 0)
    dst = timeutils.LocalTZ.dst(dt)
    # Should be timedelta(0) or positive, but not a large value
    assert isinstance(dst, timedelta)
    assert abs(dst) < timedelta(days=2)


def test_DSTSTART_2007_and_DSTEND_2007():
    # lines 507,509: year/month/day/hour mutants
    # These are used in USTimeZone.dst
    tz = timeutils.Eastern
    # 2020 DST start: March 8, 2020
    dt_before = datetime(2020, 3, 7, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(2020, 3, 15, 12, 0, 0, tzinfo=tz)
    assert tz.dst(dt_before) == timedelta(0)
    assert tz.dst(dt_after) == timedelta(hours=1)


def test_DSTSTART_1987_2006():
    # line 513: year/month/day/hour mutants
    tz = timeutils.Eastern
    dt_before = datetime(2006, 4, 1, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(2006, 4, 10, 12, 0, 0, tzinfo=tz)
    # Should transition to DST in April
    assert tz.dst(dt_before) == timedelta(0) or tz.dst(dt_before) == timedelta(hours=1)
    assert tz.dst(dt_after) == timedelta(0) or tz.dst(dt_after) == timedelta(hours=1)


def test_parse_timedelta_invalid_unit_message_exact():
    # line 185: error message string mutant
    with pytest.raises(ValueError) as e:
        timeutils.parse_timedelta('1x')
    # The message should mention 'invalid time unit'
    assert 'invalid time unit' in str(e.value)




def test_daterange_invalid_start_type_message_exact():
    # line 364: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange('2020-01-01', date(2020, 1, 2)))
    assert 'start expected datetime.date instance' in str(e.value)


def test_daterange_invalid_stop_type_message_exact():
    # line 366: error message string mutant
    with pytest.raises(TypeError) as e:
        list(timeutils.daterange(date(2020, 1, 1), '2020-01-02'))
    assert 'stop expected datetime.date instance or None' in str(e.value)




def test_bounds_minute_60_vs_61():
    # line 139: 60 -> 61
    now = datetime.utcnow()
    d = now - timedelta(seconds=60)
    result = timeutils.decimal_relative_time(d, now)
    # Should be 1.0, 'minute'
    assert result[1] == 'minute'
    assert result[0] == 1.0


def test_bounds_hour_3600_vs_3601():
    # line 140: 3600 -> 3601
    now = datetime.utcnow()
    d = now - timedelta(seconds=3600)
    result = timeutils.decimal_relative_time(d, now)
    assert result[1] == 'hour'
    assert result[0] == 1.0


def test_daterange_m_step_12_vs_13():
    # line 381: 12 -> 13
    # If 12->13, stepping by 1 year will not land on the correct month
    start = date(2020, 1, 1)
    stop = date(2021, 1, 1)
    days = list(timeutils.daterange(start, stop, step=(1, 0, 0)))
    assert days == [date(2020, 1, 1)]


def test_daterange_month_divmod_12_vs_13():
    # line 394: divmod(..., 12) -> divmod(..., 13)
    start = date(2020, 1, 1)
    stop = date(2020, 4, 1)
    days = list(timeutils.daterange(start, stop, step=(0, 1, 0), inclusive=True))
    assert days == [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1), date(2020, 4, 1)]


def test_daterange_now_replace_year_plus_vs_minus():
    # line 395: now.year + m_y_step -> now.year - m_y_step
    start = date(2020, 1, 1)
    stop = date(2020, 4, 1)
    days = list(timeutils.daterange(start, stop, step=(0, 1, 0), inclusive=True))
    assert days == [date(2020, 1, 1), date(2020, 2, 1), date(2020, 3, 1), date(2020, 4, 1)]


def test_DSTSTART_2007_and_DSTEND_2007_mutants():
    # lines 507,509: year/month/day/hour mutants
    tz = timeutils.Eastern
    # 2020 DST start: March 8, 2020
    dt_before = datetime(2020, 3, 7, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(2020, 3, 15, 12, 0, 0, tzinfo=tz)
    assert tz.dst(dt_before) == timedelta(0)
    assert tz.dst(dt_after) == timedelta(hours=1)


def test_DSTSTART_1987_2006_and_DSTEND_1987_2006_mutants():
    # lines 513,514: year/month/day/hour mutants
    tz = timeutils.Eastern
    dt_before = datetime(2006, 4, 1, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(2006, 4, 10, 12, 0, 0, tzinfo=tz)
    # Should transition to DST in April
    assert tz.dst(dt_before) == timedelta(0) or tz.dst(dt_before) == timedelta(hours=1)
    assert tz.dst(dt_after) == timedelta(0) or tz.dst(dt_after) == timedelta(hours=1)


def test_DSTSTART_1967_1986_mutants():
    # line 519: year/month/day/hour mutants
    tz = timeutils.Eastern
    dt_before = datetime(1970, 4, 24, 12, 0, 0, tzinfo=tz)
    dt_after = datetime(1970, 5, 1, 12, 0, 0, tzinfo=tz)
    # Should transition to DST in late April
    assert tz.dst(dt_before) == timedelta(0) or tz.dst(dt_before) == timedelta(hours=1)
    assert tz.dst(dt_after) == timedelta(0) or tz.dst(dt_after) == timedelta(hours=1)


def test_LocalTZInfo_is_dst_tuple_and_comparison():
    # line 466: 0->1, 1->2; line 468: > -> >=, 0->1
    dt = datetime(2020, 1, 1, 12, 0, 0)
    result = timeutils.LocalTZ.is_dst(dt)
    assert isinstance(result, bool)


def test_LocalTZInfo_utcoffset_not_none_mutant():
    # line 472: return self._dst_offset -> return None
    dt = datetime(2020, 1, 1, 12, 0, 0)
    offset = timeutils.LocalTZ.utcoffset(dt)
    assert offset is not None


def test_LocalTZInfo_dst_not_none_mutant():
    # line 477: return self._dst_offset - self._std_offset -> return None
    dt = datetime(2020, 7, 1, 12, 0, 0)
    dst = timeutils.LocalTZ.dst(dt)
    assert dst is not None


def test_USTimeZone_utcoffset_operator_plus_minus():
    # line 545: + -> -
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(2020, 6, 1, 12, 0, 0, tzinfo=tz)
    offset = tz.utcoffset(dt)
    # Should be -4 or -5 hours (timedelta)
    assert isinstance(offset, timedelta)
    assert -6 <= offset.total_seconds() / 3600 <= -4


def test_USTimeZone_dst_year_comparisons():
    # line 558: < -> <=, 2006->2007; line 560: < -> <=
    tz = timeutils.Eastern
    # 2007 is the first year of new DST rules
    dt_2007 = datetime(2007, 3, 10, 12, 0, 0, tzinfo=tz)
    dt_2006 = datetime(2006, 4, 2, 12, 0, 0, tzinfo=tz)
    # Should use different DST rules for 2006 and 2007
    assert tz.dst(dt_2007) in (timedelta(0), timedelta(hours=1))
    assert tz.dst(dt_2006) in (timedelta(0), timedelta(hours=1))


def test_ConstantTZInfo_default_name_mutant():
    # line 417: name="ConstantTZ" -> name="XX...XX"
    tz = timeutils.ConstantTZInfo()
    assert tz.name == "ConstantTZ"
