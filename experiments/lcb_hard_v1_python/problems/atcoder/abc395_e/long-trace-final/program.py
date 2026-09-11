import sys
import heapq

def main():
    input = sys.stdin.read().split()
    idx = 0
    N = int(input[idx])
    idx += 1
    M = int(input[idx])
    idx += 1
    X = int(input[idx])
    idx += 1
    size = 2 * N + 1
    adj = [[] for _ in range(size)]
    for _ in range(M):
        u = int(input[idx])
        idx += 1
        v = int(input[idx])
        idx += 1
        adj[u].append((v, 1))
        adj[v + N].append((u + N, 1))
    for v in range(1, N + 1):
        adj[v].append((v + N, X))
        adj[v + N].append((v, X))
    INF = float('inf')
    dist = [INF] * (2 * N + 1)
    dist[1] = 0
    heap = []
    heapq.heappush(heap, (0, 1))
    while heap:
        current_dist, u = heapq.heappop(heap)
        if current_dist > dist[u]:
            continue
        for neighbor, cost in adj[u]:
            if dist[neighbor] > dist[u] + cost:
                dist[neighbor] = dist[u] + cost
                heapq.heappush(heap, (dist[neighbor], neighbor))
    print(min(dist[N], dist[N + N]))
if __name__ == '__main__':
    main()
