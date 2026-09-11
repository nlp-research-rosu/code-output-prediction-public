import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
graph = [[] for _ in range(n)]
for index in range(1, len(data), 2):
    left, right = (data[index] - 1, data[index + 1] - 1)
    graph[left].append(right)
    graph[right].append(left)
degrees = [len(neighbors) for neighbors in graph]
largest = 0
for center in range(n):
    capacities = sorted((degrees[neighbor] - 1 for neighbor in graph[center]), reverse=True)
    for branch_count, leaves in enumerate(capacities, 1):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'branch_count': branch_count, 'capacities': capacities, 'center': center, 'degrees': degrees, 'largest': largest, 'leaves': leaves}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if leaves == 0:
            break
        largest = max(largest, 1 + branch_count * (leaves + 1))
print(n - largest)
