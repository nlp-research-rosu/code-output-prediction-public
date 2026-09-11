import json, sys

class Solution:

    def maximumSum(self, nums):
        n = len(nums)
        answer = nums[0]
        for base in range(1, n + 1):
            total = 0
            multiplier = 1
            while base * multiplier * multiplier <= n:
                total += nums[base * multiplier * multiplier - 1]
                multiplier += 1
            answer = max(answer, total)
        return answer

def function(nums):
    return Solution().maximumSum(nums=nums)

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
