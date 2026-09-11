import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from itertools import permutations

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    H = int(data[1])
    W = int(data[2])
    tiles = []
    for i in range(N):
        a = int(data[3 + 2 * i])
        b = int(data[4 + 2 * i])
        tiles.append((a, b))
    from itertools import combinations
    found = False
    for k in range(1, N + 1):
        for subset in combinations(range(N), k):
            total_area = 0
            for i in subset:
                a, b = tiles[i]
                total_area += a * b
            if total_area == H * W:
                selected_tiles = [tiles[i] for i in subset]
                for perm in permutations(selected_tiles):
                    from itertools import product
                    orientations = []
                    for tile in perm:
                        orientations.append([(tile[0], tile[1]), (tile[1], tile[0])])
                    for orient in product(*orientations):
                        grid = [[False for _ in range(W)] for _ in range(H)]

                        def can_place(tile_idx, row, col):
                            h, w = orient[tile_idx]
                            if row + h > H or col + w > W:
                                return False
                            for i in range(row, row + h):
                                for j in range(col, col + w):
                                    if grid[i][j]:
                                        return False
                            for i in range(row, row + h):
                                for j in range(col, col + w):
                                    grid[i][j] = True
                            return True

                        def find_empty():
                            for i in range(H):
                                for j in range(W):
                                    if not grid[i][j]:
                                        return (i, j)
                            return None
                        from copy import deepcopy

                        def backtrack(tile_idx):
                            if tile_idx == len(orient):
                                for row in grid:
                                    if False in row:
                                        return False
                                return True
                            h, w = orient[tile_idx]
                            empty = find_empty()
                            if empty is None:
                                return False
                            row, col = empty
                            if row + h > H or col + w > W:
                                return False
                            for i in range(row, row + h):
                                for j in range(col, col + w):
                                    if grid[i][j]:
                                        return False
                            for i in range(row, row + h):
                                for j in range(col, col + w):
                                    grid[i][j] = True
                            if backtrack(tile_idx + 1):
                                return True
                            for i in range(row, row + h):
                                for j in range(col, col + w):
                                    _lcb_count[0] += 1
                                    grid[i][j] = False
                                if _lcb_count[0] > 1000:
                                    _lcb_sys.stdout.write(_lcb_json.dumps({'col': col, 'empty': empty, 'grid': grid, 'h': h, 'i': i, 'orient': orient, 'w': w}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                                    raise SystemExit
                            return False
                        grid = [[False for _ in range(W)] for _ in range(H)]
                        if backtrack(0):
                            found = True
                            break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
        if found:
            break
    print('Yes' if found else 'No')
if __name__ == '__main__':
    main()
