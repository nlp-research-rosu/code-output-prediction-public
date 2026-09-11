import heapq
import json


def main():
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    source = data["source"]
    adjacency = [[] for _ in range(n)]
    for left, right, weight in data["edges"]:
        adjacency[left].append((right, weight))
        adjacency[right].append((left, weight))
    infinity = 10**30
    dist = [infinity] * n
    parent = [-1] * n
    dist[source] = 0
    queue = [(0, source)]
    visited = [False] * n
    while queue:
        distance, node = heapq.heappop(queue)
        if visited[node]:
            continue
        visited[node] = True
        for neighbor, weight in adjacency[node]:
            candidate = distance + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                parent[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
    print(json.dumps({'dist': dist, 'parent': parent, 'visited': visited}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
