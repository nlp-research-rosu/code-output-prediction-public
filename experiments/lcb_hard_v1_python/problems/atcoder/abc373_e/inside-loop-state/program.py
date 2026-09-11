import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from types import GeneratorType
import bisect
import io, os
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from contextlib import redirect_stdout
from itertools import accumulate, combinations, permutations
from array import *
from functools import lru_cache, reduce
from heapq import heapify, heappop, heappush
from math import ceil, floor, sqrt, pi, factorial, gcd, log, log10, log2, inf
from random import randint, choice, shuffle, randrange
from string import ascii_lowercase, ascii_uppercase, digits
from decimal import Decimal, getcontext
RI = lambda: map(int, sys.stdin.buffer.readline().split())
RS = lambda: map(bytes.decode, sys.stdin.buffer.readline().strip().split())
RILST = lambda: list(RI())
DEBUG = lambda *x: sys.stderr.write(f'{str(x)}\n')
DIRS = [(0, 1), (1, 0), (0, -1), (-1, 0)]
DIRS8 = [(0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0), (-1, 1)]
RANDOM = randrange(2 ** 62)
MOD = 10 ** 9 + 7
PROBLEM = '\n'

def iii():
    num = 0
    neg = False
    while True:
        c = sys.stdin.read(1)
        if c == '-':
            neg = True
            continue
        elif c < '0' or c > '9':
            continue
        while True:
            num = 10 * num + ord(c) - ord('0')
            c = sys.stdin.read(1)
            if c < '0' or c > '9':
                break
        return -num if neg else num

def lower_bound(lo: int, hi: int, key):
    """由于3.10才能用key参数，因此自己实现一个。
    :param lo: 二分的左边界(闭区间)
    :param hi: 二分的右边界(闭区间)
    :param key: key(mid)判断当前枚举的mid是否应该划分到右半部分。
    :return: 右半部分第一个位置。若不存在True则返回hi+1。
    虽然实现是开区间写法，但为了思考简单，接口以[左闭,右闭]方式放出。
    """
    lo -= 1
    hi += 1
    while lo + 1 < hi:
        mid = lo + hi >> 1
        if key(mid):
            hi = mid
        else:
            lo = mid
    return hi

def bootstrap(f, stack=[]):

    def wrappedfunc(*args, **kwargs):
        if stack:
            return f(*args, **kwargs)
        else:
            to = f(*args, **kwargs)
            while True:
                if type(to) is GeneratorType:
                    stack.append(to)
                    to = next(to)
                else:
                    stack.pop()
                    if not stack:
                        break
                    to = stack[-1].send(to)
            return to
    return wrappedfunc

def solve():
    n, m, k = RI()
    a = RILST()
    if n == m:
        return print(*[0] * n)
    b = sorted(a, reverse=True)
    pre = [0] + list(accumulate(b))
    left = k - sum(a)
    s = sum(b[:m])
    ans = []
    for v in a:
        if b[m - 1] > v + left:
            ans.append(-1)
            continue
        if b[m - 1] > v:

            def ok(x):
                nv = v + x
                l, r = (-1, m)
                while l + 1 < r:
                    mid = (l + r) // 2
                    if b[mid] <= nv:
                        r = mid
                    else:
                        l = mid
                s1 = (nv + 1) * (m - r) - (pre[m] - pre[r])
                return s1 > left - x
            ans.append(bisect_left(range(0, left + 1), True, key=ok))
        else:

            def ok(x):
                nv = v + x
                l, r = (-1, m + 1)
                while l + 1 < r:
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'b': b, 'l': l, 'left': left, 'm': m, 'mid': mid, 'nv': nv, 'r': r, 'v': v, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    mid = (l + r) // 2
                    if b[mid] <= nv:
                        r = mid
                    else:
                        l = mid
                s1 = (nv + 1) * (m - r) - (pre[m + 1] - pre[r] - v)
                return s1 > left - x
            ans.append(bisect_left(range(0, left + 1), True, key=ok))
    print(*ans)
if __name__ == '__main__':
    t = 0
    if t:
        t, = RI()
        for _ in range(t):
            solve()
    else:
        solve()
