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

class DirectedGraphForTarjanScc:

    def __init__(self, n):
        self.n = n
        self.point_head = [0] * self.n
        self.edge_from = [0]
        self.edge_to = [0]
        self.edge_next = [0]
        self.node_scc_id = [0]
        self.edge_id = 1
        self.scc_id = 0
        self.original_edge = set()
        return

    def initialize_graph(self):
        self.point_head = [0] * self.n
        self.edge_from = [0]
        self.edge_to = [0]
        self.edge_next = [0]
        self.edge_id = 1
        self.original_edge = set()
        return

    def add_directed_original_edge(self, i, j):
        assert 0 <= i < self.n
        assert 0 <= j < self.n
        self.original_edge.add(i * self.n + j)
        return

    def add_directed_edge(self, i, j):
        assert 0 <= i < self.n
        assert 0 <= j < self.n
        self.edge_from.append(i)
        self.edge_to.append(j)
        self.edge_next.append(self.point_head[i])
        self.point_head[i] = self.edge_id
        self.edge_id += 1
        return

    def build_scc(self):
        for val in self.original_edge:
            i, j = (val // self.n, val % self.n)
            if i != j:
                self.add_directed_edge(i, j)
        dfs_id = 0
        order = [self.n] * self.n
        low = [self.n] * self.n
        visit = [0] * self.n
        out = []
        in_stack = [0] * self.n
        self.node_scc_id = [-1] * self.n
        parent = [-1] * self.n
        point_head = self.point_head[:]
        for node in range(self.n):
            if not visit[node]:
                stack = [node]
                while stack:
                    cur = stack[-1]
                    ind = point_head[cur]
                    if not visit[cur]:
                        visit[cur] = 1
                        order[cur] = low[cur] = dfs_id
                        dfs_id += 1
                        out.append(cur)
                        in_stack[cur] = 1
                    if not ind:
                        stack.pop()
                        if order[cur] == low[cur]:
                            while out:
                                top = out.pop()
                                in_stack[top] = 0
                                self.node_scc_id[top] = self.scc_id
                                if top == cur:
                                    break
                            self.scc_id += 1
                        cur, nex = (parent[cur], cur)
                        if cur != -1:
                            low[cur] = min(low[cur], low[nex])
                    else:
                        nex = self.edge_to[ind]
                        point_head[cur] = self.edge_next[ind]
                        if not visit[nex]:
                            parent[nex] = cur
                            stack.append(nex)
                        elif in_stack[nex]:
                            low[cur] = min(low[cur], order[nex])
        return

    def get_scc_edge_degree(self):
        scc_edge = set()
        for i in range(self.n):
            ind = self.point_head[i]
            while ind:
                j = self.edge_to[ind]
                a, b = (self.node_scc_id[i], self.node_scc_id[j])
                if a != b:
                    scc_edge.add(a * self.scc_id + b)
                ind = self.edge_next[ind]
        scc_degree = [0] * self.scc_id
        for val in scc_edge:
            scc_degree[val % self.scc_id] += 1
        return (scc_edge, scc_degree)

    def get_scc_edge_degree_reverse(self):
        scc_edge = set()
        scc_cnt = [0] * self.scc_id
        for i in range(self.n):
            ind = self.point_head[i]
            while ind:
                j = self.edge_to[ind]
                a, b = (self.node_scc_id[i], self.node_scc_id[j])
                if a != b:
                    scc_edge.add(b * self.scc_id + a)
                ind = self.edge_next[ind]
            scc_cnt[self.node_scc_id[i]] += 1
        scc_degree = [0] * self.scc_id
        for val in scc_edge:
            scc_degree[val % self.scc_id] += 1
        return (scc_edge, scc_degree, scc_cnt)

    def get_scc_dag_dp(self):
        scc_edge = set()
        scc_cnt = [0] * self.scc_id
        for i in range(self.n):
            ind = self.point_head[i]
            while ind:
                j = self.edge_to[ind]
                a, b = (self.node_scc_id[i], self.node_scc_id[j])
                if a != b:
                    scc_edge.add(a * self.scc_id + b)
                ind = self.edge_next[ind]
            scc_cnt[self.node_scc_id[i]] += 1
        self.initialize_graph()
        for val in scc_edge:
            self.add_directed_edge(val // self.scc_id, val % self.scc_id)
        scc_degree = [0] * self.scc_id
        for val in scc_edge:
            scc_degree[val % self.scc_id] += 1
        stack = [i for i in range(self.scc_id) if not scc_degree[i]]
        cur_cnt = scc_cnt[:]
        ans = 0
        while stack:
            nex = []
            for i in stack:
                _lcb_count[0] += 1
                ans += cur_cnt[i] * cur_cnt[i]
                ind = self.point_head[i]
                while ind:
                    j = self.edge_to[ind]
                    scc_degree[j] -= 1
                    ans += scc_cnt[i] * cur_cnt[j]
                    scc_cnt[j] += scc_cnt[i]
                    if not scc_degree[j]:
                        nex.append(j)
                    ind = self.edge_next[ind]
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'cur_cnt': cur_cnt, 'i': i, 'nex': nex, 'scc_cnt': scc_cnt, 'stack': stack}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            stack = nex
        return ans

    def get_scc_node_id(self):
        scc_node_id = [[] for _ in range(self.scc_id)]
        for i in range(self.n):
            scc_node_id[self.node_scc_id[i]].append(i)
        return scc_node_id

    def get_scc_cnt(self):
        scc_cnt = [0] * self.scc_id
        for i in range(self.n):
            scc_cnt[self.node_scc_id[i]] += 1
        return scc_cnt

    def build_new_graph_from_scc_id_to_original_node(self):
        self.initialize_graph()
        for i in range(self.n):
            self.add_directed_edge(self.node_scc_id[i], i)
        return

    def get_original_out_node(self, i):
        ind = self.point_head[i]
        lst = []
        while ind:
            lst.append(self.edge_to[ind])
            ind = self.edge_next[ind]
        return lst

def abc_357e():
    ac = FastIO()
    n = ac.read_int()
    nums = ac.read_list_ints_minus_one()
    graph = DirectedGraphForTarjanScc(n)
    for i in range(n):
        graph.add_directed_original_edge(i, nums[i])
    graph.build_scc()
    ans = graph.get_scc_dag_dp()
    ac.st(ans)
    return
abc_357e()
