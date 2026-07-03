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
        - For each index i, use values[max(0, i-window+1):i+1].
        - Ignore NaN values when computing mean/std.
        - If the current value is NaN, return NaN for that position.
        - If standard deviation is 0, return 0.0.
        - Raise ValueError if window <= 0.
    """
    pass