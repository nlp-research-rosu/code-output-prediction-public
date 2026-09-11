"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc358/tasks/abc358_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc358/tasks/abc358_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
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
K = int(input())
C = list(map(int, input().split()))
mod = 998244353
dp = [[0] * 1001 for _ in range(27)]
fac = [0] * 101010
fac_inv = [0] * 101010
calc_facinv(101000)
dp[0][K] = 1
for i in range(26):
    for j in range(K + 1):
        if dp[i][j] == 0:
            continue
        cnt = min(j, C[i])
        for k in range(cnt + 1):
            dp[i + 1][j - k] += dp[i][j] * combination(j, k)
            dp[i + 1][j - k] %= mod
ans = 0
for i in range(K + 1):
    t = combination(K, i)
    ans += dp[26][i] * pow(t, mod - 2, mod)
ans -= 1
ans %= mod
print(ans)
