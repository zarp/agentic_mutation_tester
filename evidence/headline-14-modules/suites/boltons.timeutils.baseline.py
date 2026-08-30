import pytest
import time
import re
from datetime import datetime, timedelta, date

import timeutils

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

def test_dt_to_timestamp_now_close():
    now = datetime.utcnow()
    ts = timeutils.dt_to_timestamp(now)
    assert abs(ts - time.time()) < 2  # allow for test execution delay

def test_isoparse_epoch():
    epoch_dt = datetime.utcfromtimestamp(0)
    iso_str = epoch_dt.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == epoch_dt

def test_isoparse_roundtrip():
    now = datetime.utcnow().replace(microsecond=0)
    iso_str = now.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == now

def test_isoparse_with_microseconds():
    now = datetime.utcnow().replace(microsecond=123456)
    iso_str = now.isoformat()
    parsed = timeutils.isoparse(iso_str)
    assert parsed == now

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
    expected = timedelta(weeks=-1.5, minutes=3, seconds=20)
    assert td == timedelta(days=-11, seconds=43400)

def test_parse_timedelta_invalid_unit():
    with pytest.raises(ValueError):
        timeutils.parse_timedelta('1x')


def test_parse_td_alias():
    td = timeutils.parse_td('1d')
    assert td == timedelta(days=1)

@pytest.mark.parametrize("value,unit,expected", [
    (1, "day", "day"),
    (2, "day", "days"),
    (0, "hour", "hours"),
    (1, "minute", "minute"),
    (3, "minute", "minutes"),
])
def test_cardinalize_time_unit(value, unit, expected):
    assert timeutils._cardinalize_time_unit(unit, value) == expected

def test_decimal_relative_time_basic():
    now = datetime.utcnow()
    d = now - timedelta(days=1, seconds=3600)
    val, unit = timeutils.decimal_relative_time(d, now)
    assert val == 1.0
    assert unit == "day"

def test_decimal_relative_time_seconds():
    now = datetime.utcnow()
    d = now - timedelta(seconds=0.002)
    val, unit = timeutils.decimal_relative_time(d, now, ndigits=5)
    assert abs(val - 0.002) < 1e-6
    assert unit == "seconds"

def test_decimal_relative_time_negative():
    now = datetime.utcnow()
    d = now
    other = now - timedelta(days=900)
    val, unit = timeutils.decimal_relative_time(d, other, ndigits=1)
    assert val == -2.5
    assert unit == "years"

def test_decimal_relative_time_no_cardinalize():
    now = datetime.utcnow()
    d = now - timedelta(days=2)
    val, unit = timeutils.decimal_relative_time(d, now, cardinalize=False)
    assert unit == "day"

def test_relative_time_now():
    now = datetime.utcnow()
    s = timeutils.relative_time(now, ndigits=1)
    assert re.match(r"0(\.0+)? seconds ago", s)

def test_relative_time_past():
    now = datetime.utcnow()
    d = now - timedelta(days=1, seconds=36000)
    s = timeutils.relative_time(d, now, ndigits=1)
    assert s.endswith("ago")
    assert "days" in s or "day" in s

def test_relative_time_future():
    now = datetime.utcnow()
    d = now + timedelta(days=7)
    s = timeutils.relative_time(d, now, ndigits=1)
    assert s.endswith("from now")
    assert "week" in s

def test_strpdate_basic():
    d = timeutils.strpdate('2016-02-14', '%Y-%m-%d')
    assert d == date(2016, 2, 14)

def test_strpdate_with_parens():
    d = timeutils.strpdate('26/12 (2015)', '%d/%m (%Y)')
    assert d == date(2015, 12, 26)

def test_strpdate_with_time():
    d = timeutils.strpdate('20151231 23:59:59', '%Y%m%d %H:%M:%S')
    assert d == date(2015, 12, 31)

def test_strpdate_with_microseconds():
    d = timeutils.strpdate('20160101 00:00:00.001', '%Y%m%d %H:%M:%S.%f')
    assert d == date(2016, 1, 1)

def test_daterange_basic():
    christmas = date(2015, 12, 25)
    new_year = date(2016, 1, 1)
    days = list(timeutils.daterange(christmas, new_year))
    assert days[0] == christmas
    assert days[-1] == date(2015, 12, 31)
    assert len(days) == 7

def test_daterange_single_day():
    christmas = date(2015, 12, 25)
    boxing_day = date(2015, 12, 26)
    days = list(timeutils.daterange(christmas, boxing_day))
    assert days == [christmas]

def test_daterange_month_step():
    days = list(timeutils.daterange(date(2017, 5, 1), date(2017, 8, 1), step=(0, 1, 0), inclusive=True))
    assert days == [
        date(2017, 5, 1),
        date(2017, 6, 1),
        date(2017, 7, 1),
        date(2017, 8, 1),
    ]

def test_daterange_negative_step():
    start = date(2017, 8, 1)
    stop = date(2017, 5, 1)
    days = list(timeutils.daterange(start, stop, step=-1))
    assert days[0] == start
    assert days[-1] == date(2017, 5, 2)

def test_daterange_step_types():
    start = date(2020, 1, 1)
    stop = date(2020, 1, 5)
    # step as timedelta
    days = list(timeutils.daterange(start, stop, step=timedelta(days=2)))
    assert days == [date(2020, 1, 1), date(2020, 1, 3)]
    # step as int
    days2 = list(timeutils.daterange(start, stop, step=2))
    assert days2 == [date(2020, 1, 1), date(2020, 1, 3)]

