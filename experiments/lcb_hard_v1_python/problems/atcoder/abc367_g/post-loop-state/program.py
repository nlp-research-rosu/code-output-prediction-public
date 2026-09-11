import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
mod = 998244353

def hadamard(a, m):
    for k in range(m):
        i = 1 << k
        for j in range(1 << m):
            if not i & j:
                a[j], a[i | j] = (a[j] + a[i | j], a[j] - a[i | j])
N, M, K = map(int, input().split())
A = list(map(int, input().split()))
L = 20
cnt = [0] * (1 << L)
for i in range(N):
    cnt[A[i]] += 1
F = [[0] * M for i in range(N + 1)]
G = [[0] * M for i in range(N + 1)]
F[0][0] = 1
G[0][0] = 1
for i in range(N):
    for j in range(M):
        F[i + 1][j] = (F[i][j] + F[i][j - 1]) % mod
        G[i + 1][j] = (G[i][j] - G[i][j - 1]) % mod
res = [0] * (N + 1)
for i in range(N + 1):
    for j in range(M):
        res[i] += F[i][j] * G[N - i][-j]
        res[i] %= mod
hadamard(cnt, L)
B = [(cnt[i] + N) // 2 for i in range(1 << L)]
C = [res[B[i]] for i in range(1 << L)]
hadamard(C, L)
inv = pow(1 << L, mod - 2, mod)
ans = 0
for i in range(1 << L):
    _lcb_count[0] += 1
    C[i] = C[i] % mod * inv % mod
    ans += C[i] * pow(i, K, mod)
    ans %= mod
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'C[i]': C[i], 'ans': ans, 'i': i, 'inv': inv}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print(ans)
