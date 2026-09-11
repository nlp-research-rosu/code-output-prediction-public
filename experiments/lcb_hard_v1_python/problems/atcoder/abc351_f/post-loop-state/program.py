import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import random
from types import GeneratorType
import bisect
import io, os
from bisect import *
from collections import *
from contextlib import redirect_stdout
from itertools import *
from array import *
from functools import lru_cache, reduce
from heapq import *
from math import sqrt, gcd, inf
RI = lambda: map(int, sys.stdin.buffer.readline().split())
RS = lambda: map(bytes.decode, sys.stdin.buffer.readline().strip().split())
RILST = lambda: list(RI())
DEBUG = lambda *x: sys.stderr.write(f'{str(x)}\n')
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRS8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
RANDOM = random.randrange(2 ** 62)
MOD = 10 ** 9 + 7
PROBLEM = '\n'

class BinIndexTree:
    """    PURQ的最经典树状数组，每个基础操作的复杂度都是logn；如果需要查询每个位置的元素，可以打开self.a    """

    def __init__(self, size_or_nums):
        if isinstance(size_or_nums, int):
            self.size = size_or_nums
            self.c = [0 for _ in range(self.size + 5)]
        else:
            self.size = len(size_or_nums)
            self.c = [0 for _ in range(self.size + 5)]
            for i, v in enumerate(size_or_nums):
                self.add_point(i + 1, v)

    def add_point(self, i, v):
        while i <= self.size:
            self.c[i] += v
            i += i & -i

    def sum_interval(self, l, r):
        return self.sum_prefix(r) - self.sum_prefix(l - 1)

    def sum_prefix(self, i):
        s = 0
        while i >= 1:
            s += self.c[i]
            i &= i - 1
        return s

    def min_right(self, i):
        """寻找[i,size]闭区间上第一个正数(不为0的数),注意i是1-indexed。若没有返回size+1;复杂度O(lgnlgn)"""
        p = self.sum_prefix(i)
        if i == 1:
            if p > 0:
                return i
        elif p > self.sum_prefix(i - 1):
            return i
        l, r = (i, self.size + 1)
        while l + 1 < r:
            mid = l + r >> 1
            if self.sum_prefix(mid) > p:
                r = mid
            else:
                l = mid
        return r

def solve():
    n, = RI()
    a = RILST()
    h = sorted(set(a))
    m = len(h)
    cnt = BinIndexTree(m)
    s = BinIndexTree(m)
    for v in a:
        b = bisect_left(h, v)
        cnt.add_point(b + 1, 1)
        s.add_point(b + 1, v)
    ans = 0
    for v in a:
        _lcb_count[0] += 1
        b = bisect_left(h, v)
        cnt.add_point(b + 1, -1)
        s.add_point(b + 1, -v)
        ans += s.sum_interval(b + 2, m) - cnt.sum_interval(b + 2, m) * v
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'b': b, 'cnt.c': cnt.c, 's.c': s.c, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(ans)
if __name__ == '__main__':
    t = 0
    if t:
        t, = RI()
        for _ in range(t):
            solve()
    else:
        solve()
