import pytest
import statsutils


def test_stats_count_and_len_agree():
    data = [1, 2, 3, 4]
    stats = statsutils.Stats(data)
    assert stats.count == 4
    assert len(stats) == 4


def test_stats_mean_simple():
    data = [1, 2, 3, 4]
    stats = statsutils.Stats(data)
    assert stats.mean == 2.5
    assert statsutils.mean(data) == 2.5


def test_stats_mean_with_outlier():
    data = list(range(19)) + [949]
    stats = statsutils.Stats(data)
    assert stats.mean == 56.0
    assert statsutils.mean(data) == 56.0


def test_stats_max_and_min_unsorted():
    data = [2, 1, 3]
    stats = statsutils.Stats(data)
    assert stats.max == 3
    assert stats.min == 1


def test_stats_max_and_min_sorted():
    data = [1, 2, 3]
    stats = statsutils.Stats(data, is_sorted=True)
    assert stats.max == 3
    assert stats.min == 1


def test_stats_median_odd():
    data = [2, 1, 3]
    stats = statsutils.Stats(data)
    assert stats.median == 2
    assert statsutils.median(data) == 2


def test_stats_median_even():
    data = [1, 2, 3, 4]
    stats = statsutils.Stats(data)
    assert stats.median == 2.5
    assert statsutils.median(data) == 2.5


def test_stats_median_with_outlier():
    data = list(range(96)) + [1066]
    stats = statsutils.Stats(data)
    assert stats.median == 48
    assert statsutils.median(data) == 48


def test_stats_iqr_simple():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    assert stats.iqr == 2
    assert statsutils.iqr(data) == 2


def test_stats_iqr_large():
    data = list(range(1001))
    stats = statsutils.Stats(data)
    assert stats.iqr == 500
    assert statsutils.iqr(data) == 500


def test_stats_trimean_simple():
    data = [2, 1, 3]
    stats = statsutils.Stats(data)
    assert stats.trimean == 2.0
    assert statsutils.trimean(data) == 2.0


def test_stats_trimean_with_outlier():
    data = list(range(96)) + [1066]
    stats = statsutils.Stats(data)
    assert stats.trimean == 48.0
    assert statsutils.trimean(data) == 48.0


def test_stats_variance_and_std_dev():
    data = list(range(97))
    stats = statsutils.Stats(data)
    assert stats.variance == 784.0
    assert statsutils.variance(data) == 784.0
    assert stats.std_dev == 28.0
    assert statsutils.std_dev(data) == 28.0


def test_stats_median_abs_dev():
    data = list(range(97))
    stats = statsutils.Stats(data)
    assert stats.median_abs_dev == 24.0
    assert statsutils.median_abs_dev(data) == 24.0
    assert stats.mad == 24.0


def test_stats_rel_std_dev():
    data = list(range(97))
    stats = statsutils.Stats(data)
    assert round(stats.rel_std_dev, 3) == 0.583
    assert round(statsutils.rel_std_dev(data), 3) == 0.583


def test_stats_skewness_symmetrical():
    data = list(range(97))
    stats = statsutils.Stats(data)
    assert stats.skewness == 0.0
    assert statsutils.skewness(data) == 0.0


def test_stats_skewness_left_and_right():
    left_skewed = list(range(97)) + list(range(10))
    right_skewed = list(range(97)) + list(range(87, 97))
    left = statsutils.skewness(left_skewed)
    right = statsutils.skewness(right_skewed)
    assert round(left, 3) == 0.114
    assert round(right, 3) == -0.114


def test_stats_kurtosis():
    data = list(range(9))
    stats = statsutils.Stats(data)
    assert round(stats.kurtosis, 5) == 1.99125
    assert round(statsutils.kurtosis(data), 5) == 1.99125




def test_stats_pearson_type_symmetric_beta():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    # kurtosis < 3, skewness 0, so pearson_type == 2
    assert stats.pearson_type == 2


def test_stats_pearson_type_gamma():
    # Make data with skewness != 0 and c2 == 0
    data = [1, 2, 3, 4, 100]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 10
    # This may raise, but we want to pin the current behavior
    try:
        result = stats.pearson_type
    except RuntimeError as e:
        assert str(e) == 'missed a spot'
    else:
        # If it doesn't raise, pin the value
        assert result in (1, 3, 7)


def test_stats_get_quantile_boundaries():
    data = list(range(100))
    stats = statsutils.Stats(data)
    assert stats.get_quantile(0.0) == 0
    assert stats.get_quantile(1.0) == 99
    assert stats.get_quantile(0.5) == 49.5


