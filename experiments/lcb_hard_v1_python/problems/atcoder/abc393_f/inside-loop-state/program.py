import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import bisect
import sys

def main():
    input = sys.stdin.read().split()
    ptr = 0
    N = int(input[ptr])
    ptr += 1
    Q = int(input[ptr])
    ptr += 1
    A = list(map(int, input[ptr:ptr + N]))
    ptr += N
    queries = []
    for i in range(Q):
        R = int(input[ptr])
        ptr += 1
        X = int(input[ptr])
        ptr += 1
        queries.append((R, X, i))
    queries_by_r = [[] for _ in range(N + 1)]
    for r, x, idx in queries:
        queries_by_r[r].append((x, idx))
    dp = []
    ans = [0] * Q
    for r in range(1, N + 1):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'ans': ans, 'current_val': current_val, 'dp': dp, 'idx': idx, 'r': r}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        current_val = A[r - 1]
        idx = bisect.bisect_left(dp, current_val)
        if idx == len(dp):
            dp.append(current_val)
        else:
            dp[idx] = current_val
        for x, idx in queries_by_r[r]:
            ans[idx] = bisect.bisect_right(dp, x)
    for a in ans:
        print(a)
if __name__ == '__main__':
    main()
