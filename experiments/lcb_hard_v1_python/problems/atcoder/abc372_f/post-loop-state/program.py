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

def abc_372f():
    ac = FastIO()
    n, m, k = ac.read_list_ints()
    mod = 998244353
    edges = [ac.read_list_ints_minus_one() for _ in range(m)]
    dp = [0] * (n + k)
    dp[k] = 1
    for i in range(k, 0, -1):
        post = [(y, dp[i + x]) for x, y in edges]
        for y, num in post:
            _lcb_count[0] += 1
            dp[i + y - 1] += num
            dp[i + y - 1] %= mod
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'num': num, 'post': post, 'y': y}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        dp[i - 1] += dp[i + n - 1]
        dp[i - 1] %= mod
        dp[i + n - 1] = 0
    ac.st(sum(dp) % mod)
    return
abc_372f()
