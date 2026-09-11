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
PROBLEM = 'https://atcoder.jp/contests/abc375/tasks/abc375_f\n\n输入 n(2≤n≤300) m(0≤m≤n*(n-1)/2) q(1≤q≤2e5)，表示一个 n 点 m 边的无向图。保证图中无自环和重边。\n然后输入 m 条边，每条边输入 x y w(1≤w≤1e9)，表示一条边权为 w 的无向边连接 x 和 y。节点编号从 1 开始。\n\n然后输入 q 个询问，格式如下：\n"1 i"：删掉输入的第 i(1≤i≤m) 条边。保证这条边没被删除。\n"2 x y"：输出从 x 到 y 的最短距离。如果无法到达，输出 -1。\n\n保证第一种询问不超过 300 个。\n'

def solve():
    n, m, q = RI()
    es = []
    dis = [[inf] * n for _ in range(n)]
    for i in range(n):
        dis[i][i] = 0
    for _ in range(m):
        u, v, w = RI()
        u -= 1
        v -= 1
        es.append((u, v, w))
        dis[u][v] = dis[v][u] = w
    qs = []
    for _ in range(q):
        op = RILST()
        qs.append(op)
        if op[0] == 1:
            _, i = op
            u, v, _ = es[i - 1]
            dis[u][v] = dis[v][u] = inf
    for k in range(n):
        for u in range(n):
            for v in range(n):
                _lcb_count[0] += 1
                dis[u][v] = min(dis[u][v], dis[u][k] + dis[k][v])
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'dis': dis, 'i': i, 'k': k, 'u': u, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
    ans = []
    for q in qs[::-1]:
        t, *op = q
        if t == 1:
            u, v, w = es[op[0] - 1]
            for i in range(n):
                for j in range(n):
                    dis[i][j] = min(dis[i][j], dis[i][u] + w + dis[v][j], dis[i][v] + w + dis[u][j])
        else:
            u, v = op
            ans.append(dis[u - 1][v - 1] if dis[u - 1][v - 1] < inf else -1)
    print(*ans[::-1], sep='\n')
if __name__ == '__main__':
    t = 0
    if t:
        t, = RI()
        for _ in range(t):
            solve()
    else:
        solve()
