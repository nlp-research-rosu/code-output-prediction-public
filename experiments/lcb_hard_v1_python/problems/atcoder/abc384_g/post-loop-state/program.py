import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
n = int(sys.stdin.readline())
a = list(map(int, sys.stdin.readline().split()))
b = list(map(int, sys.stdin.readline().split()))
k = int(sys.stdin.readline())
queries = []
for _ in range(k):
    x, y = map(int, sys.stdin.readline().split())
    queries.append((x, y))
prefix_arrays = []
for bj in b:
    prefix = [0] * n
    current_sum = 0
    for i in range(n):
        _lcb_count[0] += 1
        current_sum += abs(a[i] - bj)
        prefix[i] = current_sum
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'bj': bj, 'current_sum': current_sum, 'i': i, 'prefix': prefix, 'prefix_arrays': prefix_arrays}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    prefix_arrays.append(prefix)
for x, y in queries:
    x -= 1
    y -= 1
    sum_val = 0
    for j in range(y + 1):
        sum_val += prefix_arrays[j][x]
    print(sum_val)
