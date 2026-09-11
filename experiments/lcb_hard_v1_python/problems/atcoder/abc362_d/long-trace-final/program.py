import sys
import heapq

def main():
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    M = int(data[idx])
    idx += 1
    A = list(map(int, data[idx:idx + N]))
    idx += N
    adj = [[] for _ in range(N)]
    for _ in range(M):
        u = int(data[idx]) - 1
        idx += 1
        v = int(data[idx]) - 1
        idx += 1
        b = int(data[idx])
        idx += 1
        adj[u].append((v, b))
        adj[v].append((u, b))
    INF = float('inf')
    dist = [INF] * N
    dist[0] = A[0]
    heap = [(dist[0], 0)]
    while heap:
        current_dist, u = heapq.heappop(heap)
        if current_dist > dist[u]:
            continue
        for v, b in adj[u]:
            new_dist = current_dist + b + A[v]
            if new_dist < dist[v]:
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))
    result = [str(dist[i]) for i in range(1, N)]
    print(' '.join(result))
if __name__ == '__main__':
    main()
