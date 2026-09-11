import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def countOfPairs(self, nums):
        fact, inv, inv_fact = [[1] * 2 for _ in list(range(3))]

        def nCr(n, k):
            while len(inv) <= n:
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'MOD': MOD, 'fact[-5:]': fact[-5:], 'inv[-5:]': inv[-5:], 'inv_fact[-5:]': inv_fact[-5:], 'k': k, 'len(inv)': len(inv), 'n': n}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                fact.append(fact[-1] * len(inv) % MOD)
                inv.append(inv[MOD % len(inv)] * (MOD - MOD // len(inv)) % MOD)
                inv_fact.append(inv_fact[-1] * inv[-1] % MOD)
            return fact[n] * inv_fact[n - k] % MOD * inv_fact[k] % MOD

        def nHr(n, r):
            return nCr(n + r - 1, r)
        MOD = 10 ** 9 + 7
        cnt = nums[-1] - sum((max(nums[i] - nums[i - 1], 0) for i in list(range(1, len(nums)))))
        return nHr(len(nums) + 1, cnt) if cnt >= 0 else 0

def function(nums):
    return Solution().countOfPairs(nums=nums)

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
