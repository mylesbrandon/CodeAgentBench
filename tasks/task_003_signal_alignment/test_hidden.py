import pytest

from starter import strategy_returns


def test_signal_after_price_jump_cannot_earn_jump_return():
    result = strategy_returns(
        [100, 200, 200],
        [0, 1, 1],
    )

    assert result == pytest.approx([0.0, 0.0, 0.0])


def test_return_uses_previous_signal_when_signals_are_opposite():
    result = strategy_returns([100, 110], [-1, 1])

    assert result == pytest.approx([0.0, -0.10])


def test_transaction_cost_is_charged_when_new_position_is_used():
    result = strategy_returns(
        [100, 100, 100, 100],
        [1, 2, 2, 2],
        transaction_cost=0.01,
    )

    assert result == pytest.approx([0.0, 0.0, -0.01, 0.0])


def test_transaction_cost_scales_with_turnover():
    result = strategy_returns(
        [100, 100, 100],
        [-2, 3, 3],
        transaction_cost=0.01,
    )

    assert result == pytest.approx([0.0, 0.0, -0.05])


def test_zero_position_earns_no_market_return():
    result = strategy_returns(
        [100, 130, 65],
        [0, 0, 0],
    )

    assert result == pytest.approx([0.0, 0.0, 0.0])


def test_negative_position_reverses_return_sign():
    result = strategy_returns(
        [100, 90, 99],
        [-2, -2, -2],
    )

    assert result == pytest.approx([0.0, 0.20, -0.20])


def test_flat_prices_still_incur_position_change_costs():
    result = strategy_returns(
        [100, 100, 100, 100],
        [0, 1, -1, -1],
        transaction_cost=0.02,
    )

    assert result == pytest.approx([0.0, 0.0, -0.02, -0.04])


def test_nonpositive_price_raises_value_error():
    for invalid_price in (0, -1):
        with pytest.raises(ValueError):
            strategy_returns([100, invalid_price], [1, 1])


def test_single_observation_returns_one_zero():
    assert strategy_returns([100], [3]) == [0.0]


def test_nonnumeric_signal_raises_value_error():
    with pytest.raises(ValueError):
        strategy_returns([100, 110], [1, "long"])
