import sys
s = input().strip()
rev_s = s[::-1]
t = rev_s + '#' + s
n = len(t)
pi = [0] * n
for i in range(1, n):
    j = pi[i - 1]
    while j > 0 and t[i] != t[j]:
        j = pi[j - 1]
    if t[i] == t[j]:
        j += 1
    pi[i] = j
l = pi[-1]
ans = s + s[:len(s) - l][::-1]
print(ans)
