import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce
import collections

class Solution(object):

    def countWinningSequences(self, s):
        MOD = 10 ** 9 + 7
        lookup = {x: i for i, x in enumerate('FWE')}
        dp = [collections.defaultdict(int) for _ in list(range(3))]
        for i, c in enumerate(s):
            new_dp = [collections.defaultdict(int) for _ in list(range(3))]
            x = lookup[c]
            for j in list(range(3)):
                diff = (j - x + 1) % 3 - 1
                if i == 0:
                    new_dp[j][diff] = 1
                    continue
                for k in list(range(3)):
                    if k == j:
                        continue
                    for v, c in dp[k].items():
                        _lcb_count[0] += 1
                        new_dp[j][v + diff] = (new_dp[j][v + diff] + c) % MOD
                    if _lcb_count[0] > 1000:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'c': c, 'diff': diff, 'dp': dp, 'i': i, 'j': j, 'k': k, 'new_dp': new_dp, 'v': v, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
            dp = new_dp
        return reduce(lambda accu, x: (accu + x) % MOD, (c for j in list(range(3)) for v, c in dp[j].items() if v >= 1), 0)

def function(s):
    return Solution().countWinningSequences(s=s)

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
    data = _read_lcb_input(('s',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
