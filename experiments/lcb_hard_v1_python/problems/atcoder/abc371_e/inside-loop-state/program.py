import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
n = int(input())
a = list(map(int, input().split()))
last_occurrence = {}
total = 0
for i in range(n):
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'last_occurrence': last_occurrence, 'num': num, 'prev': prev, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    num = a[i]
    if num in last_occurrence:
        prev = last_occurrence[num]
    else:
        prev = -1
    total += (i - prev) * (n - i)
    last_occurrence[num] = i
print(total)
