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

def abc_377e():
    ac = FastIO()
    n, k = ac.read_list_ints()
    p = ac.read_list_ints_minus_one()
    visit = [0] * n
    ans = [0] * n
    for i in range(n):
        if not visit[i]:
            lst = [i]
            visit[i] = 1
            while not visit[p[lst[-1]]]:
                lst.append(p[lst[-1]])
                visit[lst[-1]] = 1
            m = len(lst)
            j = pow(2, k, m)
            for x in range(m):
                ans[lst[x]] = lst[(x + j) % m] + 1
    ac.lst(ans)
    return
abc_377e()
