import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce
import collections

class Solution(object):

    def sumOfGoodSubsequences(self, nums):
        MOD = 10 ** 9 + 7
        dp = collections.defaultdict(int)
        cnt = collections.defaultdict(int)
        for x in nums:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'c': c, 'cnt': cnt, 'dp': dp, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            c = cnt[x - 1] + cnt[x + 1] + 1
            cnt[x] = (cnt[x] + c) % MOD
            dp[x] = (dp[x] + (dp[x - 1] + dp[x + 1] + x * c)) % MOD
        return reduce(lambda accu, x: (accu + x) % MOD, dp.values())

def function(nums):
    return Solution().sumOfGoodSubsequences(nums=nums)

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
    data = _read_lcb_input(('nums',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
