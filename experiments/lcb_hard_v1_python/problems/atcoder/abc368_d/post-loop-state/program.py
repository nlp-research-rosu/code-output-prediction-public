import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from collections import deque, defaultdict
N, K = map(int, input().split())
edges = [tuple(map(int, input().split())) for _ in range(N - 1)]
V = list(map(int, input().split()))
graph = defaultdict(list)
for u, v in edges:
    graph[u].append(v)
    graph[v].append(u)
need = set(V)
l = [0] * (N + 1)
for u in range(1, N + 1):
    l[u] = len(graph[u])
queue = deque()
for i in range(1, N + 1):
    if l[i] == 1 and i not in need:
        queue.append(i)
out = [False] * (N + 1)
while queue:
    node = queue.popleft()
    out[node] = True
    for nxt in graph[node]:
        _lcb_count[0] += 1
        if not out[nxt]:
            l[nxt] -= 1
            if l[nxt] == 1 and nxt not in need:
                queue.append(nxt)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'l': l, 'list(queue)': list(queue), 'node': node, 'nxt': nxt, 'out': out}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
ans = 0
for i in range(1, N + 1):
    if not out[i]:
        ans += 1
print(ans)
