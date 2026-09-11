import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
graph = [[] for _ in range(n)]
total = 0
for index in range(1, len(data), 3):
    left, right, cost = (data[index] - 1, data[index + 1] - 1, data[index + 2])
    graph[left].append((right, cost))
    graph[right].append((left, cost))
    total += cost

def farthest(start):
    best = (0, start)
    stack = [(start, -1, 0)]
    while stack:
        node, parent, distance = stack.pop()
        if distance > best[0]:
            best = (distance, node)
        for neighbor, cost in graph[node]:
            _lcb_count[0] += 1
            if neighbor != parent:
                stack.append((neighbor, node, distance + cost))
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'best': best, 'cost': cost, 'distance': distance, 'neighbor': neighbor, 'node': node, 'parent': parent, 'stack': stack}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    return best
_, endpoint = farthest(0)
diameter, _ = farthest(endpoint)
print(2 * total - diameter)
