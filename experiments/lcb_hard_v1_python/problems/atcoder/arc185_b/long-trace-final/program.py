import sys
T = int(input())
for _ in range(T):
    N = int(input())
    A = list(map(int, input().split()))
    n = 2
    accum = A[-1]
    for i in range(N - 2, 0, -1):
        d = A[i] - A[i + 1]
        if d > 0:
            A[i] -= d
            A[i - 1] += d
            accum += A[i]
        else:
            accum += A[i]
            A[i] = accum // n
        n += 1
    ans = 1
    for i in range(N - 1):
        if A[i] > A[i + 1]:
            ans = 0
            break
    print('Yes' if ans else 'No')
