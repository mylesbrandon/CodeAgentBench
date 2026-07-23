def strategy_returns(prices, signals, transaction_cost=0.0):
    if len(prices) != len(signals):
        raise ValueError("prices and signals must have equal length")

    if transaction_cost < 0:
        raise ValueError("transaction_cost cannot be negative")

    if not prices:
        return []

    results = [0.0]

    for i in range(1, len(prices)):
        asset_return = prices[i] / prices[i - 1] - 1

        # Deliberate lookahead bug: uses the current signal.
        strategy_return = signals[i] * asset_return

        # Deliberate cost bugs: wrong timing and flat fee.
        if signals[i] != signals[i - 1]:
            strategy_return -= transaction_cost

        results.append(strategy_return)

    return results
