import sys
N = int(input())
P = list(map(int, input().split()))
R = [0] * (N + 1)
for i in range(N):
    for k in range(i + 1, 0, -1):
        R[k] = max(R[k], 0.9 * R[k - 1] + P[i])
div = 1
for k in range(1, N + 1):
    R[k] /= div
    div = div * 0.9 + 1
    R[k] -= 1200 / k ** 0.5
print(max(R[1:]))
print(*R[1:], file=sys.stderr)
