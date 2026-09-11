import json, sys

class Solution(object):

    def findMaximumLength(self, nums):
        dp = prefix = left = 0
        stk = [(0, 0, 0)]
        for right in list(range(len(nums))):
            prefix += nums[right]
            while left + 1 < len(stk) and stk[left + 1][0] <= prefix:
                left += 1
            last, dp = (prefix - stk[left][1], stk[left][2] + 1)
            while stk and stk[-1][0] >= last + prefix:
                stk.pop()
            stk.append((last + prefix, prefix, dp))
            left = min(left, len(stk) - 1)
        return dp

def function(nums):
    return Solution().findMaximumLength(nums=nums)

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
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
