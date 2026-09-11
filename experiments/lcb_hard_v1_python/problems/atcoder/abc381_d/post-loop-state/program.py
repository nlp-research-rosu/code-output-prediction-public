import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
values = data[1:]
answer = 0
for parity in range(2):
    last = {}
    left = parity
    for index in range(parity, n - 1, 2):
        _lcb_count[0] += 1
        if values[index] != values[index + 1]:
            left = index + 2
            continue
        value = values[index]
        if last.get(value, -2) >= left:
            left = last[value] + 2
        last[value] = index
        answer = max(answer, index + 2 - left)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'index': index, 'last': last, 'left': left, 'parity': parity, 'value': value, 'values[index:index + 8]': values[index:index + 8]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
print(answer)
