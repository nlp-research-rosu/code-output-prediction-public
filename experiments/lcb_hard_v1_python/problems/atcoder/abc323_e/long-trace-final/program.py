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

def abc_323e():
    ac = FastIO()
    n, x = ac.read_list_ints()
    t = ac.read_list_ints()
    dp = [0] * (x + 1)
    dp[0] = 1
    mod = 998244353
    pp = pow(n, -1, mod)
    for i in range(1, x + 1):
        for j in range(n):
            if i >= t[j]:
                dp[i] += dp[i - t[j]] * pp
        dp[i] %= mod
    res = 0
    for i in range(x + 1):
        if i + t[0] > x:
            res += dp[i]
    res = res * pp % mod
    ac.st(res)
    return
abc_323e()
