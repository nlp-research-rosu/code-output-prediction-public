import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def sumOfPowers(self, nums, k):
        MOD = 10 ** 9 + 7
        nums.sort()
        result = prev = 0
        for mn in sorted({nums[j] - nums[i] for i in list(range(len(nums))) for j in list(range(i + 1, len(nums)))}, reverse=True):
            dp = [[0] * (k + 1) for _ in list(range(len(nums) + 1))]
            dp[0][0] = 1
            j = 0
            for i in list(range(len(nums))):
                j = next((j for j in list(range(j, len(nums))) if nums[i] - nums[j] < mn), len(nums))
                for l in list(range(1, k + 1)):
                    dp[i + 1][l] = (dp[i + 1][l] + dp[j - 1 + 1][l - 1]) % MOD
                for l in list(range(k + 1)):
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'j': j, 'k': k, 'l': l, 'mn': mn, 'nums': nums, 'prev': prev, 'result': result}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    dp[i + 1][l] = (dp[i + 1][l] + dp[i][l]) % MOD
            cnt = (dp[-1][k] - prev) % MOD
            result = (result + mn * cnt) % MOD
            prev = dp[-1][k]
        return result

def function(nums, k):
    return Solution().sumOfPowers(nums=nums, k=k)

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
    data = _read_lcb_input(('nums', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
