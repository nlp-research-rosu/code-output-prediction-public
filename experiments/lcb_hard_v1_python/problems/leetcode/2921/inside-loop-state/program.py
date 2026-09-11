import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce

class Solution(object):

    def countSteppingNumbers(self, low, high):
        MOD = 10 ** 9 + 7

        def f(s):
            dp = [[0] * 10 for _ in list(range(2))]
            for j in list(range(1, ord(s[0]) - ord('0') + 1)):
                dp[0][j] = 1
            prefix = True
            for i in list(range(1, len(s))):
                for j in list(range(10)):
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'j': j, 'prefix': prefix, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    dp[i % 2][j] = int(j != 0)
                    if j - 1 >= 0:
                        dp[i % 2][j] = (dp[i % 2][j] + (dp[(i - 1) % 2][j - 1] - int(prefix and ord(s[i - 1]) - ord('0') == j - 1 and (j > ord(s[i]) - ord('0'))))) % MOD
                    if j + 1 < 10:
                        dp[i % 2][j] = (dp[i % 2][j] + (dp[(i - 1) % 2][j + 1] - int(prefix and ord(s[i - 1]) - ord('0') == j + 1 and (j > ord(s[i]) - ord('0'))))) % MOD
                if abs(ord(s[i]) - ord(s[i - 1])) != 1:
                    prefix = False
            return reduce(lambda x, y: (x + y) % MOD, dp[(len(s) - 1) % 2])
        return (f(high) - f(str(int(low) - 1))) % MOD

def function(low, high):
    return Solution().countSteppingNumbers(low=low, high=high)

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
    data = _read_lcb_input(('low', 'high'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
