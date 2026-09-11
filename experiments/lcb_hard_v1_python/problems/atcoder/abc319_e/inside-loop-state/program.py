import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
max_d = 840
N, X, Y = map(int, input().split())
P, T = ([], [])
for _ in range(N - 1):
    p, t = map(int, input().split())
    P.append(p)
    T.append(t)
dp = [[0] * max_d for _ in range(N)]
for j in range(max_d):
    dp[0][j] = X
for i in range(N - 1):
    for j in range(max_d):
        _lcb_count[0] += 1
        if _lcb_count[0] > 501:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'j': j, 'now': now}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        now = dp[i][j] + j
        if now % P[i] == 0:
            mod = 0
        else:
            mod = P[i] - now % P[i]
        dp[i + 1][j] = dp[i][j] + mod + T[i]
for j in range(max_d):
    dp[N - 1][j] += Y
Q = int(input())
for qi in range(Q):
    q = int(input())
    div, mod = divmod(q, max_d)
    ans = dp[N - 1][mod] + div * max_d + mod
    print(ans)
