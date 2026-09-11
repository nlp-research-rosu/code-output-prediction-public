import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
sys.setrecursionlimit(int(1000000.0))
input = lambda: sys.stdin.readline().rstrip('\r\n')
MOD = 998244353
INF = int(4e+18)

def max2(a: int, b: int) -> int:
    return a if a > b else b
if __name__ == '__main__':
    N, M, X0 = map(int, input().split())
    A, B, S, T = ([0] * M, [0] * M, [0] * M, [0] * M)
    for i in range(M):
        a, b, s, t = map(int, input().split())
        A[i], B[i], S[i], T[i] = (a - 1, b - 1, s, t)
    events = []
    for i in range(M):
        events.append((S[i], 1, i))
        events.append((T[i], 0, i))
    events.sort()
    res = [0] * M
    res[0] = X0
    latest = [0] * N
    for time, kind, i in events:
        _lcb_count[0] += 1
        if kind == 1:
            if i != 0:
                res[i] = max2(0, latest[A[i]] - S[i])
        else:
            latest[B[i]] = max2(latest[B[i]], T[i] + res[i])
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'kind': kind, 'latest': latest, 'res': res, 'time': time}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(*res[1:])
