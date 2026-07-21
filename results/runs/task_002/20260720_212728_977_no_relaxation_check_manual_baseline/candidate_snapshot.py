import heapq
import math


def shortest_path(graph, start, target):
    """
    Find the shortest path between two nodes in a directed,
    nonnegatively weighted graph.

    This implementation contains logical bugs that must be repaired.
    """
    distances = {node: math.inf for node in graph}
    distances[start] = 0

    previous = {}
    visited = set()
    queue = [(0, start)]

    while queue:
        current_distance, node = heapq.heappop(queue)

        if node in visited:
            continue

        visited.add(node)

        if node == target:
            break

        for neighbor, weight in graph[node]:
            new_distance = current_distance + weight

            # BUG: This overwrites the best-known distance without
            # checking whether the new route is actually better.
            if neighbor not in visited:
                distances[neighbor] = new_distance
                previous[neighbor] = node
                heapq.heappush(queue, (new_distance, neighbor))

    # BUG: The required unreachable result is (math.inf, []).
    if distances[target] == math.inf:
        return None

    path = [target]

    while path[-1] != start:
        path.append(previous[path[-1]])

    path.reverse()
    return distances[target], path
