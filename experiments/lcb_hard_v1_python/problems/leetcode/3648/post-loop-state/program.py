import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from typing import List
from math import inf

class Solution:

    def maxCollectedFruits(self, fruits: List[List[int]]) -> int:
        n = len(fruits)
        f = [[-inf] * n for _ in range(n)]
        f[0][n - 1] = fruits[0][n - 1]
        for i in range(1, n):
            for j in range(i + 1, n):
                f[i][j] = max(f[i - 1][j], f[i - 1][j - 1]) + fruits[i][j]
                if j + 1 < n:
                    f[i][j] = max(f[i][j], f[i - 1][j + 1] + fruits[i][j])
        f[n - 1][0] = fruits[n - 1][0]
        for j in range(1, n):
            for i in range(j + 1, n):
                _lcb_count[0] += 1
                f[i][j] = max(f[i][j - 1], f[i - 1][j - 1]) + fruits[i][j]
                if i + 1 < n:
                    f[i][j] = max(f[i][j], f[i + 1][j - 1] + fruits[i][j])
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'f[i-1][j-1]': f[i - 1][j - 1], 'f[i][j-1]': f[i][j - 1], 'fruits[i][j]': fruits[i][j], 'i': i, 'j': j, 'n': n}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
        return sum((fruits[i][i] for i in range(n))) + f[n - 2][n - 1] + f[n - 1][n - 2]

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
    data = _read_lcb_input(('fruits',))
    result = Solution().maxCollectedFruits(data['fruits'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
