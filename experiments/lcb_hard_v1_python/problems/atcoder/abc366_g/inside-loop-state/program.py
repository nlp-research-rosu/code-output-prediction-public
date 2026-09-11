import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
N, M = map(int, input().split())
g = [0 for _ in range(N)]
for _ in range(M):
    u, v = map(int, input().split())
    u -= 1
    v -= 1
    g[u] |= 1 << v
    g[v] |= 1 << u
c = [0] * N
C = 0
for i in range(N):
    k = -1
    for j in range(N):
        if g[j] >> i & 1 == 1 and g[j] >> i << i == g[j]:
            k = j
            break
    if k == -1:
        c[i] = 1 << i
        C |= c[i]
        continue
    g[i], g[k] = (g[k], g[i])
    for j in range(N):
        if i != j and g[j] >> i & 1 == 1:
            g[j] ^= g[i]
for i in range(N):
    if g[i].bit_count() == 1:
        print('No')
        exit()
for i in range(N):
    for j in range(N):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'C': C, 'c': c, 'g': g, 'i': i, 'j': j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if c[j] == 0 and g[i] >> j & 1 == 1:
            c[j] ^= g[i] & C
print('Yes')
print(*c)
