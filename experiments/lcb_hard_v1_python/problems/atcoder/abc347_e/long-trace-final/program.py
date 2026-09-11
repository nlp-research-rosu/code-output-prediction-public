import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, q = data[:2]
queries = data[2:]
active = set()
started = [0] * (n + 1)
answer = [0] * (n + 1)
accumulated_size = 0
for value in queries:
    if value in active:
        answer[value] += accumulated_size - started[value]
        active.remove(value)
    else:
        active.add(value)
        started[value] = accumulated_size
    accumulated_size += len(active)
for value in active:
    answer[value] += accumulated_size - started[value]
print(*answer[1:])
