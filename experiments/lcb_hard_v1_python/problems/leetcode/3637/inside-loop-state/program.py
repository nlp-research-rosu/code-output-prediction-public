import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from collections import Counter
from functools import cache
from math import comb

class Solution:

    def countBalancedPermutations(self, num: str) -> int:

        @cache
        def dfs(i: int, j: int, a: int, b: int) -> int:
            if i > 9:
                return j | a | b == 0
            if a == 0 and j:
                return 0
            ans = 0
            for l in range(min(cnt[i], a) + 1):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'ans': ans, 'b': b, 'cnt': cnt, 'i': i, 'j': j, 'l': l, 'mod': mod, 'r': r}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                r = cnt[i] - l
                if 0 <= r <= b and l * i <= j:
                    t = comb(a, l) * comb(b, r) * dfs(i + 1, j - l * i, a - l, b - r)
                    ans = (ans + t) % mod
            return ans
        nums = list(map(int, num))
        s = sum(nums)
        if s % 2:
            return 0
        n = len(nums)
        mod = 10 ** 9 + 7
        cnt = Counter(nums)
        return dfs(0, s // 2, n // 2, (n + 1) // 2)

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
    data = _read_lcb_input(('num',))
    result = Solution().countBalancedPermutations(data['num'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
