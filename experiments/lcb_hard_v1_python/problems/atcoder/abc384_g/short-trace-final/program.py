import sys
n = int(sys.stdin.readline())
a = list(map(int, sys.stdin.readline().split()))
b = list(map(int, sys.stdin.readline().split()))
k = int(sys.stdin.readline())
queries = []
for _ in range(k):
    x, y = map(int, sys.stdin.readline().split())
    queries.append((x, y))
prefix_arrays = []
for bj in b:
    prefix = [0] * n
    current_sum = 0
    for i in range(n):
        current_sum += abs(a[i] - bj)
        prefix[i] = current_sum
    prefix_arrays.append(prefix)
for x, y in queries:
    x -= 1
    y -= 1
    sum_val = 0
    for j in range(y + 1):
        sum_val += prefix_arrays[j][x]
    print(sum_val)
