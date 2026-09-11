import json
import sys

class Solution:

    def minimumDistance(self, points):
        if not points or not isinstance(points[0], list):
            return 0

        def spread(excluded):
            min_sum = min_diff = float('inf')
            max_sum = max_diff = -float('inf')
            for index, (x, y) in enumerate(points):
                if index == excluded:
                    continue
                min_sum = min(min_sum, x + y)
                max_sum = max(max_sum, x + y)
                min_diff = min(min_diff, x - y)
                max_diff = max(max_diff, x - y)
            return max(max_sum - min_sum, max_diff - min_diff)
        candidates = set()
        for key in (lambda p: p[0] + p[1], lambda p: p[0] - p[1]):
            candidates.add(min(range(len(points)), key=lambda i: key(points[i])))
            candidates.add(max(range(len(points)), key=lambda i: key(points[i])))
        return min((spread(index) for index in candidates))

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
    data = _read_lcb_input(('points',))
    result = Solution().minimumDistance(data['points'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
