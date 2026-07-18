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
    if window <= 0:
        raise ValueError("window must be positive")

    result = []

    for i, current in enumerate(values):
        if math.isnan(current):
            result.append(float("nan"))
            continue

        start = max(0, i - window + 1)
        valid_values = [
            value for value in values[start:i + 1]
            if not math.isnan(value)
        ]

        if not valid_values:
            result.append(float("nan"))
            continue

        mean = math.fsum(valid_values) / len(valid_values)
        variance = math.fsum(
            (value - mean) ** 2 for value in valid_values
        ) / len(valid_values)
        standard_deviation = math.sqrt(variance)

        if standard_deviation == 0:
            result.append(0.0)
        else:
            result.append(float((current - mean) / standard_deviation))

    return result