import json
import sys

class Solution:

    def canTraverseAllPairs(self, nums):
        if len(nums) == 1:
            return True
        if 1 in nums:
            return False
        parent = list(range(len(nums)))
        size = [1] * len(nums)

        def find(node):
            while parent[node] != node:
                parent[node] = parent[parent[node]]
                node = parent[node]
            return node

        def union(first, second):
            first = find(first)
            second = find(second)
            if first == second:
                return
            if size[first] < size[second]:
                first, second = (second, first)
            parent[second] = first
            size[first] += size[second]
        owner = {}
        for index, number in enumerate(nums):
            factor = 2
            value = number
            while factor * factor <= value:
                if value % factor == 0:
                    if factor in owner:
                        union(index, owner[factor])
                    else:
                        owner[factor] = index
                    while value % factor == 0:
                        value //= factor
                factor += 1
            if value > 1:
                if value in owner:
                    union(index, owner[value])
                else:
                    owner[value] = index
        root = find(0)
        return all((find(index) == root for index in range(1, len(nums))))

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
    result = Solution().canTraverseAllPairs(data['nums'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
