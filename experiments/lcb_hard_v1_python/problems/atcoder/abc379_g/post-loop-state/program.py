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

def abc_379g():
    ac = FastIO()
    m, n = ac.read_list_ints()
    grid = [list(ac.read_str()) for _ in range(m)]
    if m < n:
        grid = [[grid[i][j] for i in range(m)] for j in range(n)]
        m, n = (n, m)
    mod = 998244353
    pre = defaultdict(int)
    pre[0] = 1
    b = 10 ** (n - 1)
    for i in range(m):
        for j in range(n):
            cur = defaultdict(int)
            for x in [int(grid[i][j])] if grid[i][j] != '?' else [1, 2, 3]:
                for p in pre:
                    _lcb_count[0] += 1
                    if (not i or p // b != x) and (not j or p % 10 != x):
                        cur[p % b * 10 + x] += pre[p]
                        cur[p % b * 10 + x] %= mod
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'b': b, 'cur': cur, 'i': i, 'j': j, 'p': p, 'pre': pre, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
            pre = cur
    ans = sum(pre.values()) % mod
    ac.st(ans)
    return
abc_379g()
