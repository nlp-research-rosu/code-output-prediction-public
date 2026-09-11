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

class RangeAddRangeMaxIndex:

    def __init__(self, n):
        self.n = n
        self.lazy_tag = [0] * (4 * self.n)
        self.ceil = [0] * (4 * self.n)
        self.index = [0] * (4 * self.n)
        return

    def build(self, nums):
        stack = [(0, self.n - 1, 1)]
        while stack:
            s, t, i = stack.pop()
            if i >= 0:
                if s == t:
                    self.ceil[i] = nums[s]
                    self.index[i] = s
                else:
                    stack.append((s, t, ~i))
                    m = s + (t - s) // 2
                    stack.append((s, m, i << 1))
                    stack.append((m + 1, t, i << 1 | 1))
            else:
                i = ~i
                self._push_up(i)
        return

    def _push_down(self, i):
        if self.lazy_tag[i]:
            self.ceil[i << 1] += self.lazy_tag[i]
            self.ceil[i << 1 | 1] += self.lazy_tag[i]
            self.lazy_tag[i << 1] += self.lazy_tag[i]
            self.lazy_tag[i << 1 | 1] += self.lazy_tag[i]
            self.lazy_tag[i] = 0

    def _push_up(self, i):
        if self.ceil[i << 1] >= self.ceil[i << 1 | 1]:
            self.ceil[i] = self.ceil[i << 1]
            self.index[i] = self.index[i << 1]
        else:
            self.ceil[i] = self.ceil[i << 1 | 1]
            self.index[i] = self.index[i << 1 | 1]
        return

    def _make_tag(self, i, val):
        self.ceil[i] += val
        self.lazy_tag[i] += val
        return

    def range_add(self, left, right, val):
        stack = [(0, self.n - 1, 1)]
        while stack:
            s, t, i = stack.pop()
            if i >= 0:
                if left <= s and t <= right:
                    self._make_tag(i, val)
                    continue
                m = s + (t - s) // 2
                self._push_down(i)
                stack.append((s, t, ~i))
                if left <= m:
                    stack.append((s, m, i << 1))
                if right > m:
                    stack.append((m + 1, t, i << 1 | 1))
            else:
                i = ~i
                self._push_up(i)
        return

    def get(self):
        stack = [(0, self.n - 1, 1)]
        nums = [0] * self.n
        while stack:
            s, t, i = stack.pop()
            if s == t:
                val = self.ceil[i]
                nums[s] = val
                continue
            self._push_down(i)
            m = s + (t - s) // 2
            stack.append((s, m, i << 1))
            stack.append((m + 1, t, i << 1 | 1))
        return nums

    def range_max_bisect_left(self, left, right, val):
        stack = [(0, self.n - 1, 1)]
        res = -1
        while stack and res == -1:
            s, t, i = stack.pop()
            if s == t:
                if left <= s <= right and self.ceil[i] >= val:
                    res = s
                continue
            m = s + (t - s) // 2
            self._push_down(i)
            if right > m and self.ceil[i << 1 | 1] >= val:
                stack.append((m + 1, t, i << 1 | 1))
            if left <= m and self.ceil[i << 1] >= val:
                stack.append((s, m, i << 1))
        return res

    def range_max(self, left, right):
        stack = [(0, self.n - 1, 1)]
        highest = -math.inf
        while stack:
            s, t, i = stack.pop()
            if left <= s and t <= right:
                highest = max(highest, self.ceil[i])
                continue
            m = s + (t - s) // 2
            self._push_down(i)
            if left <= m:
                stack.append((s, m, i << 1))
            if right > m:
                stack.append((m + 1, t, i << 1 | 1))
        return highest

    def range_max_index(self, left, right):
        stack = [(0, self.n - 1, 1)]
        highest = -math.inf
        ind = -1
        while stack:
            s, t, i = stack.pop()
            if left <= s and t <= right:
                if self.ceil[i] > highest:
                    highest = self.ceil[i]
                    ind = self.index[i]
                continue
            m = s + (t - s) // 2
            self._push_down(i)
            if right > m:
                stack.append((m + 1, t, i << 1 | 1))
            if left <= m:
                stack.append((s, m, i << 1))
        return (highest, ind)

def abc_369g():
    ac = FastIO()
    n = ac.read_int()
    dct = [list() for _ in range(n)]
    for _ in range(n - 1):
        i, j, ll = ac.read_list_ints_minus_one()
        ll += 1
        dct[i].append(ll * n + j)
        dct[j].append(ll * n + i)
    order = 0
    start = [-1] * n
    end = [-1] * n
    parent = [-1] * n
    stack = [(0, -1)]
    depth = [0] * n
    order_to_node = [-1] * n
    while stack:
        i, fa = stack.pop()
        if i >= 0:
            start[i] = order
            order_to_node[order] = i
            end[i] = order
            order += 1
            stack.append((~i, fa))
            for val in dct[i]:
                j, w = (val % n, val // n)
                if j != fa:
                    parent[j] = i
                    depth[j] = depth[i] + w
                    stack.append((j, i))
        else:
            i = ~i
            if parent[i] != -1:
                end[parent[i]] = end[i]
    tree = RangeAddRangeMaxIndex(n)
    tree.build([depth[x] for x in order_to_node])
    ans = 0
    visit = [0] * n
    for _ in range(n):
        ceil = tree.ceil[1]
        i = order_to_node[tree.index[1]]
        if ceil <= 0:
            ac.st(ans)
            continue
        visit[i] = 1
        path = [i]
        while parent[i] != -1 and (not visit[parent[i]]):
            visit[parent[i]] = 1
            i = parent[i]
            path.append(i)
        path.reverse()
        for i in path:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'ceil': ceil, 'i': i, 'path': path, 'pre': pre}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if parent[i] != -1:
                pre = depth[i] - depth[parent[i]]
            else:
                pre = 0
            tree.range_add(start[i], end[i], -pre)
        ans += ceil * 2
        ac.st(ans)
    return
abc_369g()
