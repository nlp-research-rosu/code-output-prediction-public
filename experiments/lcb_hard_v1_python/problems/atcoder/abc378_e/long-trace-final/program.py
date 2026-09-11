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

class PointAddRangeSum:

    def __init__(self, n: int, initial=0) -> None:
        """index from 1 to n"""
        self.n = n
        self.t = [initial] * (self.n + 1)
        return

    def _lowest_bit(self, i: int) -> int:
        assert 1 <= i <= self.n
        return i & -i

    def _pre_sum(self, i: int) -> int:
        """index start from 1 and the prefix sum of nums[:i] which is 0-index"""
        assert 0 <= i < self.n
        i += 1
        val = 0
        while i:
            val += self.t[i]
            i -= self._lowest_bit(i)
        return val

    def build(self, nums) -> None:
        """initialize the tree array"""
        assert len(nums) == self.n
        pre = [0] * (self.n + 1)
        for i in range(self.n):
            pre[i + 1] = pre[i] + nums[i]
            self.t[i + 1] = pre[i + 1] - pre[i + 1 - self._lowest_bit(i + 1)]
        return

    def get(self):
        """get the original nums sometimes for debug"""
        nums = [self._pre_sum(i) for i in range(self.n)]
        for i in range(self.n - 1, 0, -1):
            nums[i] -= nums[i - 1]
        return nums

    def point_add(self, i: int, val: int) -> None:
        """index start from 1 and the value val can be any inter including positive and negative number"""
        assert 0 <= i < self.n
        i += 1
        while i < len(self.t):
            self.t[i] += val
            i += self._lowest_bit(i)
        return

    def range_sum(self, x: int, y: int) -> int:
        assert 0 <= x <= y < self.n
        '0-index'
        res = self._pre_sum(y) - self._pre_sum(x - 1) if x else self._pre_sum(y)
        return res

    def bisect_right(self, w):
        x, k = (0, 1)
        while k * 2 <= self.n:
            k *= 2
        while k > 0:
            if x + k <= self.n and self.t[x + k] <= w:
                w -= self.t[x + k]
                x += k
            k //= 2
        assert 0 <= x <= self.n
        return x

def abc_378e():
    ac = FastIO()
    n, m = ac.read_list_ints()
    nums = ac.read_list_ints()
    tree = PointAddRangeSum(m + 1)
    tree_cnt = PointAddRangeSum(m + 1)
    ans = pre = 0
    tree_cnt.point_add(0, 1)
    for i in range(n):
        pre += nums[i]
        pre %= m
        low = pre * tree_cnt.range_sum(0, pre) - tree.range_sum(0, pre)
        ans += low
        high = tree_cnt.range_sum(pre + 1, m) * (m + pre) - tree.range_sum(pre + 1, m)
        ans += high
        tree.point_add(pre, pre)
        tree_cnt.point_add(pre, 1)
    ac.st(ans)
    return
abc_378e()
