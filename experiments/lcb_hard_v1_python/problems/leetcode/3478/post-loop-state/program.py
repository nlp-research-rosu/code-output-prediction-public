import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
import sys
sys.setrecursionlimit(1000000)
from typing import List

class Solution:

    def canReachCorner(self, xCorner: int, yCorner: int, circles: List[List[int]]) -> bool:

        def in_circle(x: int, y: int, cx: int, cy: int, r: int) -> int:
            return (x - cx) ** 2 + (y - cy) ** 2 <= r ** 2

        def cross_left_top(cx: int, cy: int, r: int) -> bool:
            a = abs(cx) <= r and 0 <= cy <= yCorner
            b = abs(cy - yCorner) <= r and 0 <= cx <= xCorner
            return a or b

        def cross_right_bottom(cx: int, cy: int, r: int) -> bool:
            a = abs(cx - xCorner) <= r and 0 <= cy <= yCorner
            b = abs(cy) <= r and 0 <= cx <= xCorner
            return a or b

        def dfs(i: int) -> bool:
            x1, y1, r1 = circles[i]
            if cross_right_bottom(x1, y1, r1):
                return True
            vis[i] = True
            for j, (x2, y2, r2) in enumerate(circles):
                _lcb_count[0] += 1
                if vis[j] or not (x1 - x2) ** 2 + (y1 - y2) ** 2 <= (r1 + r2) ** 2:
                    continue
                if x1 * r2 + x2 * r1 < (r1 + r2) * xCorner and y1 * r2 + y2 * r1 < (r1 + r2) * yCorner and dfs(j):
                    return True
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'len(circles)': len(circles), 'r1': r1, 'r2': r2, 'sum(vis)': sum(vis), 'vis': vis, 'x1': x1, 'x2': x2, 'y1': y1, 'y2': y2}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            return False
        vis = [False] * len(circles)
        for i, (x, y, r) in enumerate(circles):
            if in_circle(0, 0, x, y, r) or in_circle(xCorner, yCorner, x, y, r):
                return False
            if not vis[i] and cross_left_top(x, y, r) and dfs(i):
                return False
        return True

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
    data = _read_lcb_input(('xCorner', 'yCorner', 'circles'))
    result = Solution().canReachCorner(data['xCorner'], data['yCorner'], data['circles'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
