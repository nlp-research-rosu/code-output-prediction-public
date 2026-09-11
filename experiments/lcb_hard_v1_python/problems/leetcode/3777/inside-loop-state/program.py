import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
import collections
import collections

class Solution(object):

    def maxProduct(self, nums, k, limit):
        """
        :type nums: List[int]
        :type k: int
        :type limit: int
        :rtype: int
        """
        total = sum(nums)
        if k > total or k < -total:
            return -1
        dp = collections.defaultdict(set)
        for x in nums:
            new_dp = collections.defaultdict(set, {k: set(v) for k, v in dp.items()})
            new_dp[1, x].add(min(x, limit + 1))
            for (p, total), products in dp.items():
                new_state = (p ^ 1, total + (x if p == 0 else -x))
                for v in products:
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'k': k, 'len(dp)': len(dp), 'len(products)': len(products), 'limit': limit, 'new_state': new_state, 'p': p, 'sorted(products)': sorted(products), 'total': total, 'v': v, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    new_dp[new_state].add(min(v * x, limit + 1))
            dp = new_dp
        result = -1
        for (p, total), products in dp.items():
            if total != k:
                continue
            for v in products:
                if v <= limit:
                    result = max(result, v)
        return result

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
    data = _read_lcb_input(('nums', 'k', 'limit'))
    result = Solution().maxProduct(data['nums'], data['k'], data['limit'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
