import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.read

class UnionFind:

    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        xroot = self.find(x)
        yroot = self.find(y)
        if xroot == yroot:
            return False
        if self.rank[xroot] < self.rank[yroot]:
            self.parent[xroot] = yroot
        else:
            self.parent[yroot] = xroot
            if self.rank[xroot] == self.rank[yroot]:
                self.rank[xroot] += 1
        return True

def main():
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    M = int(data[idx])
    idx += 1
    edges = []
    for _ in range(M):
        K_i = int(data[idx])
        idx += 1
        C_i = int(data[idx])
        idx += 1
        subset = list(map(int, data[idx:idx + K_i]))
        idx += K_i
        first = subset[0] - 1
        for v in subset[1:]:
            u = v - 1
            edges.append((C_i, first, u))
    edges.sort()
    uf = UnionFind(N)
    mst_weight = 0
    for weight, u, v in edges:
        _lcb_count[0] += 1
        if uf.union(u, v):
            mst_weight += weight
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'mst_weight': mst_weight, 'u': u, 'uf.parent': uf.parent, 'uf.rank': uf.rank, 'v': v, 'weight': weight}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    root = uf.find(0)
    for i in range(1, N):
        if uf.find(i) != root:
            print(-1)
            return
    print(mst_weight)
if __name__ == '__main__':
    main()
