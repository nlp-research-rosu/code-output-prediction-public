import json
import sys

from typing import List

m = 50
cnt = [0] * (m + 1)
s = [0] * (m + 1)
p = 1
for i in range(1, m + 1):
    cnt[i] = cnt[i - 1] * 2 + p
    s[i] = s[i - 1] * 2 + p * (i - 1)
    p *= 2

def num_idx_and_sum(x: int) -> tuple:
    idx = 0
    total_sum = 0
    while x:
        i = x.bit_length() - 1
        idx += cnt[i]
        total_sum += s[i]
        x -= 1 << i
        total_sum += (x + 1) * i
        idx += x + 1
    return (idx, total_sum)

def f(i: int) -> int:
    l, r = (0, 1 << m)
    while l < r:
        mid = l + r + 1 >> 1
        idx, _ = num_idx_and_sum(mid)
        if idx < i:
            l = mid
        else:
            r = mid - 1
    total_sum = 0
    idx, total_sum = num_idx_and_sum(l)
    i -= idx
    x = l + 1
    for _ in range(i):
        y = x & -x
        total_sum += y.bit_length() - 1
        x -= y
    return total_sum

class Solution:

    def findProductsOfElements(self, queries: List[List[int]]) -> List[int]:
        return [pow(2, f(right + 1) - f(left), mod) for left, right, mod in queries]

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
    data = _read_lcb_input(('queries',))
    result = Solution().findProductsOfElements(data['queries'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
