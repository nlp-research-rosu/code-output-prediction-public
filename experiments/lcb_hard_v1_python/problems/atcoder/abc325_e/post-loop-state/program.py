import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import heapq

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    A = int(data[1])
    B = int(data[2])
    C = int(data[3])
    D = []
    index = 4
    for _ in range(N):
        row = list(map(int, data[index:index + N]))
        D.append(row)
        index += N
    INF = float('inf')
    dist = [[INF] * 2 for _ in range(N)]
    dist[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        time, u, state = heapq.heappop(heap)
        if u == N - 1:
            break
        if time > dist[u][state]:
            continue
        if state == 0:
            for v in range(N):
                if u == v:
                    continue
                cost = D[u][v] * A
                if dist[v][0] > time + cost:
                    dist[v][0] = time + cost
                    heapq.heappush(heap, (dist[v][0], v, 0))
            if dist[u][1] > time:
                dist[u][1] = time
                heapq.heappush(heap, (dist[u][1], u, 1))
        else:
            for v in range(N):
                _lcb_count[0] += 1
                if u == v:
                    continue
                cost = D[u][v] * B + C
                if dist[v][1] > time + cost:
                    dist[v][1] = time + cost
                    heapq.heappush(heap, (dist[v][1], v, 1))
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'cost': cost, 'dist': dist, 'heap': heap, 'time': time, 'u': u, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
    print(min(dist[N - 1][0], dist[N - 1][1]))
if __name__ == '__main__':
    main()
