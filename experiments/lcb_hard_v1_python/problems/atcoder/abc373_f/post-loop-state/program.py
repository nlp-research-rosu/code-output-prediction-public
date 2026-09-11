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

def abc_373f():
    ac = FastIO()
    n, w = ac.read_list_ints()
    nums = [[] for _ in range(w + 1)]
    for _ in range(n):
        ww, vv = ac.read_list_ints()
        nums[ww].append(vv)
    dp = [0] * (w + 1)
    dp[0] = 0
    for ww in range(w + 1):
        if nums[ww]:
            stack = [-(v - 1) for v in nums[ww]]
            heapify(stack)
            cur = [0]
            for i in range(1, w // ww + 1):
                v = -heappop(stack)
                cur.append(cur[-1] + v)
                heappush(stack, -(v - 2))
            for j in range(w, -1, -1):
                for i in range(1, j // ww + 1):
                    _lcb_count[0] += 1
                    dp[j] = max(dp[j], dp[j - i * ww] + cur[i])
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'cur': cur, 'dp': dp, 'i': i, 'j': j, 'ww': ww}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
    ac.st(max(dp))
    return
abc_373f()
