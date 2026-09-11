import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from typing import List

class UnionFindArraySimple:
    __slots__ = ('part', 'n', '_data')

    def __init__(self, n: int):
        self.part = n
        self.n = n
        self._data = [-1] * n

    def union(self, key1: int, key2: int) -> bool:
        root1, root2 = (self.find(key1), self.find(key2))
        if root1 == root2:
            return False
        if self._data[root1] > self._data[root2]:
            root1, root2 = (root2, root1)
        self._data[root1] += self._data[root2]
        self._data[root2] = root1
        self.part -= 1
        return True

    def find(self, key: int) -> int:
        if self._data[key] < 0:
            return key
        self._data[key] = self.find(self._data[key])
        return self._data[key]

    def getSize(self, key: int) -> int:
        return -self._data[self.find(key)]

    def getGroups(self) -> List[List[int]]:
        res = [[] for _ in range(self.n)]
        for i in range(self.n):
            res[self.find(i)].append(i)
        return [x for x in res if x]
C = 26
if __name__ == '__main__':
    N = int(input())
    S = input()
    T = input()
    if S == T:
        print(0)
        exit()
    nums1 = [ord(c) - ord('a') for c in S]
    nums2 = [ord(c) - ord('a') for c in T]
    to = [-1] * C
    for c1, c2 in zip(nums1, nums2):
        _lcb_count[0] += 1
        if to[c1] != -1 and to[c1] != c2:
            print(-1)
            exit()
        to[c1] = c2
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'c1': c1, 'c2': c2, 'nums1': nums1, 'nums2': nums2, 'to': to}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    tmp = sorted(to)
    isPerm = all((tmp[i] == i for i in range(C)))
    if isPerm:
        print(-1)
        exit()
    res = 0
    indeg = [0] * C
    uf = UnionFindArraySimple(C)
    for i, v in enumerate(to):
        if v != -1:
            if i != v:
                res += 1
            indeg[v] += 1
            uf.union(i, v)
    for g in uf.getGroups():
        if len(g) == 1:
            continue
        isCycle = all((indeg[i] == 1 for i in g))
        res += isCycle
    print(res)
