import json, sys

class Solution(object):

    def maxFrequencyScore(self, nums, k):
        nums.sort()
        result = left = curr = 0
        for right in list(range(len(nums))):
            curr += nums[right] - nums[(left + right) // 2]
            if not curr <= k:
                curr -= nums[(left + 1 + right) // 2] - nums[left]
                left += 1
        return right - left + 1

def function(nums, k):
    return Solution().maxFrequencyScore(nums=nums, k=k)

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
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
