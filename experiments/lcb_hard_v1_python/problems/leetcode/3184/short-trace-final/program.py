import json, sys

class Solution(object):

    def maxBalancedSubsequenceSum(self, nums):
        NEG_INF = float('-inf')

        class BIT(object):

            def __init__(self, n, default=0, fn=lambda x, y: x + y):
                self.__bit = [NEG_INF] * (n + 1)
                self.__default = default
                self.__fn = fn

            def update(self, i, val):
                i += 1
                while i < len(self.__bit):
                    self.__bit[i] = self.__fn(self.__bit[i], val)
                    i += i & -i

            def query(self, i):
                i += 1
                ret = self.__default
                while i > 0:
                    ret = self.__fn(ret, self.__bit[i])
                    i -= i & -i
                return ret
        val_to_idx = {x: i for i, x in enumerate(sorted({x - i for i, x in enumerate(nums)}))}
        bit = BIT(len(val_to_idx), default=NEG_INF, fn=max)
        for i, x in enumerate(nums):
            v = max(bit.query(val_to_idx[x - i]), 0) + x
            bit.update(val_to_idx[x - i], v)
        return bit.query(len(val_to_idx) - 1)

def function(nums):
    return Solution().maxBalancedSubsequenceSum(nums=nums)

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
