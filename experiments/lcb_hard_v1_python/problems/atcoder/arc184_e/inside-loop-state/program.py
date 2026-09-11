import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
MOD = 998244353
import sys
from collections import defaultdict

class Fenw:

    def __init__(self, size):
        self.n = size
        self.fw = [0] * (self.n + 2)

    def add(self, idx, delta):
        i = idx + 1
        while i <= self.n:
            self.fw[i] = (self.fw[i] + delta) % MOD
            i += i & -i

    def _sum(self, i):
        s = 0
        while i:
            s = (s + self.fw[i]) % MOD
            i -= i & -i
        return s

    def sum(self, l, r):
        if l > r:
            return 0
        res = self._sum(r + 1) - self._sum(l)
        res %= MOD
        if res < 0:
            res += MOD
        return res

def applyT(vec):
    s = 0
    res = []
    for bit in vec:
        s ^= bit
        res.append(s)
    return tuple(res)

def generate_orbit(vec, M):
    orbit = []
    seen = set()
    cur = vec
    while cur not in seen:
        seen.add(cur)
        orbit.append(cur)
        cur = applyT(cur)
    return orbit

def main():
    data = sys.stdin.read().splitlines()
    if not data:
        return
    n, m = map(int, data[0].split())
    vectors = []
    for i in range(1, 1 + n):
        vec = tuple(map(int, data[i].split()))
        vectors.append(vec)
    vector_occurrences = defaultdict(list)
    for idx, vec in enumerate(vectors, start=1):
        vector_occurrences[vec].append(idx)
    visited = set()
    ans = 0
    for vec in list(vector_occurrences.keys()):
        if vec in visited:
            continue
        orbit = generate_orbit(vec, m)
        d = len(orbit)
        rep = min(orbit)
        pos = orbit.index(rep)
        occ_list = []
        for vv in orbit:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'d': d, 'len(occ_list)': len(occ_list), 'len(orbit)': len(orbit), 'pos': pos, 'rep[:40]': rep[:40], 'vv[:40]': vv[:40]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if vv in vector_occurrences:
                idx_in_orbit = orbit.index(vv)
                index_val = (idx_in_orbit - pos) % d
                for input_idx in vector_occurrences[vv]:
                    occ_list.append((input_idx, index_val))
                visited.add(vv)
        visited.add(vec)
        occ_list.sort(key=lambda x: x[0], reverse=True)
        if d == 0:
            continue
        fenw_count = Fenw(d)
        fenw_sum = Fenw(d)
        for input_index, k in occ_list:
            total_count = fenw_count.sum(0, d - 1)
            total_sum = fenw_sum.sum(0, d - 1)
            count_less = fenw_count.sum(0, k - 1)
            cur = (total_sum - k * total_count + d * count_less) % MOD
            ans = (ans + cur) % MOD
            fenw_count.add(k, 1)
            fenw_sum.add(k, k)
    print(ans % MOD)
if __name__ == '__main__':
    main()
