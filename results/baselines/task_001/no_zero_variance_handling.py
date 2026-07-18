import math


def rolling_zscore(values, window):
    if window <= 0:
        raise ValueError("window must be positive")

    results = []

    for index, current in enumerate(values):
        if math.isnan(current):
            results.append(float("nan"))
            continue

        start = max(0, index - window + 1)
        valid = [
            value
            for value in values[start : index + 1]
            if not math.isnan(value)
        ]

        # A singleton window is needed for the public first-position case.
        if len(valid) == 1:
            results.append(0.0)
            continue

        mean = sum(valid) / len(valid)
        variance = sum(
            (value - mean) ** 2 for value in valid
        ) / len(valid)
        standard_deviation = math.sqrt(variance)

        # Deliberate bug: a zero-variance multi-value window divides by zero.
        results.append(
            (current - mean) / standard_deviation
        )

    return results
