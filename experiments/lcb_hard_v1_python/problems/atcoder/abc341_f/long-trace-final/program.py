import sys
import heapq

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    M = int(data[idx])
    idx += 1
    edges = [[] for _ in range(N)]
    for _ in range(M):
        u = int(data[idx]) - 1
        idx += 1
        v = int(data[idx]) - 1
        idx += 1
        edges[u].append(v)
        edges[v].append(u)
    W = list(map(int, data[idx:idx + N]))
    idx += N
    A = list(map(int, data[idx:idx + N]))
    idx += N
    from collections import defaultdict
    adj_weights = [[] for _ in range(N)]
    for x in range(N):
        for y in edges[x]:
            if W[y] < W[x]:
                adj_weights[x].append(W[y])
    max_pieces_per_piece = [0] * N
    for x in range(N):
        capacity = W[x] - 1
        items = adj_weights[x]
        dp = [0] * (capacity + 1)
        for w in items:
            for j in range(capacity, w - 1, -1):
                if dp[j - w] + 1 > dp[j]:
                    dp[j] = dp[j - w] + 1
        max_pieces_per_piece[x] = max(dp)
    vertices = list(range(N))
    vertices.sort(key=lambda x: W[x])
    f = [0] * N
    for x in vertices:
        capacity = W[x] - 1
        items = []
        for y in edges[x]:
            if W[y] < W[x]:
                items.append((W[y], f[y]))
        dp = [0] * (capacity + 1)
        for w, val in items:
            for j in range(capacity, w - 1, -1):
                if dp[j - w] + val > dp[j]:
                    dp[j] = dp[j - w] + val
        f[x] = 1 + max(dp)
    answer = 0
    for x in range(N):
        answer += A[x] * f[x]
    print(answer)
if __name__ == '__main__':
    main()
