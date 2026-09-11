import json
import sys

class Solution(object):

    def minDifference(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """

        def binary_search(left, right, check):
            while left <= right:
                mid = left + (right - left) // 2
                if check(mid):
                    right = mid - 1
                else:
                    left = mid + 1
            return left

        def check(d):
            prev = cnt = 0
            for i in range(len(nums)):
                if nums[i] == -1:
                    cnt += 1
                    continue
                if prev and cnt and (min((max(abs(prev - x), abs(nums[i] - x)) for x in (left + d, right - d))) > d) and (cnt == 1 or right - d - (left + d) > d):
                    return False
                prev = nums[i]
                cnt = 0
            return True
        max_diff, left, right = (0, float('inf'), 0)
        for i in range(len(nums)):
            if nums[i] != -1:
                if i + 1 < len(nums) and nums[i + 1] != -1:
                    max_diff = max(max_diff, abs(nums[i] - nums[i + 1]))
                continue
            if i - 1 < len(nums) and nums[i - 1] != -1:
                left = min(left, nums[i - 1])
                right = max(right, nums[i - 1])
            if i + 1 < len(nums) and nums[i + 1] != -1:
                left = min(left, nums[i + 1])
                right = max(right, nums[i + 1])
        return binary_search(max_diff, (right - left) // 2, check)

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
    data = _read_lcb_input(('nums',))
    result = Solution().minDifference(data['nums'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
