import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys

class Solution(object):

    def maxPartitionsAfterOperations(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """

        def popcount(n):
            n = (n & 1431655765) + (n >> 1 & 1431655765)
            n = (n & 858993459) + (n >> 2 & 858993459)
            n = (n & 252645135) + (n >> 4 & 252645135)
            n = (n & 16711935) + (n >> 8 & 16711935)
            n = (n & 65535) + (n >> 16 & 65535)
            return n
        left = [0] * (len(s) + 1)
        left_mask = [0] * (len(s) + 1)
        cnt = mask = 0
        for i in range(len(s)):
            mask |= 1 << ord(s[i]) - ord('a')
            if popcount(mask) > k:
                cnt += 1
                mask = 1 << ord(s[i]) - ord('a')
            left[i + 1] = cnt
            left_mask[i + 1] = mask
        right = [0] * (len(s) + 1)
        right_mask = [0] * (len(s) + 1)
        cnt = mask = 0
        for i in reversed(range(len(s))):
            mask |= 1 << ord(s[i]) - ord('a')
            if popcount(mask) > k:
                cnt += 1
                mask = 1 << ord(s[i]) - ord('a')
            right[i] = cnt
            right_mask[i] = mask
        result = 0
        for i in range(len(s)):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'curr': curr, 'i': i, 'left[i]': left[i], 'left_mask[i]': left_mask[i], 'mask': mask, 'result': result, 'right[i+1]': right[i + 1], 'right_mask[i+1]': right_mask[i + 1]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            curr = left[i] + right[i + 1]
            mask = left_mask[i] | right_mask[i + 1]
            if popcount(left_mask[i]) == popcount(right_mask[i + 1]) == k and popcount(mask) != 26:
                curr += 3
            elif popcount(mask) + int(popcount(mask) != 26) > k:
                curr += 2
            else:
                curr += 1
            result = max(result, curr)
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
        if isinstance(value, dict) and all((name in value for name in names)):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError('input argument count does not match the solution signature')
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('s', 'k'))
    result = Solution().maxPartitionsAfterOperations(data['s'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
