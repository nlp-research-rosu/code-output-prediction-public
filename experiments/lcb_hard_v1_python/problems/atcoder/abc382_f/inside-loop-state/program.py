import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.read

def main():
    data = input().split()
    idx = 0
    H = int(data[idx])
    idx += 1
    W = int(data[idx])
    idx += 1
    N = int(data[idx])
    idx += 1
    bars = []
    for _ in range(N):
        R = int(data[idx])
        idx += 1
        C = int(data[idx])
        idx += 1
        L = int(data[idx])
        idx += 1
        bars.append((R, C, L))
    row_occupied = [set() for _ in range(H + 2)]
    current_row = [0] * N
    for i in range(N):
        R, C, L = bars[i]
        for j in range(C, C + L):
            row_occupied[R].add(j)
        current_row[i] = R
    from collections import defaultdict
    grid = defaultdict(set)
    current_row = []
    H = int(data[0])
    W = int(data[1])
    N = int(data[2])
    bars = []
    for i in range(N):
        R = int(data[3 + 3 * i])
        C = int(data[3 + 3 * i + 1])
        L = int(data[3 + 3 * i + 2])
        bars.append((R, C, L))
    for i in range(N):
        R, C, L = bars[i]
        current_row.append(R)
        for j in range(C, C + L):
            grid[R].add(j)
    current_row = [R for R, C, L in bars]

    def can_move_down(row, col, length, grid):
        for j in range(col, col + length):
            if row + 1 > H:
                return False
            if j in grid[row + 1]:
                return False
        return True
    moved = True
    for _ in range(1000):
        moved = False
        for i in range(N):
            R, C, L = bars[i]
            if current_row[i] + 1 > H:
                continue
            can_move = True
            for j in range(C, C + L):
                if j in grid[current_row[i] + 1]:
                    can_move = False
                    break
            if can_move:
                current_row[i] += 1
                for j in range(C, C + L):
                    grid[current_row[i] - 1].remove(j)
                for j in range(C, C + L):
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'C': C, 'L': L, 'R': R, 'bars': bars, 'current_row': current_row, 'i': i, 'j': j, 'moved': moved}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    grid[current_row[i]].add(j)
                moved = True
        if not moved:
            break
    for r in current_row:
        print(r)
main()
