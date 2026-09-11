import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import bisect
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, q = data[:2]
points = sorted(data[2:2 + n])
index = 2 + n
answer = []
for _ in range(q):
    center, count = (data[index], data[index + 1])
    index += 2
    low = -1
    high = 200000001
    while high - low > 1:
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'center': center, 'count': count, 'high': high, 'inside': inside, 'low': low, 'middle': middle}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        middle = (low + high) // 2
        inside = bisect.bisect_right(points, center + middle) - bisect.bisect_left(points, center - middle)
        if inside >= count:
            high = middle
        else:
            low = middle
    answer.append(high)
print(*answer, sep='\n')
