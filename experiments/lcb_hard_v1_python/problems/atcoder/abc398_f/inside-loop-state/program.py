import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
s = input().strip()
rev_s = s[::-1]
t = rev_s + '#' + s
n = len(t)
pi = [0] * n
for i in range(1, n):
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'n': n, 'pi': pi, 's': s, 't': t}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    j = pi[i - 1]
    while j > 0 and t[i] != t[j]:
        j = pi[j - 1]
    if t[i] == t[j]:
        j += 1
    pi[i] = j
l = pi[-1]
ans = s + s[:len(s) - l][::-1]
print(ans)
