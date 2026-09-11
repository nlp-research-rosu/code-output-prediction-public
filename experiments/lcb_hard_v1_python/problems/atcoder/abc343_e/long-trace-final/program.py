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

def abc_343e():
    ac = FastIO()

    def three(x, y, z, xx, yy, zz, xxx, yyy, zzz):
        res = 1
        res *= max(0, min(x, xx, xxx) + 7 - max(x, xx, xxx))
        res *= max(0, min(y, yy, yyy) + 7 - max(y, yy, yyy))
        res *= max(0, min(z, zz, zzz) + 7 - max(z, zz, zzz))
        return res

    def two(x, y, z, xx, yy, zz):
        res = 1
        res *= max(0, min(x, xx) + 7 - max(x, xx))
        res *= max(0, min(y, yy) + 7 - max(y, yy))
        res *= max(0, min(z, zz) + 7 - max(z, zz))
        return res
    a1 = b1 = c1 = 0
    low = -1
    high = 7
    v1, v2, v3 = ac.read_list_ints()
    for a2 in range(low, high + 1):
        for b2 in range(low, high + 1):
            for c2 in range(low, high + 1):
                for a3 in range(low, high + 1):
                    for b3 in range(low, high + 1):
                        for c3 in range(low, high + 1):
                            inter3 = three(a1, b1, c1, a2, b2, c2, a3, b3, c3)
                            inter2 = two(a1, b1, c1, a2, b2, c2) + two(a1, b1, c1, a3, b3, c3) + two(a2, b2, c2, a3, b3, c3) - inter3 * 3
                            inter1 = 3 * (7 * 7 * 7) - 2 * inter2 - 3 * inter3
                            if (v1, v2, v3) == (inter1, inter2, inter3):
                                ac.yes()
                                ac.lst([a1, b1, c1, a2, b2, c2, a3, b3, c3])
                                return
    ac.no()
    return
abc_343e()
