import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
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
    _lcb_count[0] += 1
    answer[value] += accumulated_size - started[value]
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'accumulated_size': accumulated_size, 'answer': answer, 'value': value}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print(*answer[1:])
