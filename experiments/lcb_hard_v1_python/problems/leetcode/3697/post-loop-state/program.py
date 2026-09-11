import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def minimumIncrements(self, nums, target):
        INF = float('inf')

        def gcd(a, b):
            while b:
                a, b = (b, a % b)
            return a

        def lcm(a, b):
            return a // gcd(a, b) * b
        n = len(nums)
        m = len(target)
        lcms = [0] * (1 << m)
        for mask in list(range(1 << m)):
            l = 1
            for i in list(range(m)):
                if mask & 1 << i:
                    l = lcm(l, target[i])
            lcms[mask] = l
        dp = [INF] * (1 << m)
        dp[0] = 0
        for x in nums:
            for mask in reversed(list(range(1 << m))):
                if dp[mask] == INF:
                    continue
                submask = new_mask = (1 << m) - 1 - mask
                while submask:
                    _lcb_count[0] += 1
                    dp[mask | submask] = min(dp[mask | submask], dp[mask] + (lcms[submask] - x % lcms[submask] if x % lcms[submask] else 0))
                    submask = submask - 1 & new_mask
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'dp[mask]': dp[mask], 'dp[mask|submask]': dp[mask | submask], 'lcms': lcms, 'mask': mask, 'new_mask': new_mask, 'submask': submask, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
        return dp[-1]

def function(nums, target):
    return Solution().minimumIncrements(nums=nums, target=target)

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
    data = _read_lcb_input(('nums', 'target'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
