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

def abc_366f():
    ac = FastIO()
    n, k = ac.read_list_ints()
    dp = [-math.inf] * (k + 1)
    dp[0] = 1
    nums = [ac.read_list_ints() for _ in range(n)]

    def compare_(x, y):
        if x[0] * y[1] + x[1] < y[0] * x[1] + y[1]:
            return -1
        return 1
    nums.sort(key=cmp_to_key(compare_))
    for a, b in nums:
        for i in range(k, 0, -1):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'b': b, '[value for value in dp if value != -math.inf]': [value for value in dp if value != -math.inf], 'i': i}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            dp[i] = max(dp[i], a * dp[i - 1] + b)
    ac.st(dp[-1])
    return
abc_366f()
