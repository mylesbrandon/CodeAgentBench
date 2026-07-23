import pytest

from starter import strategy_returns


def test_constant_long_position():
    result = strategy_returns(
        [100, 110, 121],
        [1, 1, 1],
    )

    assert result == pytest.approx([0.0, 0.10, 0.10])


def test_constant_short_position():
    result = strategy_returns([100, 90], [-1, -1])

    assert result == pytest.approx([0.0, 0.10])


def test_unequal_lengths_raise_value_error():
    with pytest.raises(ValueError):
        strategy_returns([100, 110], [1])


def test_negative_transaction_cost_raises_value_error():
    with pytest.raises(ValueError):
        strategy_returns([100], [1], transaction_cost=-0.01)


def test_empty_input_returns_empty_list():
    assert strategy_returns([], []) == []


def test_tuple_inputs_return_matching_length():
    result = strategy_returns((100, 105), (2, 2))

    assert isinstance(result, list)
    assert result == pytest.approx([0.0, 0.10])
