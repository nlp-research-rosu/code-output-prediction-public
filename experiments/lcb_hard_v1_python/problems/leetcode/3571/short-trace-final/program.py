import json
import sys

import bisect

import bisect

class Solution(object):

    def maxPathLength(self, coordinates, k):
        """
        :type coordinates: List[List[int]]
        :type k: int
        :rtype: int
        """

        def longest_increasing_subsequence(arr):
            result = []
            for x in arr:
                i = bisect.bisect_left(result, x)
                if i == len(result):
                    result.append(x)
                else:
                    result[i] = x
            return len(result)
        target = coordinates[k]
        coordinates.sort(key=lambda x: (x[0], -x[1]))
        left, right = ([], [])
        for x, y in coordinates:
            if x < target[0] and y < target[1]:
                left.append(y)
            elif x > target[0] and y > target[1]:
                right.append(y)
        return longest_increasing_subsequence(left) + 1 + longest_increasing_subsequence(right)

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
    data = _read_lcb_input(('coordinates', 'k'))
    result = Solution().maxPathLength(data['coordinates'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
