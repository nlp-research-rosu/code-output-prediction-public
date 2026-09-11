import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def maxDistance(self, side, points, k):

        def binary_search_right(left, right, check):
            while left <= right:
                mid = left + (right - left) // 2
                if not check(mid):
                    right = mid - 1
                else:
                    left = mid + 1
            return right

        def check(d):
            intervals = [(0, 0, 1)]
            i = 0
            for right in list(range(1, len(p))):
                left, cnt = (right, 1)
                while i < len(intervals):
                    _lcb_count[0] += 1
                    l, r, c = intervals[i]
                    if p[right] - p[r] < d:
                        break
                    if p[l] + 4 * side - p[right] >= d:
                        if c + 1 >= cnt:
                            cnt = c + 1
                            left = l
                    i += 1
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'd': d, 'i': i, 'intervals': intervals, 'left': left, 'right': right}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                intervals.append((left, right, cnt))
            return max((x[2] for x in intervals)) >= k
        p = []
        for x, y in points:
            if x == 0:
                p.append(0 * side + y)
            elif y == side:
                p.append(1 * side + x)
            elif x == side:
                p.append(2 * side + (side - y))
            else:
                p.append(3 * side + (side - x))
        p.sort()
        return binary_search_right(1, 4 * side // k, check)

def function(side, points, k):
    return Solution().maxDistance(side=side, points=points, k=k)

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
    data = _read_lcb_input(('side', 'points', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
