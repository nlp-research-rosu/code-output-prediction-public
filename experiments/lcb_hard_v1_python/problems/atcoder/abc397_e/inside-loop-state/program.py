import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
sys.setrecursionlimit(1000000)

def solve() -> None:
    it = iter(sys.stdin.read().strip().split())
    N = int(next(it))
    K = int(next(it))
    n = N * K
    g = [[] for _ in range(n)]
    for _ in range(n - 1):
        u = int(next(it)) - 1
        v = int(next(it)) - 1
        g[u].append(v)
        g[v].append(u)
    ok = True

    def dfs(v: int, parent: int) -> int:
        """return down(v) as defined in the editorial.
        0  → no unfinished path coming from the subtree of v
        >0 → length of the unique unfinished path (1 ≤ length < K)
        """
        nonlocal ok
        pending = []
        for to in g[v]:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'g': g, 'ok': ok, 'parent': parent, 'pending': pending, 'to': to, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if to == parent:
                continue
            child_len = dfs(to, v)
            if not ok:
                return 0
            if child_len > 0:
                pending.append(child_len)
        if len(pending) > 2:
            ok = False
            return 0
        if len(pending) == 2:
            a, b = pending
            if a + b + 1 != K:
                ok = False
                return 0
            return 0
        if len(pending) == 1:
            a = pending[0]
            if a + 1 > K:
                ok = False
                return 0
            if a + 1 == K:
                return 0
            else:
                return a + 1
        if K == 1:
            return 0
        else:
            return 1
    root_len = dfs(0, -1)
    if not ok:
        print('No')
        return
    if root_len == 0 or root_len == K:
        print('Yes')
    else:
        print('No')
if __name__ == '__main__':
    solve()
