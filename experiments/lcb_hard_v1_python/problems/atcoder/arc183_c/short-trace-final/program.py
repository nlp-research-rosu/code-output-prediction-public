import sys
input = sys.stdin.readline
n, m = map(int, input().split())
mod = 998244353
limit = []
for i in range(m):
    l, r, x = map(int, input().split())
    limit.append((l, r, x))
limit.sort(key=lambda x: x[1])
comb = [[0] * (i + 1) for i in range(n + 1)]
comb[0][0] = 1
for i in range(1, n + 1):
    for j in range(i + 1):
        if j == 0 or j == i:
            comb[i][j] = 1
        else:
            comb[i][j] = (comb[i - 1][j - 1] + comb[i - 1][j]) % mod
rcd = [-1] * (n + 1)
dp = [[0] * (n + 1) for i in range(n + 1)]
for i in range(1, n + 1):
    dp[i][i - 1] = 1
top = 0
for i in range(1, n + 1):
    while top < m and limit[top][1] == i:
        ls, pos = (limit[top][0], limit[top][2])
        rcd[pos] = max(rcd[pos], ls)
        top += 1
    for j in range(i, 0, -1):
        for k in range(j, i + 1):
            if rcd[k] >= j:
                continue
            val = comb[i - j][k - j]
            if k > j:
                val *= dp[j][k - 1]
            if k < i:
                val *= dp[k + 1][i]
            dp[j][i] += val % mod
        dp[j][i] %= mod
print(dp[1][n])
