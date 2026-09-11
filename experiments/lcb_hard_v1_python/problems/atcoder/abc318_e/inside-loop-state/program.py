import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.buffer.readline
N = int(input())
A = list(map(int, input().split()))
d = {}
for i in range(N):
    if A[i] not in d:
        d[A[i]] = []
    d[A[i]].append(i)
ans = 0
for k, v in d.items():
    if len(v) == 1:
        continue
    for i in range(len(v) - 1):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'diff_cnt': diff_cnt, 'i': i, 'k': k, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        diff_cnt = v[i + 1] - v[i] - 1
        ans += diff_cnt * (i + 1) * (len(v) - i - 1)
print(ans)
