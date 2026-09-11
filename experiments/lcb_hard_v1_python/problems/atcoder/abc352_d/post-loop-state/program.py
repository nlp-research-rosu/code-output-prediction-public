import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
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
    _lcb_count[0] += 1
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
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'current': current, 'left': left, 'position': position, 'value': value}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print(answer)
