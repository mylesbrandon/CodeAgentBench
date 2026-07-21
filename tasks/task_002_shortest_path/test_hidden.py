import math

from starter import shortest_path


def test_unreachable_target():
    graph = {
        "A": [("B", 1)],
        "B": [],
        "C": [],
    }

    assert shortest_path(graph, "A", "C") == (math.inf, [])


def test_zero_weight_edge():
    graph = {
        "A": [("B", 0), ("C", 5)],
        "B": [("C", 2)],
        "C": [],
    }

    assert shortest_path(graph, "A", "C") == (
        2,
        ["A", "B", "C"],
    )


def test_duplicate_edges_choose_cheapest():
    graph = {
        "A": [("B", 1), ("B", 10)],
        "B": [],
    }

    distance, path = shortest_path(graph, "A", "B")

    assert distance == 1
    assert path == ["A", "B"]


def test_better_path_discovered_later():
    graph = {
        "A": [("B", 10), ("C", 1)],
        "B": [("D", 1)],
        "C": [("B", 1)],
        "D": [],
    }

    assert shortest_path(graph, "A", "D") == (
        3,
        ["A", "C", "B", "D"],
    )


def test_cycle_does_not_break_search():
    graph = {
        "A": [("B", 1)],
        "B": [("C", 1)],
        "C": [("A", 1), ("D", 1)],
        "D": [],
    }

    assert shortest_path(graph, "A", "D") == (
        3,
        ["A", "B", "C", "D"],
    )


def test_node_with_empty_adjacency_list():
    graph = {
        "A": [],
        "B": [],
    }

    assert shortest_path(graph, "A", "B") == (math.inf, [])


def test_graph_is_directed():
    graph = {
        "A": [("B", 2)],
        "B": [],
    }

    assert shortest_path(graph, "B", "A") == (math.inf, [])


def test_input_graph_is_not_mutated():
    graph = {
        "A": [("B", 1)],
        "B": [],
    }

    original = {
        node: list(edges)
        for node, edges in graph.items()
    }

    shortest_path(graph, "A", "B")

    assert graph == original
