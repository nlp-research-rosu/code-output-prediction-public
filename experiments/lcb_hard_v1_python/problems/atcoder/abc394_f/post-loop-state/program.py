import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
sys.setrecursionlimit(1000000)
INF_NEG = -10 ** 9

def solve() -> None:
    it = iter(sys.stdin.read().strip().split())
    N = int(next(it))
    adj = [[] for _ in range(N)]
    for _ in range(N - 1):
        a = int(next(it)) - 1
        b = int(next(it)) - 1
        adj[a].append(b)
        adj[b].append(a)
    dp0 = [1] * N
    dp1 = [INF_NEG] * N

    def dfs1(v: int, parent: int) -> None:
        child_vals = []
        for to in adj[v]:
            if to == parent:
                continue
            dfs1(to, v)
            best = max(dp0[to], dp1[to])
            child_vals.append(best)
        if len(child_vals) >= 3:
            child_vals.sort(reverse=True)
            dp1[v] = 1 + child_vals[0] + child_vals[1] + child_vals[2]
        else:
            dp1[v] = INF_NEG
    dfs1(0, -1)
    answer = -1

    def dfs2(v: int, parent: int, up_contrib: int) -> None:
        nonlocal answer
        neigh = []
        for to in adj[v]:
            if to == parent:
                continue
            best = max(dp0[to], dp1[to])
            neigh.append((to, best))
        if parent != -1:
            neigh.append((parent, up_contrib))
        if len(neigh) >= 4:
            vals = [c for _, c in neigh]
            vals.sort(reverse=True)
            cand = 1 + sum(vals[:4])
            if cand > answer:
                answer = cand
        vals_sorted = sorted([c for _, c in neigh], reverse=True)
        top4 = vals_sorted[:4]
        sum3 = sum(top4[:3]) if len(top4) >= 3 else INF_NEG
        for nb, val in neigh:
            if len(vals_sorted) < 3:
                internal = INF_NEG
            else:
                cnt_in_top3 = 0
                for i in range(3):
                    _lcb_count[0] += 1
                    if i < len(top4) and top4[i] == val:
                        cnt_in_top3 += 1
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'i': i, 'nb': nb, 'neigh': neigh, 'parent': parent, 'sum3': sum3, 'top4': top4, 'up_contrib': up_contrib, 'v': v, 'val': val, 'vals_sorted': vals_sorted}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if cnt_in_top3 == 0:
                    sum_wo = sum3
                else:
                    replacement = top4[3] if len(top4) >= 4 else INF_NEG
                    sum_wo = sum3 - val + replacement
                internal = 1 + sum_wo if sum_wo != INF_NEG else INF_NEG
            contrib = max(1, internal)
            if nb != parent:
                dfs2(nb, v, contrib)
    dfs2(0, -1, INF_NEG)
    print(answer)
if __name__ == '__main__':
    solve()
