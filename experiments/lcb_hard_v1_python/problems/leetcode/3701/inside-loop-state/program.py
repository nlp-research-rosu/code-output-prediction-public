import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def minCostGoodCaption(self, caption):
        L = 3
        n = len(caption)
        if n < L:
            return ''
        dp = [[[0] * 2 for _ in list(range(26))] for _ in list(range(n - L + 1))]
        mn = [[0] * 2 for _ in list(range(n - L + 1))]
        cap = list(map(lambda x: ord(x) - ord('a'), caption))
        for i in reversed(list(range(n - L + 1))):
            for j in list(range(26)):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'c': c, 'cap[i]': cap[i], 'curr': curr, 'dp[i][j]': dp[i][j], 'i': i, 'j': j, 'mn': mn, 'n': n}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if i == n - L:
                    dp[i][j][:] = [sum((abs(cap[k] - j) for k in list(range(i, i + L)))), L]
                    continue
                dp[i][j][:] = [dp[i + 1][j][0] + abs(cap[i] - j), 1]
                if i + L < n - 2:
                    curr, c = mn[i + L]
                    curr += sum((abs(cap[k] - j) for k in list(range(i, i + L))))
                    if curr < dp[i][j][0] or (curr == dp[i][j][0] and c < j):
                        dp[i][j][:] = [curr, L]
            mn[i] = min(([dp[i][j][0], j] for j in list(range(26))))
        result = []
        i, j, l = (0, mn[0][1], 1)
        while i != n:
            if l == L:
                j = mn[i][1]
            l = dp[i][j][1]
            result.append(chr(ord('a') + j) * l)
            i += l
        return ''.join(result)

def function(caption):
    return Solution().minCostGoodCaption(caption=caption)

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
    data = _read_lcb_input(('caption',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
