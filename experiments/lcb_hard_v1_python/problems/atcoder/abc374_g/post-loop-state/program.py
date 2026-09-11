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
from typing import NamedTuple, Optional, List, cast

class MFGraph:

    class Edge(NamedTuple):
        src: int
        dst: int
        cap: int
        flow: int

    class _Edge:

        def __init__(self, dst: int, cap: int) -> None:
            self.dst = dst
            self.cap = cap
            self.rev: Optional[MFGraph._Edge] = None

    def __init__(self, n: int) -> None:
        self._n = n
        self._g: List[List[MFGraph._Edge]] = [[] for _ in range(n)]
        self._edges: List[MFGraph._Edge] = []

    def add_edge(self, src: int, dst: int, cap: int) -> int:
        assert 0 <= src < self._n
        assert 0 <= dst < self._n
        assert 0 <= cap
        m = len(self._edges)
        e = MFGraph._Edge(dst, cap)
        re = MFGraph._Edge(src, 0)
        e.rev = re
        re.rev = e
        self._g[src].append(e)
        self._g[dst].append(re)
        self._edges.append(e)
        return m

    def get_edge(self, i: int) -> Edge:
        assert 0 <= i < len(self._edges)
        e = self._edges[i]
        re = cast(MFGraph._Edge, e.rev)
        return MFGraph.Edge(re.dst, e.dst, e.cap + re.cap, re.cap)

    def edges(self) -> List[Edge]:
        return [self.get_edge(i) for i in range(len(self._edges))]

    def change_edge(self, i: int, new_cap: int, new_flow: int) -> None:
        assert 0 <= i < len(self._edges)
        assert 0 <= new_flow <= new_cap
        e = self._edges[i]
        e.cap = new_cap - new_flow
        assert e.rev is not None
        e.rev.cap = new_flow

    def flow(self, s: int, t: int, flow_limit: Optional[int]=None) -> int:
        assert 0 <= s < self._n
        assert 0 <= t < self._n
        assert s != t
        if flow_limit is None:
            flow_limit = cast(int, sum((e.cap for e in self._g[s])))
        current_edge = [0] * self._n
        level = [0] * self._n

        def fill(arr: List[int], value: int) -> None:
            for i in range(len(arr)):
                arr[i] = value

        def bfs() -> bool:
            fill(level, self._n)
            queue = []
            q_front = 0
            queue.append(s)
            level[s] = 0
            while q_front < len(queue):
                v = queue[q_front]
                q_front += 1
                next_level = level[v] + 1
                for e in self._g[v]:
                    if e.cap == 0 or level[e.dst] <= next_level:
                        continue
                    level[e.dst] = next_level
                    if e.dst == t:
                        return True
                    queue.append(e.dst)
            return False

        def dfs(lim: int) -> int:
            stack = []
            edge_stack: List[MFGraph._Edge] = []
            stack.append(t)
            while stack:
                v = stack[-1]
                if v == s:
                    flow = min(lim, min((e.cap for e in edge_stack)))
                    for e in edge_stack:
                        e.cap -= flow
                        assert e.rev is not None
                        e.rev.cap += flow
                    return flow
                next_level = level[v] - 1
                while current_edge[v] < len(self._g[v]):
                    e = self._g[v][current_edge[v]]
                    re = cast(MFGraph._Edge, e.rev)
                    if level[e.dst] != next_level or re.cap == 0:
                        current_edge[v] += 1
                        continue
                    stack.append(e.dst)
                    edge_stack.append(re)
                    break
                else:
                    stack.pop()
                    if edge_stack:
                        edge_stack.pop()
                    level[v] = self._n
            return 0
        flow = 0
        while flow < flow_limit:
            if not bfs():
                break
            fill(current_edge, 0)
            while flow < flow_limit:
                f = dfs(flow_limit - flow)
                flow += f
                if f == 0:
                    break
        return flow

    def min_cut(self, s: int) -> List[bool]:
        visited = [False] * self._n
        stack = [s]
        visited[s] = True
        while stack:
            v = stack.pop()
            for e in self._g[v]:
                if e.cap > 0 and (not visited[e.dst]):
                    visited[e.dst] = True
                    stack.append(e.dst)
        return visited

def compress(S):
    """ 座標圧縮 """
    S = set(S)
    zipped, unzipped = ({}, {})
    for i, a in enumerate(sorted(S)):
        zipped[a] = i
        unzipped[i] = a
    return (zipped, unzipped)

def scc(N, G, RG):
    order = []
    used = [0] * N
    group = [None] * N

    def dfs(s):
        used[s] = 1
        for t in G[s]:
            if not used[t]:
                dfs(t)
        order.append(s)

    def rdfs(s, col):
        group[s] = col
        used[s] = 1
        for t in RG[s]:
            if not used[t]:
                rdfs(t, col)
    for i in range(N):
        if not used[i]:
            dfs(i)
    used = [0] * N
    label = 0
    for s in reversed(order):
        if not used[s]:
            rdfs(s, label)
            label += 1
    return (label, group)

def construct(N, G, label, group):
    """
    縮約後のグラフを構築: トポソ済み
    G0: 各強連結成分の遷移先の集合
    GP: 各強連結成分内の元の頂点のリスト
    """
    G0 = [set() for i in range(label)]
    GP = [[] for i in range(label)]
    for v in range(N):
        lbs = group[v]
        for w in G[v]:
            lbt = group[w]
            if lbs == lbt:
                continue
            G0[lbs].add(lbt)
        GP[lbs].append(v)
    return (G0, GP)

def make_adjlist_d(n, edges):
    res = [[] for _ in range(n)]
    for edge in edges:
        res[edge[0]].append(edge[1])
    return res

def main():
    N = NI()
    S = [SI() for _ in range(N)]
    RS = {s: i for i, s in enumerate(S)}
    G = [[] for _ in range(N)]
    RG = [[] for _ in range(N)]
    for i in range(N):
        for j in range(i + 1, N):
            si, sj = (S[i], S[j])
            if si[-1] == sj[0]:
                G[i].append(j)
                RG[j].append(i)
            if sj[-1] == si[0]:
                G[j].append(i)
                RG[i].append(j)
    label, group = scc(N, G, RG)
    G0, GP = construct(N, G, label, group)
    D = [[0] * label for _ in range(label)]
    for i in range(label):
        for j in G0[i]:
            D[i][j] = 1
    for i in range(label):
        for j in range(label):
            if D[i][j]:
                for k in range(label):
                    _lcb_count[0] += 1
                    D[i][k] |= D[j][k]
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'D': D, 'i': i, 'j': j, 'k': k, 'label': label}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
    F = MFGraph(label * 2 + 2)
    src = label * 2
    dst = src + 1
    for i in range(label):
        F.add_edge(src, i, 1)
        F.add_edge(i + label, dst, 1)
        for j in range(label):
            if D[i][j]:
                F.add_edge(i, j + label, 1)
    f = F.flow(src, dst)
    print(label - f)
if __name__ == '__main__':
    main()
