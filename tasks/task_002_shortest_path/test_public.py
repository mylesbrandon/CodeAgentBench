import pytest

from starter import shortest_path


def test_basic_shortest_path():
    graph = {
        "A": [("B", 4), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 2), ("D", 5)],
        "D": [],
    }

    result = shortest_path(graph, "A", "D")

    assert result == (4, ["A", "C", "B", "D"])


def test_indirect_path_is_cheaper():
    graph = {
        "A": [("B", 5), ("C", 1)],
        "B": [],
        "C": [("B", 1)],
    }

    result = shortest_path(graph, "A", "B")

    assert result == (2, ["A", "C", "B"])


def test_start_equals_target():
    graph = {
        "A": [("B", 1)],
        "B": [],
    }

    assert shortest_path(graph, "A", "A") == (0, ["A"])


def test_missing_start_raises_key_error():
    graph = {"A": []}

    with pytest.raises(KeyError):
        shortest_path(graph, "missing", "A")


def test_missing_target_raises_key_error():
    graph = {"A": []}

    with pytest.raises(KeyError):
        shortest_path(graph, "A", "missing")
