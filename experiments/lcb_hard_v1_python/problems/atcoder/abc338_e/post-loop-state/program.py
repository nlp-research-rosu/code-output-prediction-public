import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
N = int(input())
AB = [list(map(int, input().split())) for _ in range(N)]
events = []
for i, (a, b) in enumerate(AB):
    s, l = (min(a, b), max(a, b))
    events.append(((s, -l), 1, i))
    events.append(((l, s), -1, i))
stamp = [0] * N
cur = 0
for (x, _), t, i in sorted(events):
    _lcb_count[0] += 1
    if t == 1:
        stamp[i] = cur
        cur += 1
    else:
        cur -= 1
        if stamp[i] != cur:
            print('Yes')
            sys.exit()
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'cur': cur, 'i': i, 'stamp': stamp, 't': t, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print('No')
