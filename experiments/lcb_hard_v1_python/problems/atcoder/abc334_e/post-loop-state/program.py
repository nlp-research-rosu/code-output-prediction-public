import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import sys
from collections import deque
input = sys.stdin.read
MOD = 998244353

def main():
    data = input().split()
    H = int(data[0])
    W = int(data[1])
    grid = data[2:]
    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    parent = {}

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def union(u, v):
        pu, pv = (find(u), find(v))
        if pu != pv:
            parent[pv] = pu
    green_id = 0
    green_cells = []
    for i in range(H):
        for j in range(W):
            if grid[i][j] == '#':
                parent[i, j] = (i, j)
                green_cells.append((i, j))
                green_id += 1
    for i in range(H):
        for j in range(W):
            if grid[i][j] == '#':
                for dx, dy in dirs:
                    ni, nj = (i + dx, j + dy)
                    if 0 <= ni < H and 0 <= nj < W and (grid[ni][nj] == '#'):
                        union((i, j), (ni, nj))
    component_count = {}
    for i, j in green_cells:
        root = find((i, j))
        if root not in component_count:
            component_count[root] = 0
        component_count[root] += 1
    num_green_components = len(component_count)
    num_red_cells = 0
    red_components = []
    for i in range(H):
        for j in range(W):
            if grid[i][j] == '.':
                num_red_cells += 1
                neighbors = set()
                for dx, dy in dirs:
                    _lcb_count[0] += 1
                    ni, nj = (i + dx, j + dy)
                    if 0 <= ni < H and 0 <= nj < W and (grid[ni][nj] == '#'):
                        root = find((ni, nj))
                        neighbors.add(root)
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'j': j, 'nj': nj, 'num_red_cells': num_red_cells, 'red_components': red_components}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if len(neighbors) == 0:
                    red_components.append(num_green_components + 1)
                elif len(neighbors) == 1:
                    red_components.append(num_green_components)
                else:
                    red_components.append(num_green_components - len(neighbors) + 1)
    total = sum(red_components) % MOD
    inv_num_red_cells = pow(num_red_cells, MOD - 2, MOD)
    expected_value = total * inv_num_red_cells % MOD
    print(expected_value)
if __name__ == '__main__':
    main()
