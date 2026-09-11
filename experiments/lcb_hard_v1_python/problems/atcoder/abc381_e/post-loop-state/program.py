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
            _lcb_count[0] += 1
            prefix.append(prefix[-1] + value)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'prefix': prefix, 'value': value, 'values': values}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
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

def abc_381e():
    ac = FastIO()
    n, q = ac.read_list_ints()
    s = ac.read_str()
    pre = ac.accumulate([x == '/' for x in s])
    one = [i for i in range(n) if s[i] == '1']
    two = [i for i in range(n) if s[i] == '2']
    n1 = len(one)

    def check(x):
        if x == 0:
            return True
        if i1 + x - 1 >= n1 or j2 - x + 1 < 0:
            return False
        aa, bb = (one[i1 + x - 1], two[j2 - x + 1])
        return aa < bb and pre[bb] - pre[aa + 1] > 0
    for _ in range(q):
        ll, rr = ac.read_list_ints_minus_one()
        if pre[rr + 1] == pre[ll]:
            ac.st(0)
            continue
        i1 = bisect_left(one, ll)
        j2 = bisect_right(two, rr) - 1
        ans = BinarySearch().find_int_right(0, (rr - ll + 1) // 2, check) * 2 + 1
        ac.st(ans)
    return
abc_381e()
