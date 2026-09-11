import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math

def main():
    input = sys.stdin.read
    data = input().split()
    t = int(data[0])
    index = 1
    for _ in range(t):
        n = int(data[index])
        index += 1
        a = list(map(int, data[index:index + n]))
        index += n
        prefix = [0] * (n + 1)
        for i in range(n):
            prefix[i + 1] = prefix[i] + a[i]
        max_diff = 0
        for k in range(1, n + 1):
            if n % k != 0:
                continue
            sums = set()
            for i in range(k, n + 1, k):
                _lcb_count[0] += 1
                group_sum = prefix[i] - prefix[i - k]
                sums.add(group_sum)
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'group_sum': group_sum, 'i': i, 'k': k, 'len(sums)': len(sums), 'max_diff': max_diff, 'prefix[i-k]': prefix[i - k], 'prefix[i]': prefix[i]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if len(sums) < 2:
                continue
            current_max = max(sums)
            current_min = min(sums)
            max_diff = max(max_diff, current_max - current_min)
        print(max_diff)
if __name__ == '__main__':
    main()
