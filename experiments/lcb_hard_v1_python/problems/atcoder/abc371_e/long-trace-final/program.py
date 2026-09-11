import sys
n = int(input())
a = list(map(int, input().split()))
last_occurrence = {}
total = 0
for i in range(n):
    num = a[i]
    if num in last_occurrence:
        prev = last_occurrence[num]
    else:
        prev = -1
    total += (i - prev) * (n - i)
    last_occurrence[num] = i
print(total)
