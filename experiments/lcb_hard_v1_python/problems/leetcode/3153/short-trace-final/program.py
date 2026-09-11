import json
import sys

from typing import List

class Solution:

    def maxSum(self, nums: List[int], k: int) -> int:
        mod = 10 ** 9 + 7
        cnt = [0] * 31
        for x in nums:
            for i in range(31):
                if x >> i & 1:
                    cnt[i] += 1
        ans = 0
        for _ in range(k):
            x = 0
            for i in range(31):
                if cnt[i]:
                    x |= 1 << i
                    cnt[i] -= 1
            ans = (ans + x * x) % mod
        return ans

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
    result = Solution().maxSum(data['nums'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
