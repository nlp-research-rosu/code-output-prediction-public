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

def main():
    N = NI()
    X = NLI()
    G0 = [X[i + 1] - X[i] for i in range(N - 1) if i % 2 == 0]
    G0.sort()
    G1 = [X[i + 1] - X[i] for i in range(N - 1) if i % 2]
    G1.sort()
    Y = [X[0]]
    for i in range(N):
        if i < len(G0):
            Y.append(Y[-1] + G0[i])
        if i < len(G1):
            Y.append(Y[-1] + G1[i])
    print(sum(Y))
if __name__ == '__main__':
    main()
