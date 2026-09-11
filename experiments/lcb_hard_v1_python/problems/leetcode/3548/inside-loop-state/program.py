import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from collections import Counter
from math import factorial

class Solution:

    def countGoodIntegers(self, n: int, k: int) -> int:
        fac = [factorial(i) for i in range(n + 1)]
        ans = 0
        vis = set()
        base = 10 ** ((n - 1) // 2)
        for i in range(base, base * 10):
            s = str(i)
            s += s[::-1][n % 2:]
            if int(s) % k:
                continue
            t = ''.join(sorted(s))
            if t in vis:
                continue
            vis.add(t)
            cnt = Counter(t)
            res = (n - cnt['0']) * fac[n - 1]
            for x in cnt.values():
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'cnt': cnt, 'i': i, 'k': k, 'res': res, 's': s, 't': t, 'len(vis)': len(vis), 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                res //= fac[x]
            ans += res
        return ans

def _read_lcb_input(names):
    text = sys.stdin.read()
    decoder = json.JSONDecoder()
    values = []
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset == len(text):
            break
        value, offset = decoder.raw_decode(text, offset)
        values.append(value)
    if len(values) == 1:
        value = values[0]
        if isinstance(value, dict) and all((name in value for name in names)):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError('input argument count does not match the solution signature')
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('n', 'k'))
    result = Solution().countGoodIntegers(data['n'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
