import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
import collections

class Solution(object):

    def minMaxSubarraySum(self, nums, k):

        def count(check):
            result = total = 0
            dq = collections.deque()
            for right in list(range(len(nums))):
                while dq and (not check(nums[dq[-1]], nums[right])):
                    _lcb_count[0] += 1
                    i = dq.pop()
                    cnt = i - (dq[-1] + 1 if dq else max(right - k + 1, 0)) + 1
                    total -= cnt * nums[i]
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'k': k, 'list(dq)': list(dq), 'nums[i]': nums[i], 'result': result, 'right': right, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                cnt = right - (dq[-1] + 1 if dq else max(right - k + 1, 0)) + 1
                dq.append(right)
                total += cnt * nums[right]
                result += total
                if right - (k - 1) >= 0:
                    total -= nums[dq[0]]
                    if dq[0] == right - (k - 1):
                        dq.popleft()
            return result
        return count(lambda a, b: a < b) + count(lambda a, b: a > b)

def function(nums, k):
    return Solution().minMaxSubarraySum(nums=nums, k=k)

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
