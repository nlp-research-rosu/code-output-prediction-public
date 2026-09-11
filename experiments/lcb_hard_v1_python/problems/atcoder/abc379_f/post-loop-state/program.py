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

class BinarySearch:

    def __init__(self):
        return

    @staticmethod
    def find_int_left(low: int, high: int, check) -> int:
        """find the minimum int x which make check true"""
        while low < high:
            mid = low + (high - low) // 2
            if check(mid):
                high = mid
            else:
                low = mid + 1
        return low

    @staticmethod
    def find_int_right(low: int, high: int, check) -> int:
        """find the maximum int x which make check true"""
        while low < high:
            mid = low + (high - low + 1) // 2
            if check(mid):
                low = mid
            else:
                high = mid - 1
        return high

    @staticmethod
    def find_float_left(low: float, high: float, check, error=1e-06) -> float:
        """find the minimum float x which make check true"""
        while low < high - error:
            mid = low + (high - low) / 2
            if check(mid):
                high = mid
            else:
                low = mid
        return low if check(low) else high

    @staticmethod
    def find_float_right(low: float, high: float, check, error=1e-06) -> float:
        """find the maximum float x which make check true"""
        while low < high - error:
            mid = low + (high - low) / 2
            if check(mid):
                low = mid
            else:
                high = mid
        return high if check(high) else low

class SparseTable:

    def __init__(self, lst, fun):
        """static range queries can be performed as long as the range_merge_to_disjoint fun satisfies monotonicity"""
        n = len(lst)
        self.bit = [0] * (n + 1)
        self.fun = fun
        self.n = n
        for i in range(2, n + 1):
            self.bit[i] = self.bit[i >> 1] + 1
        for i in range(n + 1):
            assert self.bit[i] == (i.bit_length() - 1 if i else i.bit_length())
        self.st = [[0] * n for _ in range(self.bit[-1] + 1)]
        self.st[0] = lst
        for i in range(1, self.bit[-1] + 1):
            for j in range(n - (1 << i) + 1):
                self.st[i][j] = fun(self.st[i - 1][j], self.st[i - 1][j + (1 << i - 1)])

    def query(self, left, right):
        """index start from 0"""
        assert 0 <= left <= right < self.n
        pos = self.bit[right - left + 1]
        return self.fun(self.st[pos][left], self.st[pos][right - (1 << pos) + 1])

    def bisect_right(self, left, val, initial):
        """index start from 0"""
        assert 0 <= left < self.n
        pos = left
        pre = initial
        for x in range(self.bit[-1], -1, -1):
            if pos + (1 << x) - 1 < self.n and self.fun(self.st[x][pos], pre) >= val:
                pre = self.fun(self.st[x][pos], pre)
                pos += 1 << x
        if pos > left:
            pos -= 1
        else:
            pre = self.st[0][left]
        assert left <= pos < self.n
        return (pos, pre)

    def bisect_right_length(self, left):
        """index start from 0"""
        assert 0 <= left < self.n
        pos = left
        pre = 0
        for x in range(self.bit[-1], -1, -1):
            if pos + (1 << x) - 1 < self.n and self.fun(self.st[x][pos], pre) > pos + (1 << x) - left:
                pre = self.fun(self.st[x][pos], pre)
                pos += 1 << x
        if pos == left and self.st[0][pos] == 1:
            return (True, pos)
        if pos < self.n and self.fun(pre, self.st[0][pos]) == pos + 1 - left:
            return (True, pos)
        return (False, pos)

def abc_379f():
    ac = FastIO()
    n, q = ac.read_list_ints()
    nums = ac.read_list_ints()
    queries = [[] for _ in range(n)]
    for i in range(q):
        ll, rr = ac.read_list_ints_minus_one()
        queries[rr].append(ll * q + i)
    st = SparseTable(nums, max)
    ans = [0] * q
    stack = []
    for i in range(n - 1, -1, -1):
        _lcb_count[0] += 1

        def check(xx):
            return nums[stack[xx]] >= ceil
        for val in queries[i]:
            ll, ind = (val // q, val % q)
            ceil = st.query(ll + 1, i)
            if stack and nums[stack[0]] >= ceil:
                j = BinarySearch().find_int_right(0, len(stack) - 1, check)
                ans[ind] = j + 1
        while stack and nums[stack[-1]] < nums[i]:
            stack.pop()
        stack.append(i)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'ceil': ceil, 'i': i, 'ind': ind, 'll': ll, 'stack': stack}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    for x in ans:
        ac.st(x)
    return
abc_379f()
