import json, sys
from functools import reduce
import itertools

class Solution(object):

    def findKthSmallest(self, coins, k):

        def gcd(a, b):
            while b:
                a, b = (b, a % b)
            return a

        def lcm(a, b):
            return a // gcd(a, b) * b

        def check(target):
            return sum(((-1 if i + 1 & 1 else +1) * (target // l) for i in list(range(1, len(coins) + 1)) for l in lookup[i])) >= k

        def binary_search(left, right, check):
            while left <= right:
                mid = left + (right - left) // 2
                if check(mid):
                    right = mid - 1
                else:
                    left = mid + 1
            return left
        lookup = [[] for _ in list(range(len(coins) + 1))]
        for i in list(range(1, len(coins) + 1)):
            for comb in itertools.combinations(coins, i):
                lookup[i].append(reduce(lcm, comb))
        mn = min(coins)
        l = 1
        for i in list(range(1, 25 + 1)):
            l = lcm(l, i)
        return binary_search(mn, k * mn, check)

def function(coins, k):
    return Solution().findKthSmallest(coins=coins, k=k)

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
    data = _read_lcb_input(('coins', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
