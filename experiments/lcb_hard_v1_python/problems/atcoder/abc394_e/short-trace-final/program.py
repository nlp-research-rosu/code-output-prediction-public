import sys
import heapq
from collections import defaultdict

def main():
    import sys
    input = sys.stdin.read().split()
    idx = 0
    N = int(input[idx])
    idx += 1
    C = []
    for _ in range(N):
        line = input[idx]
        idx += 1
        C.append(line)
    in_edges = [defaultdict(list) for _ in range(N + 1)]
    out_edges = [defaultdict(list) for _ in range(N + 1)]
    for u in range(1, N + 1):
        for v in range(1, N + 1):
            c = C[u - 1][v - 1]
            if c != '-':
                in_edges[v][c].append(u)
                out_edges[u][c].append(v)
    INF = float('inf')
    dp = [[INF] * (N + 1) for _ in range(N + 1)]
    for i in range(1, N + 1):
        dp[i][i] = 0
    heap = []
    for i in range(1, N + 1):
        heapq.heappush(heap, (0, i, i))
    for u in range(1, N + 1):
        for v in range(1, N + 1):
            if C[u - 1][v - 1] != '-':
                if dp[u][v] > 1:
                    dp[u][v] = 1
                    heapq.heappush(heap, (1, u, v))
    while heap:
        current_cost, a, b = heapq.heappop(heap)
        if current_cost > dp[a][b]:
            continue
        common_chars = set(in_edges[a].keys()) & set(out_edges[b].keys())
        for c in common_chars:
            u_list = in_edges[a][c]
            v_list = out_edges[b][c]
            for u in u_list:
                for v in v_list:
                    new_cost = current_cost + 2
                    if new_cost < dp[u][v]:
                        dp[u][v] = new_cost
                        heapq.heappush(heap, (new_cost, u, v))
    for i in range(1, N + 1):
        row = []
        for j in range(1, N + 1):
            if dp[i][j] == INF:
                row.append('-1')
            else:
                row.append(str(dp[i][j]))
        print(' '.join(row))
if __name__ == '__main__':
    main()
