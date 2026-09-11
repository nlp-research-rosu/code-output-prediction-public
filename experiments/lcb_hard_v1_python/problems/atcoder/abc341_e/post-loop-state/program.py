"""https://atcoder.jp/contests/practice2/submissions/21246566 より引用"""
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.readline

class SegTree:

    def __init__(self, op, e, n, v=None):
        self._n = n
        self._op = op
        self._e = e
        self._log = (n - 1).bit_length()
        self._size = 1 << self._log
        self._d = [self._e()] * (self._size << 1)
        if v is not None:
            for i in range(self._n):
                self._d[self._size + i] = v[i]
            for i in range(self._size - 1, 0, -1):
                self._d[i] = self._op(self._d[i << 1], self._d[i << 1 | 1])

    def set(self, p, x):
        p += self._size
        self._d[p] = x
        while p:
            self._d[p >> 1] = self._op(self._d[p], self._d[p ^ 1])
            p >>= 1

    def get(self, p):
        return self._d[p + self._size]

    def prod(self, l, r):
        sml, smr = (self._e(), self._e())
        l += self._size
        r += self._size
        while l < r:
            if l & 1:
                sml = self._op(sml, self._d[l])
                l += 1
            if r & 1:
                r -= 1
                smr = self._op(self._d[r], smr)
            l >>= 1
            r >>= 1
        return self._op(sml, smr)

    def all_prod(self):
        return self._d[1]

    def max_right(self, l, f):
        if l == self._n:
            return self._n
        l += self._size
        sm = self._e()
        while True:
            while l % 2 == 0:
                l >>= 1
            if not f(self._op(sm, self._d[l])):
                while l < self._size:
                    l <<= 1
                    if f(self._op(sm, self._d[l])):
                        sm = self._op(sm, self._d[l])
                        l += 1
                return l - self._size
            sm = self._op(sm, self._d[l])
            l += 1
            if l & -l == l:
                break
        return self._n

def op(x, y):
    return x + y

def e():
    return 0
n, q = map(int, input().split())
s = list(input())
v = [0] * (n - 1)
for i in range(n - 1):
    if s[i] == s[i + 1]:
        v[i] = 1
    else:
        v[i] = 0
seg = SegTree(op, e, n - 1, v)
k, l, r = ([0] * q, [0] * q, [0] * q)
for i in range(q):
    _lcb_count[0] += 1
    k[i], l[i], r[i] = map(int, input().split())
    l[i] -= 1
    r[i] -= 1
    if k[i] == 1:
        l[i] -= 1
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'k': k, 'l': l, 'r': r}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
for i in range(q):
    if k[i] == 1:
        if l[i] >= 0:
            seg.set(l[i], not seg.get(l[i]))
        if r[i] < n - 1:
            seg.set(r[i], not seg.get(r[i]))
    if k[i] == 2:
        print('No') if seg.prod(l[i], r[i]) else print('Yes')
