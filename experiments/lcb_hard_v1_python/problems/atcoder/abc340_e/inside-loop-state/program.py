import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, m = data[:2]
initial = data[2:2 + n]
operations = data[2 + n:]
tree = [0] * (n + 2)

def add(index, value):
    index += 1
    while index <= n + 1:
        tree[index] += value
        index += index & -index

def range_add(left, right, value):
    if left >= right:
        return
    add(left, value)
    add(right, -value)

def point(index):
    result = 0
    index += 1
    while index:
        result += tree[index]
        index -= index & -index
    return result
for index, value in enumerate(initial):
    range_add(index, index + 1, value)
for box in operations:
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'balls': balls, 'box': box, 'end': end, 'quotient': quotient, 'remainder': remainder, 'tree': tree}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    balls = point(box)
    range_add(box, box + 1, -balls)
    quotient, remainder = divmod(balls, n)
    range_add(0, n, quotient)
    end = box + 1 + remainder
    if end <= n:
        range_add(box + 1, end, 1)
    else:
        range_add(box + 1, n, 1)
        range_add(0, end - n, 1)
print(*(point(index) for index in range(n)))