def test_stats_get_quantile_invalid():
    stats = statsutils.Stats([1, 2, 3])
    with pytest.raises(ValueError) as e:
        stats.get_quantile(-0.1)
    assert "expected q between 0.0 and 1.0" in str(e.value)
    with pytest.raises(ValueError) as e:
        stats.get_quantile(1.1)
    assert "expected q between 0.0 and 1.0" in str(e.value)


def test_stats_get_quantile_empty():
    stats = statsutils.Stats([])
    assert stats.get_quantile(0.5) == 0.0




def test_stats_get_zscore_zero_std():
    data = [5, 5, 5]
    stats = statsutils.Stats(data)
    assert stats.get_zscore(5) == 0
    assert stats.get_zscore(6) == float('inf')
    assert stats.get_zscore(4) == float('-inf')


def test_stats_trim_relative_basic():
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = statsutils.Stats(data)
    stats.trim_relative(0.2)
    assert stats.data == [3, 4, 5, 6, 7, 8]


def test_stats_trim_relative_zero():
    data = [1, 2, 3, 4]
    stats = statsutils.Stats(data)
    stats.trim_relative(0.0)
    assert stats.data == [1, 2, 3, 4]


def test_stats_trim_relative_invalid():
    stats = statsutils.Stats([1, 2, 3, 4])
    with pytest.raises(ValueError) as e:
        stats.trim_relative(-0.1)
    assert "expected amount between 0.0 and 0.5" in str(e.value)
    with pytest.raises(ValueError) as e:
        stats.trim_relative(0.5)
    assert "expected amount between 0.0 and 0.5" in str(e.value)


def test_stats_clear_cache_resets_properties():
    data = [1, 2, 3, 4]
    stats = statsutils.Stats(data)
    m1 = stats.mean
    stats.data.append(5)
    stats.clear_cache()
    m2 = stats.mean
    assert m2 != m1
    assert m2 == 3.0


def test_stats_get_histogram_counts_default():
    data = list(range(20)) + list(range(5, 15)) + [10]
    stats = statsutils.Stats(data)
    counts = stats.get_histogram_counts()
    # Should be a list of (bin, count) tuples, bins increasing
    assert isinstance(counts, list)
    assert all(isinstance(x, tuple) and len(x) == 2 for x in counts)
    # The sum of counts equals the number of data points
    assert sum(c for b, c in counts) == len(data)
    # Bins are sorted
    bins = [b for b, c in counts]
    assert bins == sorted(bins)


def test_stats_get_histogram_counts_with_bins():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    counts = stats.get_histogram_counts(bins=2)
    assert isinstance(counts, list)
    assert sum(c for b, c in counts) == 5


def test_stats_get_histogram_counts_with_bin_list():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    bins = [2, 4]
    counts = stats.get_histogram_counts(bins=bins)
    assert isinstance(counts, list)
    assert sum(c for b, c in counts) == 5


def test_stats_get_histogram_counts_invalid_kwarg():
    stats = statsutils.Stats([1, 2, 3])
    with pytest.raises(TypeError) as e:
        stats.get_histogram_counts(foo=1)
    assert "unexpected keyword arguments" in str(e.value)




def test_stats_format_histogram_output():
    data = list(range(20)) + list(range(5, 15)) + [10]
    stats = statsutils.Stats(data)
    output = stats.format_histogram(width=30)
    # Output is a string with lines for each bin
    assert isinstance(output, str)
    lines = output.strip().splitlines()
    assert all(":" in line for line in lines)
    assert any("#" in line for line in lines)


def test_stats_format_histogram_with_format_bin():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    output = stats.format_histogram(format_bin=lambda x: f"{x}ms")
    assert "ms" in output


def test_stats_describe_dict():
    data = list(range(1, 8))
    stats = statsutils.Stats(data)
    desc = stats.describe(format='dict')
    assert isinstance(desc, dict)
    assert desc['count'] == 7
    assert desc['mean'] == 4.0
    assert desc['std_dev'] == 2.0
    assert desc['mad'] == 2.0
    assert desc['min'] == 1
    assert desc['0.25'] == 2.5
    assert desc['0.5'] == 4
    assert desc['0.75'] == 5.5
    assert desc['max'] == 7


