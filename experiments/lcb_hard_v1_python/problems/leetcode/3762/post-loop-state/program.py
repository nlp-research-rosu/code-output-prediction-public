import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def maxScore(self, points, m):

        def ceil_divide(a, b):
            return (a + b - 1) // b

        def binary_search_right(left, right, check):
            while left <= right:
                mid = left + (right - left) // 2
                if not check(mid):
                    right = mid - 1
                else:
                    left = mid + 1
            return right

        def check(x):
            cnt = prev = 0
            for i in list(range(len(points))):
                _lcb_count[0] += 1
                remain = ceil_divide(x, points[i]) - prev
                if remain >= 1:
                    prev = remain - 1
                    cnt += 2 * remain - 1
                elif i != len(points) - 1:
                    prev = 0
                    cnt += 1
                if cnt > m:
                    return False
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'm': m, 'points': points, 'prev': prev, 'remain': remain, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            return True
        return binary_search_right(1, max(points) * m, check)

def function(points, m):
    return Solution().maxScore(points=points, m=m)

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
    data = _read_lcb_input(('points', 'm'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
