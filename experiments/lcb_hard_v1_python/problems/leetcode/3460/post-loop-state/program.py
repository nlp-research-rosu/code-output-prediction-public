import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce

class Solution(object):

    def numberOfPermutations(self, n, requirements):
        MOD = 10 ** 9 + 7
        lookup = [-1] * n
        for i, c in requirements:
            lookup[i] = c
        dp = [1]
        prev = 0
        for i in list(range(n)):
            if lookup[i] != -1:
                dp = [reduce(lambda total, i: (total + dp[i]) % MOD, list(range(max(lookup[i] - i - prev, 0), min(lookup[i] + 1 - prev, len(dp)))), 0)]
                prev = lookup[i]
                continue
            new_dp = [0] * min(len(dp) + (i + 1 - 1), lookup[-1] + 1 - prev)
            for j in list(range(len(new_dp))):
                _lcb_count[0] += 1
                new_dp[j] = dp[j] if j < len(dp) else 0
                if j - 1 >= 0:
                    new_dp[j] = (new_dp[j] + new_dp[j - 1]) % MOD
                if j - (i + 1) >= 0:
                    new_dp[j] = (new_dp[j] - dp[j - (i + 1)]) % MOD
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'j': j, 'lookup': lookup, 'n': n, 'new_dp': new_dp, 'prev': prev}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            dp = new_dp
        return dp[-1]

def function(n, requirements):
    return Solution().numberOfPermutations(n=n, requirements=requirements)

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
    data = _read_lcb_input(('n', 'requirements'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