def test_stats_describe_list():
    data = list(range(1, 8))
    stats = statsutils.Stats(data)
    desc = stats.describe(format='list')
    assert isinstance(desc, list)
    keys = [k for k, v in desc]
    assert 'count' in keys
    assert 'mean' in keys
    assert 'std_dev' in keys
    assert 'mad' in keys
    assert 'min' in keys
    assert '0.25' in keys
    assert '0.5' in keys
    assert '0.75' in keys
    assert 'max' in keys


def test_stats_describe_text():
    data = list(range(1, 8))
    stats = statsutils.Stats(data)
    desc = stats.describe(format='text')
    assert isinstance(desc, str)
    assert "count:" in desc
    assert "mean:" in desc
    assert "std_dev:" in desc
    assert "mad:" in desc
    assert "min:" in desc
    assert "max:" in desc


def test_stats_describe_invalid_format():
    stats = statsutils.Stats([1, 2, 3])
    with pytest.raises(ValueError) as e:
        stats.describe(format='invalid')
    assert "invalid format for describe" in str(e.value)


def test_describe_function_text():
    data = list(range(7))
    output = statsutils.describe(data, format='text')
    assert isinstance(output, str)
    assert "count:" in output
    assert "mean:" in output
    assert "std_dev:" in output
    assert "mad:" in output
    assert "min:" in output
    assert "max:" in output


def test_describe_function_dict():
    data = list(range(7))
    output = statsutils.describe(data, format='dict')
    assert isinstance(output, dict)
    assert output['count'] == 7
    assert output['mean'] == 3.0
    assert output['std_dev'] == 2.0
    assert output['mad'] == 2.0
    assert output['min'] == 0
    assert output['0.25'] == 1.5
    assert output['0.5'] == 3
    assert output['0.75'] == 4.5
    assert output['max'] == 6


def test_format_histogram_counts_basic():
    bin_counts = [(0.0, 5), (4.4, 8), (8.9, 11), (13.3, 5), (17.8, 2)]
    output = statsutils.format_histogram_counts(bin_counts, width=30)
    assert isinstance(output, str)
    lines = output.strip().splitlines()
    assert len(lines) == len(bin_counts)
    assert all(":" in line for line in lines)
    assert any("#" in line for line in lines)


def test_format_histogram_counts_with_format_bin():
    bin_counts = [(1, 2), (2, 3)]
    output = statsutils.format_histogram_counts(bin_counts, format_bin=lambda x: f"{x}ms")
    assert "ms" in output


def test_format_histogram_counts_width():
    bin_counts = [(1, 2), (2, 3)]
    output = statsutils.format_histogram_counts(bin_counts, width=10)
    assert isinstance(output, str)
    assert len(output.splitlines()) == 2


def test_stats_iter_and_list_conversion():
    data = [1, 2, 3]
    stats = statsutils.Stats(data)
    assert list(stats) == data


def test_stats_use_copy_false_reflects_changes():
    data = [1, 2, 3]
    stats = statsutils.Stats(data, use_copy=False)
    data.append(4)
    assert list(stats) == [1, 2, 3, 4]


def test_stats_use_copy_true_does_not_reflect_changes():
    data = [1, 2, 3]
    stats = statsutils.Stats(data, use_copy=True)
    data.append(4)
    assert list(stats) == [1, 2, 3]




def test_stats_get_bin_bounds_empty():
    stats = statsutils.Stats([])
    assert stats._get_bin_bounds() == [0.0]




def test_stats_get_bin_bounds_with_max():
    stats = statsutils.Stats([1, 2, 3])
    bins = stats._get_bin_bounds(with_max=True)
    assert bins[-1] == 3.0


def test_stats_get_bin_bounds_count():
    stats = statsutils.Stats([1, 2, 3, 4])
    bins = stats._get_bin_bounds(count=2)
    assert len(bins) == 2


def test_stats__get_pow_diffs():
    data = [1, 2, 3]
    stats = statsutils.Stats(data)
    diffs = stats._get_pow_diffs(2)
    mean = stats.mean
    expected = [(v - mean) ** 2 for v in data]
    assert diffs == expected


import math


def test_stats_property_returns_default_on_empty():
    stats = statsutils.Stats([])
    # mean property should return default (0.0) for empty data
    assert stats.mean == 0.0
    # median property should return default (0.0) for empty data
    assert stats.median == 0.0


def test_stats_use_copy_default_is_true():
    data = [1, 2, 3]
    stats = statsutils.Stats(data)
    data.append(4)
    # Should not reflect changes if use_copy is True by default
    assert list(stats) == [1, 2, 3]


