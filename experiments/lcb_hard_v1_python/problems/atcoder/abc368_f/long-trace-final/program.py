import sys
n = int(input())
a = list(map(int, input().split()))
max_val = 100000
g = [0] * (max_val + 1)
for i in range(2, max_val + 1):
    divisors = set()
    for d in range(1, int(i ** 0.5) + 1):
        if i % d == 0:
            if d < i:
                divisors.add(d)
            if i // d != d and i // d < i:
                divisors.add(i // d)
    seen = set()
    for d in divisors:
        seen.add(g[d])
    mex = 0
    while mex in seen:
        mex += 1
    g[i] = mex
xor_sum = 0
for x in a:
    xor_sum ^= g[x]
if xor_sum != 0:
    print('Anna')
else:
    print('Bruno')
