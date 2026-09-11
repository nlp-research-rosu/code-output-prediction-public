import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce
import collections

class Solution(object):

    def minimumValueSum(self, nums, andValues):
        INF = float('inf')
        L = max(nums).bit_length()

        def update(cnt, x, d):
            for i in list(range(L)):
                if x & 1 << i:
                    cnt[i] += d

        def mask(cnt, l):
            return reduce(lambda accu, i: accu | 1 << i, (i for i in list(range(L)) if cnt[i] == l), 0)
        dp = [INF] * (len(nums) + 1)
        dp[0] = 0
        for j in list(range(len(andValues))):
            new_dp = [INF] * (len(nums) + 1)
            cnt = [0] * L
            l = [0] * len(dp)
            dq = collections.deque()
            left = idx = j
            for right in list(range(j, len(nums))):
                update(cnt, nums[right], +1)
                if mask(cnt, right - left + 1) <= andValues[j]:
                    while left <= right:
                        _lcb_count[0] += 1
                        if _lcb_count[0] == 502:
                            _lcb_sys.stdout.write(_lcb_json.dumps({'andValues[j]': andValues[j], 'cnt': cnt, 'idx': idx, 'j': j, 'l': l, 'left': left, 'nums[left]': nums[left], 'nums[right]': nums[right], 'right': right}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                            raise SystemExit
                        if mask(cnt, right - left + 1) > andValues[j]:
                            break
                        update(cnt, nums[left], -1)
                        left += 1
                    left -= 1
                    update(cnt, nums[left], +1)
                if andValues[j] & nums[right] == andValues[j]:
                    l[right + 1] = l[right] + 1
                if mask(cnt, right - left + 1) != andValues[j]:
                    continue
                while idx <= left:
                    while dq and dp[dq[-1]] >= dp[idx]:
                        dq.pop()
                    dq.append(idx)
                    idx += 1
                while dq and dq[0] < left - l[left]:
                    dq.popleft()
                if dq:
                    new_dp[right + 1] = dp[dq[0]] + nums[right]
            dp = new_dp
        return dp[-1] if dp[-1] != INF else -1

def function(nums, andValues):
    return Solution().minimumValueSum(nums=nums, andValues=andValues)

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
    data = _read_lcb_input(('nums', 'andValues'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
