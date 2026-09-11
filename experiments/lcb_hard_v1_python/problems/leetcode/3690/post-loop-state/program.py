import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from bisect import bisect_left

class Solution:

    def minLength(self, s: str, numOps: int) -> int:

        def check(m: int) -> bool:
            cnt = 0
            if m == 1:
                t = '01'
                cnt = sum((c == t[i & 1] for i, c in enumerate(s)))
                cnt = min(cnt, n - cnt)
            else:
                k = 0
                for i, c in enumerate(s):
                    _lcb_count[0] += 1
                    k += 1
                    if i == len(s) - 1 or c != s[i + 1]:
                        cnt += k // (m + 1)
                        k = 0
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'k': k, 'm': m, 'n': n, 'numOps': numOps, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
            return cnt <= numOps
        n = len(s)
        return bisect_left(range(n), True, lo=1, key=check)

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
    data = _read_lcb_input(('s', 'numOps'))
    result = Solution().minLength(data['s'], data['numOps'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
