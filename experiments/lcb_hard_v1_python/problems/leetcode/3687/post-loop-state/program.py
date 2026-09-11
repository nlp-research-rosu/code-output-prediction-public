import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
import collections

class Solution(object):

    def longestSpecialPath(self, edges, nums):

        def iter_dfs():
            result = [float('inf')] * 2
            lookup = collections.defaultdict(lambda: -1)
            prefix = [0]
            stk = [(1, (0, -1, 0, -1))]
            while stk:
                _lcb_count[0] += 1
                step, args = stk.pop()
                if step == 1:
                    u, p, d, left = args
                    prev_d, lookup[nums[u] - 1] = (lookup[nums[u] - 1], d)
                    left = max(left, prev_d)
                    result = min(result, [-(prefix[d - 1 + 1] - prefix[left + 1]), d - left])
                    stk.append((4, (u, prev_d)))
                    stk.append((2, (u, p, d, left, 0)))
                elif step == 2:
                    u, p, d, left, i = args
                    if i == len(adj[u]):
                        continue
                    stk.append((2, (u, p, d, left, i + 1)))
                    v, l = adj[u][i]
                    if v == p:
                        continue
                    prefix.append(prefix[-1] + l)
                    stk.append((3, None))
                    stk.append((1, (v, u, d + 1, left)))
                elif step == 3:
                    prefix.pop()
                elif step == 4:
                    u, prev_d = args
                    lookup[nums[u] - 1] = prev_d
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'args': args, 'd': d, 'lookup': lookup, 'p': p, 'prefix': prefix, 'result': result, 'step': step}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            return [-result[0], result[1]]
        adj = [[] for _ in list(range(len(nums)))]
        for u, v, l in edges:
            adj[u].append((v, l))
            adj[v].append((u, l))
        return iter_dfs()

def function(edges, nums):
    return Solution().longestSpecialPath(edges=edges, nums=nums)

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
    data = _read_lcb_input(('edges', 'nums'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
