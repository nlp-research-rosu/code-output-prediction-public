import json
import sys

from typing import List

class Solution:

    def minOrAfterOperations(self, nums: List[int], k: int) -> int:
        ans = 0
        rans = 0
        for i in range(29, -1, -1):
            test = ans + (1 << i)
            cnt = 0
            val = 0
            for num in nums:
                if val == 0:
                    val = test & num
                else:
                    val &= test & num
                if val:
                    cnt += 1
            if cnt > k:
                rans += 1 << i
            else:
                ans += 1 << i
        return rans

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
    result = Solution().minOrAfterOperations(data['nums'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
