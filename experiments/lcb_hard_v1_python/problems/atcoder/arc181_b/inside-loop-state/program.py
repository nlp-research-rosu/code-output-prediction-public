import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
import bisect
from heapq import heapify, heappop, heappush
from collections import deque, defaultdict, Counter
from functools import lru_cache
from itertools import accumulate, combinations, permutations, product
sys.set_int_max_str_digits(10 ** 6)
sys.setrecursionlimit(1000000)
MOD = 10 ** 9 + 7
MOD99 = 998244353
input = lambda: sys.stdin.readline().strip()
NI = lambda: int(input())
NMI = lambda: map(int, input().split())
NLI = lambda: list(NMI())
SI = lambda: input()
SMI = lambda: input().split()
SLI = lambda: list(SMI())
EI = lambda m: [NLI() for _ in range(m)]

def divisors(x):
    res = set()
    for i in range(1, int(x ** 0.5) + 2):
        if x % i == 0:
            res.add(i)
            res.add(x // i)
    return res

def check(S):
    N = len(S)
    D = sorted(divisors(N))
    for d in D:
        P = set()
        for i in range(N // d):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'D': D, 'N': N, 'sorted(P)': sorted(P), 'S': S, 'd': d, 'i': i}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            P.add(S[i * d:i * d + d])
        if len(P) == 1:
            return (P.pop(), N // d)

def solve(S, X, Y):
    N = len(S)
    s, k = check(S)
    x0 = X.count('0') * k
    x1 = X.count('1')
    y0 = Y.count('0') * k
    y1 = Y.count('1')
    S = s
    if x0 == y0:
        return True
    if x1 == y1:
        return False
    if (y0 - x0) * (x1 - y1) < 0:
        return False
    if N * (y0 - x0) % (x1 - y1):
        return False
    M = N * (y0 - x0) // (x1 - y1)
    if M <= N:
        if N % M:
            return False
        P = set()
        for i in range(N // M):
            P.add(S[i * M:i * M + M])
        if len(P) == 1:
            return True
        return False
    else:
        if M % N:
            return False
        return True

def main():
    case = NI()
    for _ in range(case):
        S = SI()
        X = SI()
        Y = SI()
        if solve(S, X, Y):
            print('Yes')
        else:
            print('No')
if __name__ == '__main__':
    main()
