import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from collections import deque
INF = 10 ** 9

def min_edges_to_ensure_distance(N, edges, L):
    """
    Returns the minimum number of edges that have to be set to weight 1
    so that every path from 1 to N uses at least L edges of weight 1.
    If it is impossible (i.e., L is larger than the length of any path),
    returns INF.
    The graph constructed is a layered graph with L layers (0 .. L-1).
    For each original edge we add:
        - a "free" edge staying in the same layer, capacity 1 (can be cut)
        - a "paid" edge moving to the next layer, capacity INF (always usable)
    The source is (1,0), the sink collects all (N, d) for d = 0..L-1.
    The min s-t cut value in this graph equals the minimum number of original
    edges that must be turned into weight 1 to guarantee distance >= L.
    """
    total_nodes = N * L + 1
    sink = total_nodes - 1
    g = [[] for _ in range(total_nodes)]

    def add_edge(fr, to, cap):
        g[fr].append([to, cap, len(g[to])])
        g[to].append([fr, 0, len(g[fr]) - 1])
    for a, b in edges:
        a -= 1
        b -= 1
        for layer in range(L):
            u = a * L + layer
            v_same = b * L + layer
            add_edge(u, v_same, 1)
            if layer + 1 < L:
                v_next = b * L + layer + 1
                add_edge(u, v_next, INF)
    t = N - 1
    for layer in range(L):
        add_edge(t * L + layer, sink, INF)
    level = [0] * total_nodes
    it = [0] * total_nodes

    def bfs():
        for i in range(total_nodes):
            level[i] = -1
        q = deque()
        q.append(0)
        level[0] = 0
        while q:
            v = q.popleft()
            for to, cap, rev in g[v]:
                if cap and level[to] < 0:
                    level[to] = level[v] + 1
                    q.append(to)
        return level[sink] >= 0

    def dfs(v, f):
        if v == sink:
            return f
        for i in range(it[v], len(g[v])):
            it[v] = i
            to, cap, rev = g[v][i]
            if cap and level[v] < level[to]:
                d = dfs(to, min(f, cap))
                if d:
                    g[v][i][1] -= d
                    g[to][rev][1] += d
                    return d
        return 0
    flow = 0
    while bfs():
        it = [0] * total_nodes
        while True:
            f = dfs(0, INF)
            if not f:
                break
            flow += f
            if flow > INF:
                return INF
    return flow

def solve():
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    M = int(next(it))
    K = int(next(it))
    edges = [(int(next(it)), int(next(it))) for _ in range(M)]
    g_unweighted = [[] for _ in range(N)]
    for a, b in edges:
        g_unweighted[a - 1].append(b - 1)
    dist = [INF] * N
    q = deque([0])
    dist[0] = 0
    while q:
        v = q.popleft()
        for to in g_unweighted[v]:
            _lcb_count[0] += 1
            if dist[to] == INF:
                dist[to] = dist[v] + 1
                q.append(to)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dist': dist, 'g_unweighted': g_unweighted, 'list(q)': list(q), 'to': to, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    max_possible = dist[N - 1] if dist[N - 1] != INF else 0
    max_possible = min(max_possible, K)
    lo, hi = (0, max_possible)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        needed = min_edges_to_ensure_distance(N, edges, mid)
        if needed <= K:
            lo = mid
        else:
            hi = mid - 1
    print(lo)
if __name__ == '__main__':
    solve()
