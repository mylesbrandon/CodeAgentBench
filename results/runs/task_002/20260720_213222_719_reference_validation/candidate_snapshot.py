import heapq
import math
from itertools import count


def shortest_path(graph, start, target):
    if start not in graph:
        raise KeyError(start)

    if target not in graph:
        raise KeyError(target)

    if start == target:
        return 0, [start]

    distances = {node: math.inf for node in graph}
    distances[start] = 0

    previous = {}

    # The counter prevents heapq from comparing node names when
    # two entries have identical distances.
    tie_breaker = count()
    queue = [(0, next(tie_breaker), start)]

    while queue:
        current_distance, _, node = heapq.heappop(queue)

        # A node can appear in the queue multiple times.
        # Ignore entries that no longer represent its best distance.
        if current_distance > distances[node]:
            continue

        if node == target:
            break

        for neighbor, weight in graph[node]:
            new_distance = current_distance + weight

            # Edge relaxation: update only when this route is better.
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = node

                heapq.heappush(
                    queue,
                    (new_distance, next(tie_breaker), neighbor),
                )

    if math.isinf(distances[target]):
        return math.inf, []

    path = []
    current = target

    while current != start:
        path.append(current)
        current = previous[current]

    path.append(start)
    path.reverse()

    return distances[target], path
