import sys
input = sys.stdin.buffer.readline
N = int(input())
A = list(map(int, input().split()))
d = {}
for i in range(N):
    if A[i] not in d:
        d[A[i]] = []
    d[A[i]].append(i)
ans = 0
for k, v in d.items():
    if len(v) == 1:
        continue
    for i in range(len(v) - 1):
        diff_cnt = v[i + 1] - v[i] - 1
        ans += diff_cnt * (i + 1) * (len(v) - i - 1)
print(ans)
