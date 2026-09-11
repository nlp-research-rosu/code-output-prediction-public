import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class UnionFind(object):

    def __init__(self, n):
        self.set = list(range(n))
        self.rank = [0] * n

    def find_set(self, x):
        stk = []
        while self.set[x] != x:
            stk.append(x)
            x = self.set[x]
        while stk:
            self.set[stk.pop()] = x
        return x

    def union_set(self, x, y):
        x, y = (self.find_set(x), self.find_set(y))
        if x == y:
            return False
        if self.rank[x] > self.rank[y]:
            x, y = (y, x)
        self.set[x] = self.set[y]
        if self.rank[x] == self.rank[y]:
            self.rank[y] += 1
        return True

class Solution(object):

    def countComponents(self, nums, threshold):
        uf = UnionFind(threshold)
        lookup = [-1] * threshold
        result = len(nums)
        for x in nums:
            if x - 1 >= threshold:
                continue
            for i in list(range(x, threshold + 1, x)):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'lookup': lookup, 'result': result, 'threshold': threshold, 'uf.set': uf.set, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if lookup[i - 1] == -1:
                    lookup[i - 1] = x - 1
                    continue
                if uf.union_set(lookup[i - 1], x - 1):
                    result -= 1
                if i == x:
                    break
        return result

def function(nums, threshold):
    return Solution().countComponents(nums=nums, threshold=threshold)

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
    data = _read_lcb_input(('nums', 'threshold'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
