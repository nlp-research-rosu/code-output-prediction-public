import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
_lcb_sys.setrecursionlimit(10000)
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

def abc_377g():
    ac = FastIO()
    n = ac.read_int()
    words = [ac.read_str() for _ in range(n)]
    dct = dict()
    for i, word in enumerate(words):
        cur = dct
        pre = 0
        m = len(word)
        ans = m
        for w in word:
            _lcb_count[0] += 1
            if w in cur:
                pre += 1
                cur = cur[w]
                ans = min(ans, m - pre + cur['len'] - pre)
            else:
                cur[w] = dict()
                cur = cur[w]
                pre = math.inf
            cur['len'] = min(cur.get('len', math.inf), m)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dct': dct}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if i:
            ac.st(ans)
        else:
            ac.st(m)
    return
abc_377g()
