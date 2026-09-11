import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from typing import List
from functools import cache

class Solution:

    def lenOfVDiagonal(self, grid: List[List[int]]) -> int:

        @cache
        def dfs(i: int, j: int, k: int, cnt: int) -> int:
            x, y = (i + dirs[k], j + dirs[k + 1])
            target = 2 if grid[i][j] == 1 else 2 - grid[i][j]
            if not 0 <= x < m or not 0 <= y < n or grid[x][y] != target:
                return 0
            res = dfs(x, y, k, cnt)
            if cnt > 0:
                res = max(res, dfs(x, y, (k + 1) % 4, 0))
            return 1 + res
        m, n = (len(grid), len(grid[0]))
        dirs = (1, 1, -1, -1, 1)
        ans = 0
        for i, row in enumerate(grid):
            for j, x in enumerate(row):
                if x == 1:
                    for k in range(4):
                        _lcb_count[0] += 1
                        if _lcb_count[0] == 502:
                            _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'dirs': dirs, 'grid': grid, 'i': i, 'j': j, 'k': k, 'row': row, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                            raise SystemExit
                        ans = max(ans, dfs(i, j, k, 1) + 1)
        return ans

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
    data = _read_lcb_input(('grid',))
    result = Solution().lenOfVDiagonal(data['grid'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
