import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
MOD = 998244353

def solve() -> None:
    it = iter(sys.stdin.read().strip().split())
    N = int(next(it))
    M = int(next(it))
    S = next(it)
    max_mask = 1 << N
    next_mask = [[0] * 26 for _ in range(max_mask)]
    for mask in range(max_mask):
        L = [0] * (N + 1)
        cnt = 0
        for i in range(1, N + 1):
            if mask & 1 << i - 1:
                cnt += 1
            L[i] = cnt
        for ci in range(26):
            c = chr(ord('a') + ci)
            L2 = [0] * (N + 1)
            for i in range(1, N + 1):
                best = L[i] if L[i] > L2[i - 1] else L2[i - 1]
                if S[i - 1] == c:
                    cand = L[i - 1] + 1
                    if cand > best:
                        best = cand
                L2[i] = best
            nm = 0
            for i in range(1, N + 1):
                if L2[i] == L2[i - 1] + 1:
                    nm |= 1 << i - 1
            next_mask[mask][ci] = nm
    dp = [0] * max_mask
    dp[0] = 1
    for _ in range(M):
        ndp = [0] * max_mask
        for mask, cur in enumerate(dp):
            if cur == 0:
                continue
            trans = next_mask[mask]
            for nm in trans:
                _lcb_count[0] += 1
                ndp[nm] += cur
                if ndp[nm] >= MOD:
                    ndp[nm] -= MOD
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'_': _, 'cur': cur, 'dp': dp, 'mask': mask, 'ndp': ndp, 'nm': nm, 'trans': trans}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
        dp = ndp
    ans = [0] * (N + 1)
    for mask, val in enumerate(dp):
        if val:
            k = mask.bit_count()
            ans[k] += val
            if ans[k] >= MOD:
                ans[k] -= MOD
    print(' '.join((str(x % MOD) for x in ans)))
if __name__ == '__main__':
    solve()
