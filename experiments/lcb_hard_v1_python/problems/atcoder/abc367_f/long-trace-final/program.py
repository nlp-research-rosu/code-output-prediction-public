import sys
input = sys.stdin.readline

def add(i: int) -> None:
    global p1
    p1 *= fac[i]
    p1 %= mod

def delete(i: int) -> None:
    global p1
    p1 *= fac_inv[i]
    p1 %= mod

def add2(i: int) -> None:
    global p2
    p2 *= fac[i]
    p2 %= mod

def delete2(i: int) -> None:
    global p2
    p2 *= fac_inv[i]
    p2 %= mod

def calc_facinv(n: int) -> list:
    """逆元テーブルを作成する"""
    fac[0] = 1
    for i in range(1, n + 1):
        fac[i] = fac[i - 1] * i
        fac[i] %= mod
    fac_inv[0] = 1
    for i in range(1, n + 1):
        fac_inv[i] = pow(fac[i], mod - 2, mod)
    return (fac, fac_inv)

def combination(n: int, k: int) -> int:
    """nCkを計算する"""
    if n < 0 or k < 0 or n < k:
        return 0
    return fac[n] * fac_inv[k] * fac_inv[n - k] % mod
mod = 2 ** 31 - 1
fac = [0] * 201010
fac_inv = [0] * 201010
calc_facinv(201000)
con = 2 * (10 ** 5 + 1)
n, q = map(int, input().split())
a = list(map(int, input().split()))
b = list(map(int, input().split()))
block = int(n / q ** 0.5) + 1
queries = [[] for _ in range(int(q ** 0.5) + 1)]
queries2 = [[] for _ in range(int(q ** 0.5) + 1)]
p1 = 1
u = [0] * q
for i in range(q):
    l, r, L, R = map(int, input().split())
    if r - l != R - L:
        u[i] = 1
    elif r - l <= 10:
        w1 = []
        for j in range(l - 1, r):
            w1.append(a[j])
        w2 = []
        for j in range(L - 1, R):
            w2.append(b[j])
        w1.sort()
        w2.sort()
        if w1 != w2:
            u[i] = 1
    l -= 1
    r -= 1
    L -= 1
    R -= 1
    queries[l // block].append((i, l, r))
    queries2[L // block].append((i, L, R))
ans = [0] * q
left, right = (0, 0)
p1 = 1
for ind, query in enumerate(queries):
    for i, l, r in sorted(query, reverse=ind % 2, key=lambda x: x[2]):
        while right <= r:
            add(a[right])
            right += 1
        while l < left:
            left -= 1
            add(a[left])
        while r + 1 < right:
            right -= 1
            delete(a[right])
        while left < l:
            delete(a[left])
            left += 1
        ans[i] = p1
ans2 = [0] * q
left, right = (0, 0)
p2 = 1
for ind, query in enumerate(queries2):
    for i, l, r in sorted(query, reverse=ind % 2, key=lambda x: x[2]):
        while right <= r:
            add2(b[right])
            right += 1
        while l < left:
            left -= 1
            add2(b[left])
        while r + 1 < right:
            right -= 1
            delete2(b[right])
        while left < l:
            delete2(b[left])
            left += 1
        ans2[i] = p2
for i in range(q):
    if ans[i] != ans2[i] or u[i] == 1:
        print('No')
    else:
        print('Yes')
