import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys

class Solution(object):

    def maxValue(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: int
        """
        INF = float('inf')
        MAX_MASK = 127

        def is_submask(a, b):
            return a | b == b

        def dp(direction, npos):
            result = [npos] * (MAX_MASK + 1)
            dp = [INF] * (MAX_MASK + 1)
            cnt = [0] * (MAX_MASK + 1)
            for i in direction(range(len(nums))):
                dp[nums[i]] = 1
                for mask in range(MAX_MASK + 1):
                    if is_submask(nums[i], mask):
                        cnt[mask] += 1
                    dp[mask | nums[i]] = min(dp[mask | nums[i]], dp[mask] + 1)
                for mask in range(MAX_MASK + 1):
                    if cnt[mask] >= k and dp[mask] <= k and (result[mask] == npos):
                        result[mask] = i
            return result
        left = dp(lambda x: x, len(nums))
        right = dp(reversed, -1)
        return next((result for result in reversed(range(MAX_MASK + 1)) for l in range(1, MAX_MASK + 1) if left[l] < right[result ^ l]))

class Solution(object):

    def maxValue(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: int
        """
        left = [[set() if j else {0} for j in range(k + 1)] for i in range(len(nums) + 1)]
        for i in range(len(nums)):
            for j in range(1, len(left[i + 1])):
                left[i + 1][j] = set(left[i][j])
                for x in left[i][j - 1]:
                    left[i + 1][j].add(x | nums[i])
        right = [[set() if j else {0} for j in range(k + 1)] for i in range(len(nums) + 1)]
        for i in reversed(range(len(nums))):
            for j in range(1, len(right[i])):
                right[i][j] = set(right[i + 1][j])
                for x in right[i + 1][j - 1]:
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'len(right[i][j])': len(right[i][j]), 'nums[i]': nums[i], 'sorted(right[i][j])': sorted(right[i][j]), 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    right[i][j].add(x | nums[i])
        return max((l ^ r for i in range(k, len(nums) - k + 1) for l in left[i][k] for r in right[i][k]))

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
    result = Solution().maxValue(data['nums'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
