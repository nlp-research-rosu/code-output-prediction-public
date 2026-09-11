import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def solve(N, P, Q):
    grid = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            if grid[P[i] - 1][j] is None:
                grid[P[i] - 1][j] = 0
        for j in range(N):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'N': N, 'P': P, 'Q': Q, 'grid': grid, 'i': i, 'j': j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if grid[j][Q[N - 1 - i] - 1] is None:
                grid[j][Q[N - 1 - i] - 1] = 1
    for row in grid:
        print(''.join(map(str, row)))
N = int(input())
P = list(map(int, input().split()))
Q = list(map(int, input().split()))
solve(N, P, Q)
