import sys
import heapq

def main():
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    W = list(map(int, data[idx:idx + N]))
    idx += N
    intervals = []
    for i in range(N):
        L = int(data[idx])
        R = int(data[idx + 1])
        intervals.append((L, R))
        idx += 2
    Q = int(data[idx])
    idx += 1
    queries = []
    for _ in range(Q):
        s = int(data[idx]) - 1
        t = int(data[idx + 1]) - 1
        queries.append((s, t))
        idx += 2
    adj = [[] for _ in range(N)]
    for i in range(N):
        L_i, R_i = intervals[i]
        for j in range(N):
            if i == j:
                continue
            L_j, R_j = intervals[j]
            if L_j > R_i or L_i > R_j:
                adj[i].append(j)
    for s, t in queries:
        if s == t:
            print(0)
            continue
        dist = [-1] * N
        dist[s] = W[s]
        heap = []
        heapq.heappush(heap, (W[s], s))
        while heap:
            current_dist, u = heapq.heappop(heap)
            if u == t:
                print(current_dist)
                break
            if dist[u] != current_dist:
                continue
            for v in adj[u]:
                if dist[v] == -1:
                    dist[v] = current_dist + W[v]
                    heapq.heappush(heap, (dist[v], v))
        else:
            print(-1)
if __name__ == '__main__':
    main()
