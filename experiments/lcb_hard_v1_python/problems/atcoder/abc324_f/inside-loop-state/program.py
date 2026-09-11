import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
import heapq

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    M = int(data[1])
    edges = []
    index = 2
    for _ in range(M):
        u = int(data[index])
        v = int(data[index + 1])
        b = int(data[index + 2])
        c = int(data[index + 3])
        edges.append((u, v, b, c))
        index += 4
    low = 0.0
    high = 10 ** 4

    def is_possible(x):
        adj = [[] for _ in range(N + 1)]
        for u, v, b, c in edges:
            adj[u].append((v, b - x * c))
        dist = [-float('inf')] * (N + 1)
        dist[1] = 0
        heap = [(0, 1)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for v, w in adj[u]:
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'adj': adj, 'd': d, 'u': u, 'v': v, 'w': w, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if dist[v] < dist[u] + w:
                    dist[v] = dist[u] + w
                    heapq.heappush(heap, (dist[v], v))
        return dist[N] >= 0
    for _ in range(100):
        mid = (low + high) / 2
        if is_possible(mid):
            low = mid
        else:
            high = mid
    print(f'{low:.15f}')
if __name__ == '__main__':
    main()
