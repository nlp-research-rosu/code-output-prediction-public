import sys

class UnionFind:

    def __init__(self, n: int) -> None:
        self.n = n
        self.p = [-1] * n

    def leader(self, a: int) -> int:
        while self.p[a] >= 0:
            a = self.p[a]
        return a

    def merge(self, a: int, b: int) -> int:
        x = self.leader(a)
        y = self.leader(b)
        if x == y:
            return x
        if self.p[x] > self.p[y]:
            x, y = (y, x)
        self.p[x] += self.p[y]
        self.p[y] = x
        return x

    def same(self, a: int, b: int) -> bool:
        return self.leader(a) == self.leader(b)

    def groups(self) -> list:
        member = [[] for _ in range(self.n)]
        for i in range(self.n):
            member[self.leader(i)].append(i)
        return member

    def size(self, a: int) -> int:
        return -self.p[self.leader(a)]
from collections import deque

def main() -> None:
    H, W = map(int, input().split())
    S = [input() for _ in range(H)]
    ans = []
    uf = UnionFind(H * W)
    d = ((1, 0), (-1, 0), (0, 1), (0, -1))
    is_ok = [[1] * W for _ in range(H)]
    for i in range(H):
        for j in range(W):
            if S[i][j] == '#':
                is_ok[i][j] = 0
            is_near = False
            for dy, dx in d:
                ny = i + dy
                nx = j + dx
                if not (0 <= nx < W and 0 <= ny < H):
                    continue
                if S[ny][nx] == '#':
                    is_near = True
            if is_near:
                is_ok[i][j] = 0
    for i in range(H):
        for j in range(W - 1):
            if is_ok[i][j] == 1 and is_ok[i][j + 1] == 1:
                uf.merge(i * W + j, i * W + (j + 1))
    for i in range(H - 1):
        for j in range(W):
            if is_ok[i][j] == 1 and is_ok[i + 1][j] == 1:
                uf.merge(i * W + j, (i + 1) * W + j)
    ans = 1
    t = uf.groups()
    for u in t:
        s = set()
        for ii in u:
            p = ii // W
            q = ii % W
            if S[p][q] == '#':
                continue
            s.add((p, q))
            if is_ok[p][q] == 0:
                continue
            for dy, dx in d:
                ny = p + dy
                nx = q + dx
                if not (0 <= ny < H and 0 <= nx < W):
                    continue
                if S[ny][nx] == '#':
                    continue
                s.add((ny, nx))
        ans = max(ans, len(s))
    print(ans)
if __name__ == '__main__':
    main()
