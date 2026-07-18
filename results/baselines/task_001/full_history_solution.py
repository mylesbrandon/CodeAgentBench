import math


def rolling_zscore(values, window):
    if window <= 0:
        raise ValueError("window must be positive")

    results = []

    for index, current in enumerate(values):
        if math.isnan(current):
            results.append(float("nan"))
            continue

        # Deliberate bug: uses all prior values, ignoring window.
        history = values[: index + 1]
        valid = [value for value in history if not math.isnan(value)]

        mean = sum(valid) / len(valid)
        variance = sum(
            (value - mean) ** 2 for value in valid
        ) / len(valid)
        standard_deviation = math.sqrt(variance)

        if standard_deviation == 0:
            results.append(0.0)
        else:
            results.append(
                (current - mean) / standard_deviation
            )

    return results