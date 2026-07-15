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