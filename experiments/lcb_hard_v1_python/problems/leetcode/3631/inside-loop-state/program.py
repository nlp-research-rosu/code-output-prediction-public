import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from functools import reduce
cnt = [0] * 2

class Solution(object):

    def countKReducibleNumbers(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """
        MOD = 10 ** 9 + 7

        def popcount(x):
            return bin(x).count('1')
        while len(s) - 1 >= len(cnt):
            cnt.append(cnt[popcount(len(cnt))] + 1)
        dp = [0] * len(s)
        curr = 0
        for i in range(len(s)):
            for j in reversed(range(i)):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'MOD': MOD, 'curr': curr, 'dp': dp, 'i': i, 'j': j, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                dp[j + 1] = (dp[j + 1] + dp[j]) % MOD
            if s[i] != '1':
                continue
            dp[curr] = (dp[curr] + 1) % MOD
            curr += 1
        return reduce(lambda accu, x: (accu + x) % MOD, (dp[i] for i in range(1, len(s)) if cnt[i] < k), 0)
cnt = [0] * 2

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
    data = _read_lcb_input(('s', 'k'))
    result = Solution().countKReducibleNumbers(data['s'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
