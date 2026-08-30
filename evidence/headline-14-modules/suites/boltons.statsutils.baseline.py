import pytest
import math
import statsutils

# Helper for floating point comparison
def approx(a, b, rel=1e-9, abs=0.0):
    return abs(a - b) <= max(rel * max(abs(a), abs(b)), abs)

def test_stats_basic_properties():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    assert s.count == 5
    assert s.mean == 3.0
    assert s.max == 5
    assert s.min == 1
    assert s.median == 3
    assert s.iqr == 2
    assert s.trimean == 3.0
    assert s.variance == 2.0
    assert s.std_dev == pytest.approx(math.sqrt(2.0))
    assert s.median_abs_dev == 1.0
    assert s.mad == 1.0
    assert s.rel_std_dev == pytest.approx(s.std_dev / abs(s.mean))
    # Skewness and kurtosis for symmetric data
    assert s.skewness == pytest.approx(0.0)
    assert s.kurtosis > 0

def test_stats_empty_data():
    s = statsutils.Stats([])
    assert s.count == 0
    assert s.mean == 0.0
    assert s.max == 0.0
    assert s.min == 0.0
    assert s.median == 0.0
    assert s.iqr == 0.0
    assert s.trimean == 0.0
    assert s.variance == 0.0
    assert s.std_dev == 0.0
    assert s.median_abs_dev == 0.0
    assert s.mad == 0.0
    assert s.rel_std_dev == 0.0
    assert s.skewness == 0.0
    assert s.kurtosis == 0.0


def test_stats_sorted_flag():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data, is_sorted=True)
    # Should not sort again
    assert s.min == 1
    assert s.max == 5
    assert s.median == 3

def test_stats_use_copy_false():
    data = [5, 4, 3, 2, 1]
    s = statsutils.Stats(data, use_copy=False)
    # Should not sort original data
    assert s.min == 1
    assert s.max == 5
    assert s.median == 3

def test_stats_clear_cache():
    data = [1, 2, 3]
    s = statsutils.Stats(data)
    m1 = s.mean
    s.data.append(4)
    s.clear_cache()
    m2 = s.mean
    assert m1 != m2
    assert m2 == pytest.approx(2.5)

def test_stats_get_quantile():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    assert s.get_quantile(0.0) == 1
    assert s.get_quantile(1.0) == 5
    assert s.get_quantile(0.5) == 3
    assert s.get_quantile(0.25) == 2.0
    assert s.get_quantile(0.75) == 4.0
    with pytest.raises(ValueError):
        s.get_quantile(-0.1)
    with pytest.raises(ValueError):
        s.get_quantile(1.1)

def test_stats_get_zscore():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    mean = s.mean
    std = s.std_dev
    assert s.get_zscore(mean) == 0
    assert s.get_zscore(mean + std) == pytest.approx(1.0)
    assert s.get_zscore(mean - std) == pytest.approx(-1.0)
    # std_dev == 0
    s2 = statsutils.Stats([1, 1, 1])
    assert s2.get_zscore(1) == 0
    assert s2.get_zscore(2) == float('inf')
    assert s2.get_zscore(0) == float('-inf')

def test_stats_trim_relative():
    data = list(range(20))
    s = statsutils.Stats(data)
    s.trim_relative(0.1)
    assert s.data == list(range(2, 18))
    # Should raise for invalid trim
    s2 = statsutils.Stats(list(range(10)))
    with pytest.raises(ValueError):
        s2.trim_relative(-0.1)
    with pytest.raises(ValueError):
        s2.trim_relative(0.5)
    # No trim if amount is 0
    s3 = statsutils.Stats(list(range(10)))
    s3.trim_relative(0.0)
    assert s3.data == list(range(10))

def test_stats_get_histogram_counts_and_format_histogram():
    data = list(range(20)) + list(range(5, 15)) + [10]
    s = statsutils.Stats(data)
    counts = s.get_histogram_counts()
    # Should be a list of (bin, count)
    assert isinstance(counts, list)
    assert all(isinstance(x, tuple) and len(x) == 2 for x in counts)
    # Should sum to len(data)
    total = sum(c for b, c in counts)
    assert total == len(data)
    # Format histogram returns a string
    hist = s.format_histogram()
    assert isinstance(hist, str)
    assert "#" in hist

