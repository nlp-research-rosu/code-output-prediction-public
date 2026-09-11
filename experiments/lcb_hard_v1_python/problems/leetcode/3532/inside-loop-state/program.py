import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def timeTaken(self, edges):

        def topological_traversal():
            p = [-2] * len(adj)
            p[0] = -1
            topological_order = [0]
            for u in topological_order:
                for v in reversed(adj[u]):
                    if p[v] != -2:
                        continue
                    p[v] = u
                    topological_order.append(v)
            for u in reversed(topological_order):
                for v in adj[u]:
                    if v == p[u]:
                        continue
                    curr = [1 + int(v % 2 == 0) + dp[v][0][0], v]
                    for i in list(range(len(dp[u]))):
                        if curr > dp[u][i]:
                            curr, dp[u][i] = (dp[u][i], curr)

        def bfs():
            q = [(0, -1, 0)]
            while q:
                new_q = []
                for u, p, curr in q:
                    result[u] = max(dp[u][0][0], curr)
                    for v in adj[u]:
                        _lcb_count[0] += 1
                        if _lcb_count[0] == 502:
                            _lcb_sys.stdout.write(_lcb_json.dumps({'adj[u]': adj[u], 'curr': curr, 'dp[u]': dp[u], 'len(new_q)': len(new_q), 'p': p, 'q': q, 'result': result, 'u': u, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                            raise SystemExit
                        if v == p:
                            continue
                        new_q.append((v, u, 1 + int(u % 2 == 0) + max(dp[u][0][0] if dp[u][0][1] != v else dp[u][1][0], curr)))
                q = new_q
        adj = [[] for _ in list(range(len(edges) + 1))]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        dp = [[[0, -1] for _ in list(range(2))] for _ in list(range(len(edges) + 1))]
        topological_traversal()
        result = [0] * (len(edges) + 1)
        bfs()
        return result

def function(edges):
    return Solution().timeTaken(edges=edges)

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
    data = _read_lcb_input(('edges',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
