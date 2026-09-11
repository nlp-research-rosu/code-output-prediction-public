import heapq
import json


def main():
    __target_count = 0
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    adjacency = [[] for _ in range(n)]
    indegree = [0] * n
    for left, right in data["edges"]:
        adjacency[left].append(right)
        indegree[right] += 1
    queue = [node for node in range(n) if indegree[node] == 0]
    heapq.heapify(queue)
    order = []
    while queue:
        node = heapq.heappop(queue)
        order.append(node)
        for neighbor in adjacency[node]:
            __target_count += 1
            if __target_count == 202:
                print(json.dumps({'indegree': indegree, 'order': order, 'queue': queue}, separators=(",", ":"), sort_keys=True))
                return
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(queue, neighbor)
    print(json.dumps(order, separators=(",", ":")))


if __name__ == "__main__":
    main()