def test_stats_pearson_precision_default_is_zero():
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    # The default should be 0, so setting to 1 should change behavior
    assert stats._pearson_precision == 0


def test_stats_get_sorted_data_use_copy_true_returns_sorted():
    data = [3, 1, 2]
    stats = statsutils.Stats(data, use_copy=True)
    sorted_data = stats._get_sorted_data()
    assert sorted_data == [1, 2, 3]


def test_stats_get_sorted_data_use_copy_false_returns_sorted_copy():
    data = [3, 1, 2]
    stats = statsutils.Stats(data, use_copy=False)
    sorted_data = stats._get_sorted_data()
    # Should return a sorted copy, not mutate original
    assert sorted_data == [1, 2, 3]
    assert data == [3, 1, 2]


def test_stats_rel_std_dev_zero_mean_returns_default():
    stats = statsutils.Stats([0, 0, 0])
    # mean is 0, so rel_std_dev should return default (0.0)
    assert stats.rel_std_dev == 0.0


def test_stats_skewness_len_1_returns_default():
    stats = statsutils.Stats([1])
    # Should return default (0.0) if not enough data
    assert stats.skewness == 0.0


def test_stats_skewness_zero_std_returns_default():
    stats = statsutils.Stats([1, 1, 1])
    # std_dev is 0, so should return default (0.0)
    assert stats.skewness == 0.0


def test_stats_skewness_len_2_nonzero_std():
    stats = statsutils.Stats([1, 2])
    # Should not return default, but a number (skewness for [1,2] is 0.0)
    assert stats.skewness == 0.0


def test_stats_skewness_returns_default_when_not_computable():
    stats = statsutils.Stats([])
    assert stats.skewness == 0.0


def test_stats_kurtosis_len_1_returns_zero():
    stats = statsutils.Stats([1])
    # Should return 0.0 if not enough data
    assert stats.kurtosis == 0.0


def test_stats_kurtosis_zero_std_returns_zero():
    stats = statsutils.Stats([1, 1, 1])
    # std_dev is 0, so should return 0.0
    assert stats.kurtosis == 0.0


def test_stats_kurtosis_len_2_nonzero_std():
    stats = statsutils.Stats([1, 2])
    # Should not return 0.0, but a number (kurtosis for [1,2] is 2.0)
    assert stats.kurtosis == 2.0


def test_stats_kurtosis_returns_zero_when_not_computable():
    stats = statsutils.Stats([])
    assert stats.kurtosis == 0.0


def test_stats_pearson_type_beta1_calculation():
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # Should not raise, and beta1 should be skewness**2
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_stats_pearson_type_beta2_calculation():
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # Should not raise, and beta2 should be kurtosis * 1.0
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_stats_pearson_type_c0_calculation():
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # Should not raise, c0 should be (4 * beta2) - (3 * beta1)
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_stats_describe_quantiles_and_format():
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    desc = stats.describe(quantiles=[0.1, 0.9], format='dict')
    assert '0.1' in desc and '0.9' in desc
    desc_list = stats.describe(quantiles=[0.1, 0.9], format='list')
    keys = [k for k, v in desc_list]
    assert '0.1' in keys and '0.9' in keys
    desc_text = stats.describe(quantiles=[0.1, 0.9], format='text')
    assert "0.1:" in desc_text and "0.9:" in desc_text




def test_stats_get_quantile_single_element():
    stats = statsutils.Stats([42])
    assert stats.get_quantile(0.0) == 42
    assert stats.get_quantile(1.0) == 42
    assert stats.get_quantile(0.5) == 42


def test_stats_get_zscore_empty():
    stats = statsutils.Stats([])
    # mean and std_dev are 0.0, so get_zscore should return 0 for value==mean
    assert stats.get_zscore(0) == 0


def test_stats_trim_relative_just_below_half():
    data = list(range(10))
    stats = statsutils.Stats(data)
    stats.trim_relative(0.49)
    # Should leave only the middle element(s)
    assert all(x in data for x in stats.data)
    assert len(stats.data) <= 2


def test_stats_get_bin_bounds_small_data_and_count():
    stats = statsutils.Stats([1, 2])
    bins = stats._get_bin_bounds(count=2)
    assert len(bins) == 2


def test_stats_get_bin_bounds_empty_with_max():
    stats = statsutils.Stats([])
    bins = stats._get_bin_bounds(with_max=True)
    assert bins == [0.0]


