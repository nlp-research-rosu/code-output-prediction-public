import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def get_bitmask(row, col, W):
    return 1 << (row - 1) * W + (col - 1)

def count_paths(row, col, steps_left, visited_mask, grid, W, H):
    if steps_left == 0:
        return 1
    if steps_left < 0:
        return 0
    count = 0
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        _lcb_count[0] += 1
        new_row = row + dr
        new_col = col + dc
        if 1 <= new_row <= H and 1 <= new_col <= W:
            if grid[new_row - 1][new_col - 1] == '.':
                bit = get_bitmask(new_row, new_col, W)
                if not visited_mask & bit:
                    new_mask = visited_mask | bit
                    count += count_paths(new_row, new_col, steps_left - 1, new_mask, grid, W, H)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'col': col, 'count': count, 'dc': dc, 'dr': dr, 'row': row, 'steps_left': steps_left, 'visited_mask': visited_mask}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    return count

def main():
    H, W, K = map(int, sys.stdin.readline().split())
    grid = []
    for _ in range(H):
        grid.append(list(sys.stdin.readline().strip()))
    starting_cells = []
    for i in range(H):
        for j in range(W):
            if grid[i][j] == '.':
                starting_cells.append((i + 1, j + 1))
    total = 0
    for start_row, start_col in starting_cells:
        initial_mask = get_bitmask(start_row, start_col, W)
        total += count_paths(start_row, start_col, K, initial_mask, grid, W, H)
    print(total)
if __name__ == '__main__':
    main()
