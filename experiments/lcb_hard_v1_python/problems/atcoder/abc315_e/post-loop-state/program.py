import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.buffer.readline
sys.setrecursionlimit(10 ** 7)

def dfs(v):
    visited[v] = True
    for next_node in graph[v]:
        if not visited[next_node]:
            visited[next_node] = True
            dfs(next_node)
    ans.append(v + 1)
N = int(input())
cp = [list(map(int, input().split())) for _ in range(N)]
graph = [[] for _ in range(N)]
for i in range(N):
    for j in range(1, len(cp[i])):
        _lcb_count[0] += 1
        graph[i].append(cp[i][j] - 1)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'graph': graph, 'j': j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
visited = [False] * N
ans = []
dfs(0)
print(*ans[:-1])