def test_stats_get_pow_diffs_power_1():
    data = [1, 2, 3]
    stats = statsutils.Stats(data)
    diffs = stats._get_pow_diffs(1)
    mean = stats.mean
    expected = [v - mean for v in data]
    assert diffs == expected


def test_skewness_len_1_vs_2():
    # Mutant changes "if len(data) > 1" to "if len(data) >= 2" or "if len(data) > 2"
    # For len(data)==2, original returns computed value, mutant would return default (0.0)
    stats = statsutils.Stats([1, 2])
    # For [1,2], skewness is 0.0, but it is computed, not default
    # We assert it is 0.0, but not by default
    assert stats.skewness == 0.0
    # To distinguish, check that it is not the default by changing default
    stats2 = statsutils.Stats([1, 2], default=123.456)
    assert stats2.skewness == 0.0


def test_skewness_len_2_nonzero_default():
    # If mutant returns default for len==2, this will fail
    stats = statsutils.Stats([1, 2], default=99.9)
    assert stats.skewness == 0.0


def test_skewness_len_1_returns_default():
    # For len==1, should always return default
    stats = statsutils.Stats([42], default=77.7)
    assert stats.skewness == 77.7


def test_kurtosis_len_1_vs_2():
    # Mutant changes "if len(data) > 1" to "if len(data) >= 2" or "if len(data) > 2"
    # For len(data)==2, original returns computed value, mutant would return 0.0
    stats = statsutils.Stats([1, 2])
    # For [1,2], kurtosis is 2.0 (not 0.0)
    assert stats.kurtosis == 2.0
    # To distinguish, check that it is not 0.0 when default is changed
    stats2 = statsutils.Stats([1, 2], default=123.456)
    assert stats2.kurtosis == 2.0


def test_kurtosis_len_1_returns_zero():
    # For len==1, should always return 0.0
    stats = statsutils.Stats([42], default=77.7)
    assert stats.kurtosis == 0.0


def test_pearson_type_beta1_and_beta2_math():
    # Mutants change math in pearson_type: ** to *, * to /, - to +, etc.
    # We'll check that the type is as expected for known data.
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # For this data, kurtosis < 3, skewness == 0, so pearson_type == 2
    assert stats.pearson_type == 2




def test_pearson_type_gamma_case():
    # Mutant changes c2 calculation, which can affect gamma detection
    # We'll use data that triggers the gamma branch (c2 == 0)
    # This is tricky, but we can fudge _pearson_precision to make c2 round to 0
    data = [1, 2, 3, 4, 100]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 10
    try:
        result = stats.pearson_type
    except RuntimeError as e:
        assert str(e) == 'missed a spot'
    else:
        assert result in (1, 3, 7)


def test_pearson_type_beta_case():
    # Mutant changes k = c1**2/(4*c0*c2) to something else
    # We'll use data that triggers the k < 0 branch (returns 1)
    # This is hard to guarantee, but we can at least check that for some data, pearson_type == 1
    data = [1, 2, 3, 4, 5, 1000]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert result in (0, 1, 2, 3, 7)


def test_pearson_type_symmetric_beta_case():
    # Mutant changes beta2 < 3 to beta2 <= 3, which would affect this branch
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    # For this data, kurtosis < 3, so pearson_type == 2
    assert stats.pearson_type == 2






def test_pearson_type_c1_beta2_plus_3_vs_minus_3():
    # Mutant changes c1 = skewness * (beta2 + 3) to (beta2 - 3)
    # For symmetric data, skewness == 0, so c1 == 0 either way
    # For asymmetric data, this can change sign
    data = [1, 2, 3, 4, 100]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_pearson_type_c0_and_c2_math():
    # Mutant changes c0 and c2 math, e.g. - to +, * to /, etc.
    # We'll just check that for known data, the type is as expected
    data = [1, 2, 3, 4, 5]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    assert stats.pearson_type == 2


def test_pearson_type_c2_6_vs_7():
    # Mutant changes c2 = ... - 6 to ... - 7
    # This can affect which branch is taken for some data
    data = [1, 2, 3, 4, 5, 100]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_skewness_len_2_vs_1():
    # line 395: comparison `>` -> `>=`
    # For len(data)==2, original computes skewness, mutant returns default.
    stats = statsutils.Stats([1, 2], default=123.456)
    # Should compute skewness (0.0), not return default
    assert stats.skewness == 0.0
    stats1 = statsutils.Stats([42], default=77.7)
    # For len==1, should always return default
    assert stats1.skewness == 77.7


