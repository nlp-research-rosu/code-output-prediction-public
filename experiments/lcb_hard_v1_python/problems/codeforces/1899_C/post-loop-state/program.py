import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    input = sys.stdin.read
    data = input().split()
    idx = 0
    t = int(data[idx])
    idx += 1
    results = []
    for _ in range(t):
        n = int(data[idx])
        idx += 1
        a = list(map(int, data[idx:idx + n]))
        idx += n
        max_even = -float('inf')
        max_odd = -float('inf')
        result = -float('inf')
        for num in a:
            _lcb_count[0] += 1
            if num % 2 == 0:
                max_even = max(num, max_odd + num)
                max_odd = -float('inf')
            else:
                max_odd = max(num, max_even + num)
                max_even = -float('inf')
            result = max(result, max_even, max_odd)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'n': n, 'num': num, 'result': result}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        results.append(str(result))
    print('\n'.join(results))
if __name__ == '__main__':
    main()
