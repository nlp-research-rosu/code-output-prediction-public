import sys
from collections import deque
data = list(map(int, sys.stdin.buffer.read().split()))
n, k = data[:2]
permutation = data[2:]
position = [0] * (n + 1)
for index, value in enumerate(permutation):
    position[value] = index
minimums = deque()
maximums = deque()
answer = n
for value in range(1, n + 1):
    current = position[value]
    while minimums and position[minimums[-1]] >= current:
        minimums.pop()
    while maximums and position[maximums[-1]] <= current:
        maximums.pop()
    minimums.append(value)
    maximums.append(value)
    left = value - k + 1
    if minimums[0] < left:
        minimums.popleft()
    if maximums[0] < left:
        maximums.popleft()
    if value >= k:
        answer = min(answer, position[maximums[0]] - position[minimums[0]])
print(answer)
