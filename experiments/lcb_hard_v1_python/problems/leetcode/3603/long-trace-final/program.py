import json, sys

class Solution(object):

    def findAnswer(self, parent, s):

        def manacher(s):
            s = '^#' + '#'.join(s) + '#$'
            P = [0] * len(s)
            C, R = (0, 0)
            for i in list(range(1, len(s) - 1)):
                i_mirror = 2 * C - i
                if R > i:
                    P[i] = min(R - i, P[i_mirror])
                while s[i + 1 + P[i]] == s[i - 1 - P[i]]:
                    P[i] += 1
                if i + P[i] > R:
                    C, R = (i, i + P[i])
            return P

        def iter_dfs(u):
            cnt = 0
            curr = []
            lookup = [None] * len(adj)
            stk = [(1, (0,))]
            while stk:
                step, args = stk.pop()
                if step == 1:
                    u = args[0]
                    stk.append((2, (u, cnt)))
                    for v in reversed(adj[u]):
                        stk.append((1, (v,)))
                elif step == 2:
                    u, left = args
                    curr.append(s[u])
                    lookup[u] = (left, cnt)
                    cnt += 1
            return (curr, lookup)
        adj = [[] for _ in list(range(len(parent)))]
        for v in list(range(1, len(parent))):
            adj[parent[v]].append(v)
        curr, lookup = iter_dfs(0)
        P = manacher(curr)
        return [P[(2 * (left + 1) + 2 * (right + 1)) // 2] >= right - left + 1 for left, right in lookup]

def function(parent, s):
    return Solution().findAnswer(parent=parent, s=s)

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
        if isinstance(value, dict) and all(name in value for name in names):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError("input argument count does not match the solution signature")
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('parent', 's'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
