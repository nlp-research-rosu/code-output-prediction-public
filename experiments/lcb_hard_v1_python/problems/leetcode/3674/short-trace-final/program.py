import json
import sys

import collections

import collections

class Solution(object):

    def countNonDecreasingSubarrays(self, nums, k):
        """
        :type nums: List[int]
        :type k: int
        :rtype: int
        """
        result = cnt = 0
        dq = collections.deque()
        right = len(nums) - 1
        for left in reversed(range(len(nums))):
            while dq and nums[dq[-1]] < nums[left]:
                l = dq.pop()
                r = dq[-1] - 1 if dq else right
                cnt += (r - l + 1) * (nums[left] - nums[l])
            dq.append(left)
            while cnt > k:
                cnt -= nums[dq[0]] - nums[right]
                if dq[0] == right:
                    dq.popleft()
                right -= 1
            result += right - left + 1
        return result

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
        if isinstance(value, dict) and all(name in value for name in names):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError("input argument count does not match the solution signature")
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('nums', 'k'))
    result = Solution().countNonDecreasingSubarrays(data['nums'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
