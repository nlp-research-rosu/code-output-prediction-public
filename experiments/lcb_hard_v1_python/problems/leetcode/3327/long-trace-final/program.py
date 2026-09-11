import json
import sys

from typing import List
from math import inf

class Solution:

    def minimumMoves(self, nums: List[int], k: int, maxChanges: int) -> int:
        n = len(nums)
        cnt = [0] * (n + 1)
        s = [0] * (n + 1)
        for i, x in enumerate(nums, 1):
            cnt[i] = cnt[i - 1] + x
            s[i] = s[i - 1] + i * x
        ans = inf
        max = lambda x, y: x if x > y else y
        min = lambda x, y: x if x < y else y
        for i, x in enumerate(nums, 1):
            t = 0
            need = k - x
            for j in (i - 1, i + 1):
                if need > 0 and 1 <= j <= n and (nums[j - 1] == 1):
                    need -= 1
                    t += 1
            c = min(need, maxChanges)
            need -= c
            t += c * 2
            if need <= 0:
                ans = min(ans, t)
                continue
            l, r = (2, max(i - 1, n - i))
            while l <= r:
                mid = l + r >> 1
                l1, r1 = (max(1, i - mid), max(0, i - 2))
                l2, r2 = (min(n + 1, i + 2), min(n, i + mid))
                c1 = cnt[r1] - cnt[l1 - 1]
                c2 = cnt[r2] - cnt[l2 - 1]
                if c1 + c2 >= need:
                    t1 = c1 * i - (s[r1] - s[l1 - 1])
                    t2 = s[r2] - s[l2 - 1] - c2 * i
                    ans = min(ans, t + t1 + t2)
                    r = mid - 1
                else:
                    l = mid + 1
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
    data = _read_lcb_input(('nums', 'k', 'maxChanges'))
    result = Solution().minimumMoves(data['nums'], data['k'], data['maxChanges'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
