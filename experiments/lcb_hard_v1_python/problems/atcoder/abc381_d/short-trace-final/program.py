import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
values = data[1:]
answer = 0
for parity in range(2):
    last = {}
    left = parity
    for index in range(parity, n - 1, 2):
        if values[index] != values[index + 1]:
            left = index + 2
            continue
        value = values[index]
        if last.get(value, -2) >= left:
            left = last[value] + 2
        last[value] = index
        answer = max(answer, index + 2 - left)
print(answer)