def test_daterange_invalid_start():
    with pytest.raises(TypeError):
        list(timeutils.daterange("2020-01-01", date(2020, 1, 2)))

def test_daterange_invalid_stop():
    with pytest.raises(TypeError):
        list(timeutils.daterange(date(2020, 1, 1), "2020-01-02"))

def test_daterange_invalid_step():
    with pytest.raises(ValueError):
        list(timeutils.daterange(date(2020, 1, 1), date(2020, 1, 2), step="foo"))

def test_daterange_infinite(monkeypatch):
    # Test that stop=None yields an infinite generator (we break after 3)
    start = date(2020, 1, 1)
    gen = timeutils.daterange(start, None)
    days = []
    for _, d in zip(range(3), gen):
        days.append(d)
    assert days == [date(2020, 1, 1), date(2020, 1, 2), date(2020, 1, 3)]

def test_ConstantTZInfo_repr_and_properties():
    tz = timeutils.ConstantTZInfo("TestTZ", timedelta(hours=3))
    assert repr(tz) == "ConstantTZInfo(name='TestTZ', offset=datetime.timedelta(seconds=10800))"
    assert tz.utcoffset_hours == 3.0
    dt = datetime(2020, 1, 1)
    assert tz.utcoffset(dt) == timedelta(hours=3)
    assert tz.tzname(dt) == "TestTZ"
    assert tz.dst(dt) == timedelta(0)

def test_UTC_singleton():
    assert isinstance(timeutils.UTC, timeutils.ConstantTZInfo)
    assert timeutils.UTC.name == "UTC"
    assert timeutils.UTC.offset == timedelta(0)

def test_EPOCH_AWARE_and_NAIVE():
    assert timeutils.EPOCH_AWARE.tzinfo == timeutils.UTC
    assert timeutils.EPOCH_NAIVE.tzinfo is None
    assert timeutils.EPOCH_AWARE.replace(tzinfo=None) == timeutils.EPOCH_NAIVE

def test_LocalTZInfo_repr():
    tz = timeutils.LocalTZ
    assert repr(tz) == "LocalTZInfo()"

def test_LocalTZInfo_utcoffset_and_dst(monkeypatch):
    tz = timeutils.LocalTZ
    dt = datetime(2020, 1, 1)
    # Patch is_dst to return False
    monkeypatch.setattr(tz, "is_dst", lambda dt: False)
    assert tz.utcoffset(dt) == tz._std_offset
    assert tz.dst(dt) == timedelta(0)
    # Patch is_dst to return True
    monkeypatch.setattr(tz, "is_dst", lambda dt: True)
    assert tz.utcoffset(dt) == tz._dst_offset
    assert tz.dst(dt) == tz._dst_offset - tz._std_offset

def test_LocalTZInfo_tzname(monkeypatch):
    tz = timeutils.LocalTZ
    monkeypatch.setattr(tz, "is_dst", lambda dt: False)
    assert tz.tzname(datetime(2020, 1, 1)) == time.tzname[0]
    monkeypatch.setattr(tz, "is_dst", lambda dt: True)
    assert tz.tzname(datetime(2020, 7, 1)) == time.tzname[1]

def test_first_sunday_on_or_after():
    dt = datetime(2023, 3, 8)  # Wednesday
    sunday = timeutils._first_sunday_on_or_after(dt)
    assert sunday.weekday() == 6
    assert sunday >= dt

def test_USTimeZone_repr_and_tzname():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    assert repr(tz) == "Eastern"
    dt = datetime(2020, 1, 1, tzinfo=tz)
    # Should be standard time in January
    assert tz.tzname(dt) == "EST"
    # Should be DST in July
    dt_dst = datetime(2020, 7, 1, tzinfo=tz)
    assert tz.tzname(dt_dst) == "EDT"

def test_USTimeZone_utcoffset_and_dst():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(2020, 1, 1, tzinfo=tz)
    assert tz.utcoffset(dt) == timedelta(hours=-5)
    assert tz.dst(dt) == timedelta(0)
    dt_dst = datetime(2020, 7, 1, tzinfo=tz)
    assert tz.utcoffset(dt_dst) == timedelta(hours=-4)
    assert tz.dst(dt_dst) == timedelta(hours=1)

def test_USTimeZone_dst_none():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(2020, 1, 1)
    # dt.tzinfo is None, should return ZERO
    assert tz.dst(dt) == timedelta(0)
    # dt is None
    assert tz.dst(None) == timedelta(0)

def test_USTimeZone_pre_1967():
    tz = timeutils.USTimeZone(-5, "Eastern", "EST", "EDT")
    dt = datetime(1960, 1, 1, tzinfo=tz)
    assert tz.dst(dt) == timedelta(0)

def test_Eastern_Central_Mountain_Pacific_types():
    for tz, name, std, dst in [
        (timeutils.Eastern, "Eastern", "EST", "EDT"),
        (timeutils.Central, "Central", "CST", "CDT"),
        (timeutils.Mountain, "Mountain", "MST", "MDT"),
        (timeutils.Pacific, "Pacific", "PST", "PDT"),
    ]:
        assert isinstance(tz, timeutils.USTimeZone)
        assert repr(tz) == name
        dt = datetime(2020, 1, 1, tzinfo=tz)
        assert tz.tzname(dt) == std
        dt_dst = datetime(2020, 7, 1, tzinfo=tz)
        assert tz.tzname(dt_dst) == dst