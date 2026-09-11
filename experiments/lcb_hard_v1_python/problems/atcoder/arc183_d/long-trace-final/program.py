import sys
'\n                               |                                \n                              |||                               \n                             |||||                              \n                            |||||||                             \n╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╸\n                       Coded by: kobejean                       \n'
import heapq

def rint(shift=0, base=10):
    return [int(x, base) + shift for x in input().split()]

def find_centroid(T):
    N = len(T)
    size = [0] * N
    stack = [(0, None, 0)]
    centroid = None
    while stack:
        u, p, state = stack.pop()
        if state == 0:
            size[u] = 1
            stack.append((u, p, 1))
            for v in T[u]:
                if v != p:
                    stack.append((v, u, 0))
        else:
            is_centroid = True
            for v in T[u]:
                if v == p:
                    continue
                if size[v] > N // 2:
                    is_centroid = False
                size[u] += size[v]
            if N - size[u] > N // 2:
                is_centroid = False
            if is_centroid:
                centroid = u
                break
    return centroid

def solve():
    size = [0] * N
    centroid = find_centroid(T)
    dfs_order = [[] for _ in range(N)]
    matched = (0, -1)
    heap = []

    def dfs(u, p):
        r = u
        stack = [(u, p, False)]
        while stack:
            u, p, done = stack.pop()
            if not done:
                size[u] = 1
                dfs_order[r].append(u)
                m = u ^ 1
                stack.append((u, p, True))
                if m != p and m in T[u]:
                    stack.append((m, u, False))
                for v in T[u]:
                    if v == p or m == v:
                        continue
                    stack.append((v, u, False))
            else:
                for v in T[u]:
                    if v != p:
                        size[u] += size[v]
    for v in T[centroid]:
        dfs(v, centroid)
        if centroid ^ 1 == v:
            matched = (-size[v], v)
        else:
            heapq.heappush(heap, (-size[v], v))
    ops = []
    while heap:
        s, v = heapq.heappop(heap)
        if dfs_order[v] and dfs_order[matched[1]]:
            leaf1 = dfs_order[v].pop()
            leaf2 = dfs_order[matched[1]].pop()
            ops.append((leaf1, leaf2))
        else:
            continue
        if -matched[0] > 1:
            heapq.heappush(heap, (matched[0] + 1, matched[1]))
        matched = (s + 1, v)
    if matched[1] != -1:
        ops.append((centroid, matched[1]))
    return ops
N, = rint()
T = [[] for _ in range(N)]
for _ in range(N - 1):
    u, v = rint(-1)
    T[u].append(v)
    T[v].append(u)
for op in solve():
    print(op[0] + 1, op[1] + 1)
