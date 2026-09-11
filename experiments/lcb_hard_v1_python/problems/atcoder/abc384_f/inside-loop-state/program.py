import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
from collections import defaultdict

def compute_f(x):
    while x % 2 == 0:
        x //= 2
    return x

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    A = list(map(int, data[1:]))
    count = defaultdict(int)
    for i in range(N):
        for j in range(i, N):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'count': count, 'f_s': f_s, 'i': i, 'j': j, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            s = A[i] + A[j]
            f_s = compute_f(s)
            count[f_s] += 1
    total = 0
    for f_val, cnt in count.items():
        total += f_val * cnt
    print(total)
if __name__ == '__main__':
    main()
