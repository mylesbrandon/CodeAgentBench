from numbers import Real


def strategy_returns(prices, signals, transaction_cost=0.0):
    if len(prices) != len(signals):
        raise ValueError("prices and signals must have equal length")

    if transaction_cost < 0:
        raise ValueError("transaction_cost cannot be negative")

    if any(
        not isinstance(price, Real) or not (price > 0)
        for price in prices
    ):
        raise ValueError("prices must contain only positive numbers")

    if any(not isinstance(signal, Real) for signal in signals):
        raise ValueError("signals must contain only numeric values")

    if not prices:
        return []

    results = [0.0]

    for t in range(1, len(prices)):
        asset_return = prices[t] / prices[t - 1] - 1

        # Deliberate bug: uses a signal that was not known before the
        # price movement ending at t.
        position = signals[t]
        previous_position = signals[t - 1]
        turnover = abs(position - previous_position)
        cost = transaction_cost * turnover

        results.append(position * asset_return - cost)

    return results
