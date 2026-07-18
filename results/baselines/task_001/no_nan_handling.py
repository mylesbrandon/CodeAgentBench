import math


def rolling_zscore(values, window):
    if window <= 0:
        raise ValueError("window must be positive")

    results = []

    for index, current in enumerate(values):
        start = max(0, index - window + 1)
        window_values = values[start : index + 1]

        # Deliberate bug: NaN values are not removed from the window.
        mean = sum(window_values) / len(window_values)
        variance = sum(
            (value - mean) ** 2 for value in window_values
        ) / len(window_values)
        standard_deviation = math.sqrt(variance)

        if standard_deviation == 0:
            results.append(0.0)
        else:
            results.append(
                (current - mean) / standard_deviation
            )

    return results
