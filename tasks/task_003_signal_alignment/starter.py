def strategy_returns(prices, signals, transaction_cost=0.0):
    """
    Calculate strategy returns from prices and desired positions.

    This implementation contains alignment and transaction-cost bugs
    that must be repaired.
    """
    if len(prices) != len(signals):
        raise ValueError("prices and signals must have equal length")

    if transaction_cost < 0:
        raise ValueError("transaction_cost cannot be negative")

    if not prices:
        return []

    results = [0.0]

    for i in range(1, len(prices)):
        asset_return = prices[i] / prices[i - 1] - 1

        # Bug: the current signal was not known before this return.
        strategy_return = signals[i] * asset_return

        # Bug: this charges at the wrong time and ignores turnover size.
        if signals[i] != signals[i - 1]:
            strategy_return -= transaction_cost

        results.append(strategy_return)

    return results
