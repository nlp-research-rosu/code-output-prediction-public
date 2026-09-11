import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.buffer.readline
import math
INF = 10 ** 18
N = int(input())
CheckPoint = []
for i in range(N):
    x, y = map(int, input().split())
    CheckPoint.append((x, y))

def dist(i, j):
    x1, y1 = CheckPoint[i]
    x2, y2 = CheckPoint[j]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
max_c = 20
dp = [[INF] * (max_c + 1) for _ in range(N)]
dp[0][0] = 0
for i in range(1, N):
    for j in range(i - 1, max(-1, i - max_c - 5), -1):
        skip = i - j - 1
        for k in range(max_c - skip):
            _lcb_count[0] += 1
            dp[i][k + skip] = min(dp[i][k + skip], dp[j][k] + dist(j, i))
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'j': j, 'k': k, 'skip': skip}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
ans = INF
for c in range(max_c + 1):
    if dp[N - 1][c] == INF:
        continue
    if c == 0:
        penalty = 0
    else:
        penalty = 2 ** (c - 1)
    ans = min(ans, dp[N - 1][c] + penalty)
print(ans)
