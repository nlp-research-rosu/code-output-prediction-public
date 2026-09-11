import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import heapq

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    A = [0] * N
    B = [0] * N
    X = [0] * N
    index = 1
    for i in range(N - 1):
        A[i] = int(data[index])
        B[i] = int(data[index + 1])
        X[i] = int(data[index + 2])
        index += 3
    INF = float('inf')
    dist = [INF] * (N + 1)
    dist[1] = 0
    heap = [(0, 1)]
    while heap:
        _lcb_count[0] += 1
        time, u = heapq.heappop(heap)
        if u == N:
            break
        if time > dist[u]:
            continue
        if u + 1 <= N:
            if dist[u] + A[u - 1] < dist[u + 1]:
                dist[u + 1] = dist[u] + A[u - 1]
                heapq.heappush(heap, (dist[u + 1], u + 1))
        if X[u - 1] <= N:
            if dist[u] + B[u - 1] < dist[X[u - 1]]:
                dist[X[u - 1]] = dist[u] + B[u - 1]
                heapq.heappush(heap, (dist[X[u - 1]], X[u - 1]))
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'heap': heap, 'time': time, 'u': u}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(dist[N])
if __name__ == '__main__':
    main()
