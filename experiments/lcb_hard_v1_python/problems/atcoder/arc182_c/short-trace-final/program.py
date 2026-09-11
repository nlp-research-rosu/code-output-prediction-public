import sys
n, m = map(int, input().split())
M = 998244353
p = [2, 3, 5, 7, 11, 13]
f = [[0] * len(p) for i in range(m + 1)]
for i in range(1, m + 1):
    v = i
    for j in range(len(p)):
        u = p[j]
        while v % u == 0:
            v //= u
            f[i][j] += 1
L = 2 ** len(p) + 1

def seki(a, b):
    c = [[0] * L for i in range(L)]
    for i in range(L):
        for j in range(L):
            for k in range(L):
                c[i][j] += a[i][k] * b[k][j]
                c[i][j] %= M
    return c
A = [[0] * L for i in range(L)]
for s in range(L - 1):
    for i in range(1, m + 1):
        t = s
        for j in range(L - 1):
            if s & j == 0:
                t = s | j
                g = 1
                for k in range(len(p)):
                    if j >> k & 1:
                        g *= f[i][k]
                A[t][s] += g
                if t == L - 2:
                    A[-1][s] += g
A[-1][-1] = 1
B = [[0] * L for i in range(L)]
for i in range(L):
    B[i][i] = 1
for i in range(61):
    if n >> i & 1:
        B = seki(A, B)
    A = seki(A, A)
print(sum((B[-1][i] for i in range(L - 1))) % M)
