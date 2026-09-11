import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
T = int(input())
for _ in range(T):
    N = int(input())
    A = list(map(int, input().split()))
    n = 2
    accum = A[-1]
    for i in range(N - 2, 0, -1):
        d = A[i] - A[i + 1]
        if d > 0:
            A[i] -= d
            A[i - 1] += d
            accum += A[i]
        else:
            accum += A[i]
            A[i] = accum // n
        n += 1
    ans = 1
    for i in range(N - 1):
        _lcb_count[0] += 1
        if A[i] > A[i + 1]:
            ans = 0
            break
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'N': N, 'accum': accum, 'ans': ans, 'i': i, 'n': n}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print('Yes' if ans else 'No')
