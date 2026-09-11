"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc362/tasks/abc362_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc362/tasks/abc362_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.readline

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

def f(s: int, t: int) -> None:
    dp = [0] * (N + 1)
    dp[0] = 1
    for i in range(N):
        num = A[i] - s
        if num % t == 0:
            q = num // t
        else:
            q = -1
        if 0 <= q < N:
            dp[q + 1] += dp[q]
    for i in range(N + 1):
        ans[i] += dp[i]
        ans[i] %= mod
N = int(input())
A = list(map(int, input().split()))
mod = 998244353
fac = [0] * 101010
fac_inv = [0] * 101010
calc_facinv(101000)
s = set()
for i in range(N):
    for j in range(i, N):
        s.add((A[i], A[j] - A[i]))
d = {}
for i in A:
    if i in d:
        d[i] += 1
    else:
        d[i] = 1
ans = [0] * 1000
for i, j in s:
    _lcb_count[0] += 1
    if j == 0:
        for k in range(1, d[i] + 1):
            ans[k] += combination(d[i], k)
            ans[k] %= mod
        continue
    f(i, j)
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'd': d, 'i': i, 'j': j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
ans[1] = N
print(*ans[1:N + 1])
