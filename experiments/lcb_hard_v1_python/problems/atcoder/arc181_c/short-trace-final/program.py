import sys

def solve(N, P, Q):
    grid = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if grid[P[i] - 1][j] is None:
                grid[P[i] - 1][j] = 0
        for j in range(N):
            if grid[j][Q[N - 1 - i] - 1] is None:
                grid[j][Q[N - 1 - i] - 1] = 1
    for row in grid:
        print(''.join(map(str, row)))
N = int(input())
P = list(map(int, input().split()))
Q = list(map(int, input().split()))
solve(N, P, Q)
