import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = lambda: sys.stdin.readline().rstrip('\r\n')
INF = int(4e+18)

def min2(a: int, b: int) -> int:
    return a if a < b else b
if __name__ == '__main__':
    N = int(input())
    A, B = ([0] * N, [0] * N)
    for i in range(N):
        A[i], B[i] = map(int, input().split())
        A[i] -= 1
    sum_ = sum(B)
    if sum_ % 3 != 0:
        print(-1)
        exit(0)
    target = sum_ // 3
    dp = [[INF] * (target + 1) for _ in range(target + 1)]
    dp[0][0] = 0
    for i in range(N):
        ndp = [[INF] * (target + 1) for _ in range(target + 1)]
        for t in range(3):
            cost = 0 if A[i] == t else 1
            a = B[i] if t == 0 else 0
            b = B[i] if t == 1 else 0
            for j in range(target + 1 - a):
                for k in range(target + 1 - b):
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'b': b, 'cost': cost, 'dp': dp, 'i': i, 'j': j, 'k': k, 'ndp': ndp, 't': t, 'target': target}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    ndp[j + a][k + b] = min2(ndp[j + a][k + b], dp[j][k] + cost)
        dp = ndp
    res = dp[target][target]
    print(res if res < INF else -1)
