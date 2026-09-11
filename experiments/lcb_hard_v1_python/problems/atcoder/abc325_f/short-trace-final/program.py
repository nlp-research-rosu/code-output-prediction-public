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

def abc_325f():
    ac = FastIO()
    n = ac.read_int()
    dis = ac.read_list_ints()
    l1, c1, k1 = ac.read_list_ints()
    l2, c2, k2 = ac.read_list_ints()
    dp = [0] * (k1 + 1)
    for i in range(n):
        d = dis[i]
        ndp = [math.inf] * (k1 + 1)
        for j in range(k1 + 1):
            if dp[j] < math.inf:
                for x in range(k1 - j + 1):
                    need = max(0, math.ceil((d - x * l1) / l2))
                    ndp[j + x] = min(ndp[j + x], dp[j] + need)
        dp = ndp
    ans = math.inf
    for i in range(k1 + 1):
        if dp[i] <= k2:
            ans = min(ans, i * c1 + dp[i] * c2)
    ac.st(ans if ans < math.inf else -1)
    return
abc_325f()
