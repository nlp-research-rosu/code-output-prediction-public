import sys
k = int(input())
s = input().strip()
t = input().strip()
n = len(s)
m = len(t)
prev = list(range(m + 1))
for i in range(1, n + 1):
    curr = [0] * (m + 1)
    curr[0] = prev[0] + 1
    for j in range(1, m + 1):
        if s[i - 1] == t[j - 1]:
            curr[j] = prev[j - 1]
        else:
            curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + 1)
    prev = curr
edit_distance = prev[m]
print('Yes' if edit_distance <= k else 'No')
