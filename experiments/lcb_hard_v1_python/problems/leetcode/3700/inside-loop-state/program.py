import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
import collections

class Solution(object):

    def subsequencesWithMiddleMode(self, nums):

        def nC2(x):
            return x * (x - 1) // 2
        MOD = 10 ** 9 + 7
        result = 0
        left = collections.defaultdict(int)
        right = collections.defaultdict(int)
        for x in nums:
            right[x] += 1
        left_x_sq = 0
        right_x_sq = sum((v ** 2 for v in right.values()))
        left_x_right_x = 0
        left_x_sq_right_x = 0
        left_x_right_x_sq = 0
        for i, v in enumerate(nums):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'left': left, 'left_x_right_x_sq': left_x_right_x_sq, 'left_x_sq': left_x_sq, 'left_x_sq_right_x': left_x_sq_right_x, 'result': result, 'right': right, 'right_x_sq': right_x_sq, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            left_x_sq -= left[v] ** 2
            right_x_sq -= right[v] ** 2
            left_x_right_x -= left[v] * right[v]
            left_x_sq_right_x -= left[v] ** 2 * right[v]
            left_x_right_x_sq -= left[v] * right[v] ** 2
            right[v] -= 1
            l, r = (i, len(nums) - (i + 1))
            result += nC2(l) * nC2(r)
            result -= nC2(l - left[v]) * nC2(r - right[v])
            result -= ((left_x_sq - (l - left[v])) * (r - right[v]) - (left_x_sq_right_x - left_x_right_x)) * right[v] // 2
            result -= ((right_x_sq - (r - right[v])) * (l - left[v]) - (left_x_right_x_sq - left_x_right_x)) * left[v] // 2
            result -= left[v] * left_x_right_x * (r - right[v]) - left[v] * left_x_right_x_sq
            result -= right[v] * left_x_right_x * (l - left[v]) - right[v] * left_x_sq_right_x
            result -= right[v] * (left_x_sq_right_x - left_x_right_x) // 2
            result -= left[v] * (left_x_right_x_sq - left_x_right_x) // 2
            left[v] += 1
            left_x_sq += left[v] ** 2
            right_x_sq += right[v] ** 2
            left_x_right_x += left[v] * right[v]
            left_x_sq_right_x += left[v] ** 2 * right[v]
            left_x_right_x_sq += left[v] * right[v] ** 2
        return result % MOD

def function(nums):
    return Solution().subsequencesWithMiddleMode(nums=nums)

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
