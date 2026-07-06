import math
from starter import rolling_zscore 

def almost_equal(a, b, tol=1e-6):
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < tol



def test_constant_sequence_zero_variance():
    result = rolling_zscore([5,5,5,5], 3)
    assert result == [0.0, 0.0, 0.0, 0.0]



def test_negative_values():
    result = rolling_zscore([-3, -2, -1], 2)
    assert len(result) == 3
    assert almost_equal(result[0], 0.0)
    assert almost_equal(result[1], 1.0)
    assert almost_equal(result[2], 1.0)



def test_nan_current_value_returns_nan():
    result = rolling_zscore([1, 2, float("nan"), 4], 2)
    assert math.isnan(result[2])



def test_nan_ignored_in_window ():
    result = rolling_zscore([1, float("nan"), 3], 3)
    
    assert math.isnan(result[1])
    assert almost_equal(result[1], 1.0)



def test_all_nan_input():
    result = rolling_zscore([float("nan"), float("nan")], 2)

    assert math.isnan(result[0])
    assert math.isnan(result[1])



def test_window_larger_input(): 
    result = rolling_zscore([2,4], 10)

    assert len(result) == 2
    assert almost_equal(result[0], 0.0)
    assert almost_equal(result[1], 1.0)



def test_uses_rolling_window_not_full_history():
    result = rolling_zscore([1, 2, 100, 101], 2)

    # At index 3, the rolling window should be [100, 101].
    # mean = 100.5, std = 0.5, z = 1.0
    assert almost_equal(result[3], 1.0)



def test_population_std_not_sample_std():
    result = rolling_zscore([1, 2], 2)

    # Population std for [1, 2] is 0.5, so z for 2 is 1.0.
    # Sample std would be about 0.707, giving about 0.707 instead.
    assert almost_equal(result[1], 1.0)
