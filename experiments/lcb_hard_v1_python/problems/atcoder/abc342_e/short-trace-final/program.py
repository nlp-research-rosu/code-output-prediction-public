import sys
import heapq
from collections import deque

def main():
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    M = int(data[idx])
    idx += 1
    graph = [[] for _ in range(N + 1)]
    for _ in range(M):
        l = int(data[idx])
        d = int(data[idx + 1])
        k = int(data[idx + 2])
        c = int(data[idx + 3])
        A = int(data[idx + 4])
        B = int(data[idx + 5])
        idx += 6
        graph[B].append((A, l, d, k, c))
    latest = [-1] * (N + 1)
    latest[N] = float('inf')
    q = deque()
    q.append(N)
    while q:
        u = q.popleft()
        for v, l, d, k, c in graph[u]:
            max_departure = latest[u] - c
            if max_departure < l:
                continue
            t = l + (k - 1) * d
            if t > max_departure:
                x = (max_departure - l) // d
                if x < 0:
                    continue
                t = l + x * d
            if latest[v] < t:
                latest[v] = t
                q.append(v)
    for i in range(1, N):
        if latest[i] == -1:
            print('Unreachable')
        else:
            print(latest[i])
if __name__ == '__main__':
    main()
