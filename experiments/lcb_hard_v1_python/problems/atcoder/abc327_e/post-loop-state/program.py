import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
N = int(input())
P = list(map(int, input().split()))
R = [0] * (N + 1)
for i in range(N):
    for k in range(i + 1, 0, -1):
        _lcb_count[0] += 1
        R[k] = max(R[k], 0.9 * R[k - 1] + P[i])
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'R': R, 'i': i, 'k': k}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
div = 1
for k in range(1, N + 1):
    R[k] /= div
    div = div * 0.9 + 1
    R[k] -= 1200 / k ** 0.5
print(max(R[1:]))
print(*R[1:], file=sys.stderr)
