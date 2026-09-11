import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
import collections

class Solution(object):

    def beautifulNumbers(self, l, r):

        def count(x):
            s = list(map(lambda x: ord(x) - ord('0'), str(x)))
            dp = [collections.defaultdict(int) for _ in list(range(2))]
            dp[1][1, 0] = 1
            for c in s:
                new_dp = [collections.defaultdict(int) for _ in list(range(2))]
                for b in list(range(2)):
                    for (mul, total), cnt in dp[b].items():
                        for x in list(range((c if b else 9) + 1)):
                            new_dp[b and x == c][mul * (1 if total == 0 == x else x), total + x] += cnt
                dp = new_dp
            result = 0
            for b in list(range(2)):
                for (mul, total), cnt in dp[b].items():
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'b': b, 'c': c, 'cnt': cnt, 'len(dp[b])': len(dp[b]), 'mul': mul, 'result': result, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    if total and mul % total == 0:
                        result += cnt
            return result
        return count(r) - count(l - 1)

def function(l, r):
    return Solution().beautifulNumbers(l=l, r=r)

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
    data = _read_lcb_input(('l', 'r'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