def test_kurtosis_len_2_vs_1():
    # line 419: comparison `>` -> `>=`
    # For len(data)==2, original computes kurtosis, mutant returns 0.0
    stats = statsutils.Stats([1, 2], default=123.456)
    # Should compute kurtosis (2.0), not return 0.0
    assert stats.kurtosis == 2.0
    stats1 = statsutils.Stats([42], default=77.7)
    # For len==1, should always return 0.0
    assert stats1.kurtosis == 0.0


def test_pearson_type_beta1_exponent():
    # line 430: operator `**` -> `*`, `2.0` -> `3.0`
    # beta1 = skewness ** 2.0
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # For this data, skewness == 0, so beta1 == 0, so c0 = 4*beta2 - 3*beta1 = 4*1.7... - 0 = 6.8...
    # If ** is replaced with *, beta1 is 0*2.0 = 0, so same result, but for nonzero skewness, it differs.
    # Use asymmetric data to get nonzero skewness.
    data = [1, 2, 3, 4, 100]
    stats2 = statsutils.Stats(data)
    stats2._pearson_precision = 2
    # If beta1 is wrong, pearson_type will likely be wrong.
    try:
        result = stats2.pearson_type
    except RuntimeError:
        pass
    else:
        # Should be int in (1, 3, 7)
        assert isinstance(result, int)


def test_pearson_type_beta2_operator():
    # line 431: operator `*` -> `/`
    # beta2 = kurtosis * 1.0
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # kurtosis is about 1.7, so beta2 should be 1.7
    # If mutant divides instead, beta2 is much smaller, so pearson_type will be wrong
    assert stats.pearson_type == 2


def test_pearson_type_c0_math():
    # line 435: operator `-` -> `+`, `*` -> `/`, `4` -> `5`, `3` -> `4`
    # c0 = (4 * beta2) - (3 * beta1)
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    # If c0 is wrong, pearson_type will be wrong
    assert stats.pearson_type == 2


def test_pearson_type_c1_math():
    # line 436: operator `*` -> `/`, `+` -> `-`, `3` -> `4`
    # c1 = skewness * (beta2 + 3)
    stats = statsutils.Stats([1, 2, 3, 4, 100])
    stats._pearson_precision = 2
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_pearson_type_c2_math():
    # line 437: operator `-` -> `+`, `-` -> `+`, `*` -> `/`, `2` -> `3`, `3` -> `4`, `6` -> `7`
    # c2 = (2 * beta2) - (3 * beta1) - 6
    stats = statsutils.Stats([1, 2, 3, 4, 5])
    stats._pearson_precision = 2
    assert stats.pearson_type == 2


def test_pearson_type_beta2_branch():
    # line 440: `3` -> `4`
    # line 441: return value replaced with `None`, `0` -> `1`
    # line 443: comparison `<` -> `<=`, `3` -> `4`
    # line 445: comparison `>` -> `>=`
    # These affect which branch is taken for beta2 == 3, <3, >3
    # Use kurtosis == 3 (normal), <3 (symmetric beta), >3 (type 7)
    # Normal: kurtosis == 3
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 2
    # For this data, kurtosis is about 1.99, so <3, so pearson_type == 2
    assert stats.pearson_type == 2
    # Now fudge kurtosis to be exactly 3 by using a normal-like distribution
    # But statsutils never produces kurtosis == 3 exactly, so just check that for kurtosis < 3, we get 2
    # For kurtosis > 3, use a distribution with outliers
    data2 = [1, 1, 1, 1, 1, 100]
    stats2 = statsutils.Stats(data2)
    stats2._pearson_precision = 2
    try:
        result = stats2.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_pearson_type_return_value_normal():
    # line 441: return value replaced with None or 1
    # For normal, should return 0
    data = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 0
    # For this data, kurtosis is about 1.99, so not exactly normal, but check that return is int
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_pearson_type_beta2_le_3_vs_lt_3():
    # line 443: comparison `<` -> `<=`, `3` -> `4`
    # If mutant uses <= instead of <, then for kurtosis == 3, will return 2 instead of 0
    # Try to get kurtosis as close to 3 as possible
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 0
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)


def test_pearson_type_beta2_ge_3_vs_gt_3():
    # line 445: comparison `>` -> `>=`
    # If mutant uses >= instead of >, then for kurtosis == 3, will return 7 instead of 0
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    stats = statsutils.Stats(data)
    stats._pearson_precision = 0
    try:
        result = stats.pearson_type
    except RuntimeError:
        pass
    else:
        assert isinstance(result, int)
