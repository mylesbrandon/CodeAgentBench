You are completing a Python programming task.

Your job is to implement the function described in the specification by replacing the incomplete code in starter.py.

You may use the public tests to understand the expected behavior. Your solution will also be evaluated using additional hidden tests that follow the written specification.

Requirements:

Follow the specification exactly.
Preserve the given function name and signature.
Do not modify the tests.
Do not add external dependencies.
Return only the complete contents of the finished starter.py file.
Do not include explanations.
Do not include Markdown code fences.
Do not mention the hidden tests.
Specification

# Task 001: Rolling Z-Score

Implement `rolling_zscore(values, window)`.

The function takes a list of numbers and a positive integer `window`.

For each index `i`, compute the z-score of `values[i]` relative to the rolling window ending at `i`:

```python
values[max(0, i - window + 1): i + 1]

Starter Code

import math

def rolling_zscore(values, window):
    """
    Compute rolling z-scores for a list of numeric values.

    Args:
        values: list of numbers, possibly including float("nan")
        window: positive integer window size

    Returns:
        list of floats

    Rules:
        - Raise ValueError if window <= 0.
        - For each index i, use values[max(0, i - window + 1): i + 1].
        - Ignore NaN values when computing the window mean and standard deviation.
        - If the current value is NaN, return NaN for that position.
        - If there are no valid non-NaN values in the window, return NaN for that position.
        - Use population standard deviation, dividing variance by n, not n - 1.
        - If the window standard deviation is 0, return 0.0 for that position.
    """
    pass

Public Tests

import math
from starter import rolling_zscore
import pytest

def test_invalid_window():
    with pytest.raises(ValueError):
        rolling_zscore([1, 2, 3], 0)

def almost_equal(a, b, tol=1e-6):
    if math.isnan(a) and math.isnan(b):
        return True
    return abs(a - b) < tol

def test_basic_increasing_sequence():
    result = rolling_zscore([1, 2, 3], 2)
    assert len(result) == 3
    assert almost_equal(result[0], 0.0)
    assert almost_equal(result[1], 1.0)
    assert almost_equal(result[2], 1.0)

def test_window_size_three():
    result = rolling_zscore([1, 2, 3, 4], 3)

    assert len(result) == 4
    assert almost_equal(result[0], 0.0)

def test_invalid_window():
    with pytest.raises(ValueError):
        rolling_zscore([1, 2, 3], 0)