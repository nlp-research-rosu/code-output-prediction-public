import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import decimal
import math
import random
import sys
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import cmp_to_key, lru_cache
from heapq import heapify, heappop, heappush

class FastIO:

    @staticmethod
    def read_int():
        return int(sys.stdin.readline().rstrip())

    @staticmethod
    def read_list_ints():
        return list(map(int, sys.stdin.readline().rstrip().split()))

    @staticmethod
    def read_list_ints_minus_one():
        return [int(value) - 1 for value in sys.stdin.readline().rstrip().split()]

    @staticmethod
    def read_str():
        return sys.stdin.readline().rstrip()

    @staticmethod
    def st(value):
        print(value)

    @staticmethod
    def lst(values):
        print(*values)

    @staticmethod
    def yes():
        print('Yes')

    @staticmethod
    def no():
        print('No')

    @staticmethod
    def accumulate(values):
        prefix = [0]
        for value in values:
            prefix.append(prefix[-1] + value)
        return prefix

class PreFixSumMatrix:

    def __init__(self, mat):
        self.mat = mat
        self.m, self.n = (len(mat), len(mat[0]))
        self.pre = [[0] * (self.n + 1) for _ in range(self.m + 1)]
        for i in range(self.m):
            for j in range(self.n):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'mat': mat, 'self.pre': self.pre}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                self.pre[i + 1][j + 1] = self.pre[i][j + 1] + self.pre[i + 1][j] - self.pre[i][j] + mat[i][j]
        return

    def query(self, xa: int, ya: int, xb: int, yb: int) -> int:
        """left up corner is (xa, ya) and right down corner is (xb, yb)"""
        assert 0 <= xa <= xb <= self.m - 1
        assert 0 <= ya <= yb <= self.n - 1
        return self.pre[xb + 1][yb + 1] - self.pre[xb + 1][ya] - self.pre[xa][yb + 1] + self.pre[xa][ya]

def abc_331d():
    ac = FastIO()
    n, q = ac.read_list_ints()
    grid = []
    for i in range(n):
        grid.append([int(w == 'B') for w in ac.read_str()])
    pre = PreFixSumMatrix(grid)

    def check(x, y):
        aa = x // n
        bb = y // n
        res = aa * bb * pre.query(0, 0, n - 1, n - 1)
        if x % n:
            block = pre.query(0, 0, x % n - 1, n - 1)
            res += block * bb
            if y % n:
                res += pre.query(0, 0, x % n - 1, y % n - 1)
        if y % n:
            block = pre.query(0, 0, n - 1, y % n - 1)
            res += block * aa
        return res
    for _ in range(q):
        a, b, c, d = ac.read_list_ints()
        ans = check(c + 1, d + 1) - check(c + 1, b) - check(a, d + 1) + check(a, b)
        ac.st(ans)
    return
abc_331d()
