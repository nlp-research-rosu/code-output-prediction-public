import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
import bisect

class Solution(object):

    def maximumWeight(self, intervals):
        K = 4
        lookup = {}
        for i, (l, r, w) in enumerate(intervals):
            if (r, l, w) not in lookup:
                lookup[r, l, w] = i
        sorted_intervals = sorted(lookup.keys(), key=lambda x: x[0])
        dp = [[[0, []] for _ in list(range(K + 1))] for _ in list(range(len(sorted_intervals) + 1))]
        for i in list(range(len(dp) - 1)):
            j = bisect.bisect_right(sorted_intervals, (sorted_intervals[i][1], 0, 0)) - 1
            idx = lookup[sorted_intervals[i]]
            for k in list(range(1, len(dp[i]))):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'dp[i][k]': dp[i][k], 'dp[j+1][k-1]': dp[j + 1][k - 1], 'i': i, 'idx': idx, 'j': j, 'k': k, 'new_dp': new_dp, 'sorted_intervals[i]': sorted_intervals[i]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                new_dp = [dp[j + 1][k - 1][0] - sorted_intervals[i][2], dp[j + 1][k - 1][1][:]]
                bisect.insort(new_dp[1], idx)
                dp[i + 1][k] = min(dp[i][k], new_dp)
        return dp[len(sorted_intervals)][K][1]

def function(intervals):
    return Solution().maximumWeight(intervals=intervals)

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
    data = _read_lcb_input(('intervals',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
