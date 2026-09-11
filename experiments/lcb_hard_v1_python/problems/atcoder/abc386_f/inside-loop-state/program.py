import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
k = int(input())
s = input().strip()
t = input().strip()
n = len(s)
m = len(t)
prev = list(range(m + 1))
for i in range(1, n + 1):
    curr = [0] * (m + 1)
    curr[0] = prev[0] + 1
    for j in range(1, m + 1):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'curr': curr, 'i': i, 'j': j, 'm': m, 'n': n, 'prev': prev, 's': s, 't': t}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if s[i - 1] == t[j - 1]:
            curr[j] = prev[j - 1]
        else:
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + 1)
    prev = curr
edit_distance = prev[m]
print('Yes' if edit_distance <= k else 'No')
