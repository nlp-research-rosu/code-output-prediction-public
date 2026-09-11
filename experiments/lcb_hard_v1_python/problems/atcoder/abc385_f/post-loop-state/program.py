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

def abc_385f():
    ac = FastIO()
    n = ac.read_int()
    nums = [ac.read_list_ints() for _ in range(n)]
    stack = [nums[0]]
    ans = -1
    for i in range(1, n):
        _lcb_count[0] += 1
        x, y = nums[i]
        while len(stack) >= 2 and (y - stack[-1][1]) * (x - stack[-2][0]) >= (x - stack[-1][0]) * (y - stack[-2][1]):
            stack.pop()
        k = decimal.Decimal(y - stack[-1][1]) / decimal.Decimal(x - stack[-1][0])
        b = decimal.Decimal(y - k * x)
        ans = max(ans, b)
        stack.append((x, y))
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'nums': nums, 'stack': stack, 'str(ans)': str(ans), 'str(b)': str(b), 'str(k)': str(k), 'x': x, 'y': y}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    ac.st(ans if ans >= 0 else -1)
    return
abc_385f()
