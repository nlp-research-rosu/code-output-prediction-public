import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

class BIT:
    """Fenwick tree for frequencies, 0‑based indices"""

    def __init__(self, n):
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, idx, delta):
        """increase position idx (0‑based) by delta"""
        i = idx + 1
        while i <= self.n:
            self.bit[i] += delta
            i += i & -i

    def sum(self, idx):
        """prefix sum of [0, idx)   (idx may be 0)"""
        s = 0
        i = idx
        while i:
            s += self.bit[i]
            i -= i & -i
        return s

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    N = int(next(it))
    M = int(next(it))
    A = [int(next(it)) for _ in range(N)]
    bit = BIT(M)
    inv0 = 0
    for i, v in enumerate(A):
        less_equal = bit.sum(v + 1)
        inv0 += i - less_equal
        bit.add(v, 1)
    cnt = [0] * M
    posSum = [0] * M
    for pos, v in enumerate(A, start=1):
        _lcb_count[0] += 1
        cnt[v] += 1
        posSum[v] += pos
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'cnt': cnt, 'inv0': inv0, 'pos': pos, 'posSum': posSum, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    ans = [0] * M
    cur = inv0
    ans[0] = cur
    for k in range(0, M - 1):
        v = (M - 1 - k) % M
        delta = 2 * posSum[v] - cnt[v] * (N + 1)
        cur += delta
        ans[k + 1] = cur
    out = '\n'.join((str(x) for x in ans))
    sys.stdout.write(out)
if __name__ == '__main__':
    solve()
