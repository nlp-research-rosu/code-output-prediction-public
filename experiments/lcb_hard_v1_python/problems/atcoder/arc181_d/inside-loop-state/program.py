import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
n = int(input())
p = [int(t) - 1 for t in input().split()]
ind = [0] * n
for i in range(n):
    ind[p[i]] = i
m = int(input())
a = [int(t) - 1 for t in input().split()] + [n]
mtime = [0] * n
t = 0
j = 0
for i in range(n):
    while a[j] < i:
        t += 1
        j += 1
    mtime[i] = t
fenwick = [0] * (n + 1)

def update(i, x):
    while i <= n:
        fenwick[i] += x
        i += i & -i

def partial(i):
    S = 0
    while i:
        S += fenwick[i]
        i -= i & -i
    return S
diff = [0] * (m + 3)
tot = 0
for x in range(n - 1, -1, -1):
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'diff': diff, 'i': i, 'ind': ind, 'mtime': mtime, 'ops': ops, 'tot': tot, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    i = ind[x]
    ops = partial(i)
    tot += ops
    diff[mtime[i]] += 1
    diff[min(m + 1, mtime[i] + ops)] -= 1
    update(i + 1, 1)
S = 0
for x in range(m):
    S += diff[x]
    tot -= S
    print(tot)
