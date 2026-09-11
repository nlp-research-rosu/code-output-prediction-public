import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
heights = data[1:]
stack = []
area = 0
answer = []
for height in heights:
    _lcb_count[0] += 1
    width = 1
    while stack and stack[-1][0] <= height:
        previous_height, previous_width = stack.pop()
        area -= previous_height * previous_width
        width += previous_width
    stack.append((height, width))
    area += height * width
    answer.append(area + 1)
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'area': area, 'height': height, 'stack': stack, 'width': width}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print(*answer)
