import sys
MOD = 998244353

def solve_one(H, W, grid):
    r = [[1 if c == 'A' else 0 for c in row] for row in grid]
    for i in range(H):
        if sum(r[i]) % 2:
            return 0
    for j in range(W):
        if sum((r[i][j] for i in range(H))) % 2:
            return 0
    s = [[0] * W for _ in range(H)]
    for i in range(H):
        cur = 0
        for j in range(W):
            cur ^= r[i][j]
            s[i][j] = cur
    t = [[0] * W for _ in range(H)]
    for j in range(W):
        cur = 0
        for i in range(H):
            cur ^= r[i][j]
            t[i][j] = cur
    adj = [[] for _ in range(H + W)]
    for i in range(H):
        for j in range(W):
            if r[i][j] == 0:
                d = 1 ^ s[i][j] ^ t[i][j]
                u = i
                v = H + j
                adj[u].append((v, d))
                adj[v].append((u, d))
    visited = [False] * (H + W)
    value = [0] * (H + W)
    components = 0
    for start in range(H + W):
        if visited[start]:
            continue
        if not adj[start]:
            visited[start] = True
            components += 1
            continue
        stack = [start]
        visited[start] = True
        value[start] = 0
        while stack:
            u = stack.pop()
            for v, d in adj[u]:
                if not visited[v]:
                    value[v] = value[u] ^ d
                    visited[v] = True
                    stack.append(v)
                elif value[u] ^ value[v] != d:
                    return 0
        components += 1
    free_vars = H + W - (H + W - components)
    ans = pow(2, free_vars, MOD)
    return ans

def solve():
    input_data = sys.stdin.read().split()
    it = iter(input_data)
    T = int(next(it))
    out_lines = []
    for _ in range(T):
        H = int(next(it))
        W = int(next(it))
        grid = [next(it).strip() for _ in range(H)]
        out_lines.append(str(solve_one(H, W, grid)))
    sys.stdout.write('\n'.join(out_lines))
if __name__ == '__main__':
    solve()