def test_stats_get_histogram_counts_bins_argument():
    data = list(range(10))
    s = statsutils.Stats(data)
    # bins as int
    counts = s.get_histogram_counts(bins=5)
    assert len(counts) == 5
    # bins as list
    bins = [0, 2, 4, 6, 8]
    counts2 = s.get_histogram_counts(bins=bins)
    assert len(counts2) == len(bins)
    # bins as invalid type
    with pytest.raises(ValueError):
        s.get_histogram_counts(bins="bad")

def test_stats_get_histogram_counts_bin_digits():
    data = [0.123, 0.234, 0.345, 0.456, 0.567]
    s = statsutils.Stats(data)
    counts = s.get_histogram_counts(bin_digits=2)
    assert isinstance(counts, list)

def test_stats_get_histogram_counts_unexpected_kw():
    data = [1, 2, 3]
    s = statsutils.Stats(data)
    with pytest.raises(TypeError):
        s.get_histogram_counts(foo=1)

def test_stats_format_histogram_custom_format_bin():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    def fmt(b): return f"{b} units"
    hist = s.format_histogram(format_bin=fmt)
    assert "units" in hist

def test_stats_describe_formats():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    d = s.describe(format='dict')
    assert isinstance(d, dict)
    l = s.describe(format='list')
    assert isinstance(l, list)
    t = s.describe(format='text')
    assert isinstance(t, str)
    # Invalid format
    with pytest.raises(ValueError):
        s.describe(format='bad')

def test_stats_describe_quantiles():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    d = s.describe(quantiles=[0.1, 0.5, 0.9], format='dict')
    assert '0.1' in d and '0.5' in d and '0.9' in d




def test_module_level_functions():
    data = [1, 2, 3, 4, 5]
    assert statsutils.mean(data) == 3.0
    assert statsutils.median(data) == 3
    assert statsutils.variance(data) == 2.0
    assert statsutils.std_dev(data) == pytest.approx(math.sqrt(2.0))
    assert statsutils.median_abs_dev(data) == 1.0
    assert statsutils.iqr(data) == 2
    assert statsutils.trimean(data) == 3.0
    assert statsutils.skewness(data) == pytest.approx(0.0)
    assert statsutils.kurtosis(data) > 0
    assert statsutils.rel_std_dev(data) == pytest.approx(
        statsutils.std_dev(data) / abs(statsutils.mean(data))
    )

def test_module_level_describe():
    data = [1, 2, 3, 4, 5]
    d = statsutils.describe(data, format='dict')
    assert isinstance(d, dict)
    t = statsutils.describe(data, format='text')
    assert isinstance(t, str)
    l = statsutils.describe(data, format='list')
    assert isinstance(l, list)

def test_format_histogram_counts_basic():
    bin_counts = [(0, 2), (1, 3), (2, 1)]
    s = statsutils.format_histogram_counts(bin_counts)
    assert isinstance(s, str)
    assert "#" in s

def test_format_histogram_counts_custom_width_and_format_bin():
    bin_counts = [(0, 2), (1, 3), (2, 1)]
    s = statsutils.format_histogram_counts(bin_counts, width=20, format_bin=lambda x: f"B{x}")
    assert "B0" in s


def test_stats_repr_and_iter():
    data = [1, 2, 3]
    s = statsutils.Stats(data)
    assert list(iter(s)) == data
    assert len(s) == 3

def test_stats_get_bin_bounds_small_data():
    data = [1, 2]
    s = statsutils.Stats(data)
    bins = s._get_bin_bounds()
    assert isinstance(bins, list)
    assert len(bins) == 2

def test_stats_get_bin_bounds_with_max():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    bins = s._get_bin_bounds(with_max=True)
    assert bins[-1] == float(max(data))

def test_stats_get_bin_bounds_count():
    data = [1, 2, 3, 4, 5]
    s = statsutils.Stats(data)
    bins = s._get_bin_bounds(count=3)
    assert len(bins) == 3

def test_stats_get_bin_bounds_large_data():
    data = list(range(100))
    s = statsutils.Stats(data)
    bins = s._get_bin_bounds()
    assert isinstance(bins, list)
    assert bins[0] == min(data)

def test_stats__get_quantile_interpolation():
    data = [1, 2, 3, 4]
    s = statsutils.Stats(data)
    sorted_data = sorted(data)
    # 0.25 quantile between 1 and 2
    q = s._get_quantile(sorted_data, 0.25)
    assert q == pytest.approx(1.75)
    # 0.75 quantile between 3 and 4
    q2 = s._get_quantile(sorted_data, 0.75)
    assert q2 == pytest.approx(3.25)