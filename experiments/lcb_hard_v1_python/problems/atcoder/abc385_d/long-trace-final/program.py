import bisect
import sys

def main():
    input = sys.stdin.read().split()
    ptr = 0
    N = int(input[ptr])
    ptr += 1
    M = int(input[ptr])
    ptr += 1
    Sx = int(input[ptr])
    ptr += 1
    Sy = int(input[ptr])
    ptr += 1
    x_houses = {}
    y_houses = {}
    for _ in range(N):
        x = int(input[ptr])
        ptr += 1
        y = int(input[ptr])
        ptr += 1
        if x not in x_houses:
            x_houses[x] = []
        x_houses[x].append(y)
        if y not in y_houses:
            y_houses[y] = []
        y_houses[y].append(x)
    for x in x_houses:
        x_houses[x].sort()
    for y in y_houses:
        y_houses[y].sort()
    visited = set()
    current_x, current_y = (Sx, Sy)
    for _ in range(M):
        direction = input[ptr]
        ptr += 1
        C = int(input[ptr])
        ptr += 1
        if direction == 'U':
            new_y = current_y + C
            y_range_start = current_y + 1
            y_range_end = current_y + C
            first = bisect.bisect_left(x_houses.get(current_x, []), y_range_start)
            second = bisect.bisect_right(x_houses.get(current_x, []), y_range_end)
            count = second - first
            for i in range(first, second):
                y = x_houses[current_x][i]
                visited.add((current_x, y))
            current_y = new_y
        elif direction == 'D':
            new_y = current_y - C
            y_range_start = current_y - C
            y_range_end = current_y - 1
            first = bisect.bisect_left(x_houses.get(current_x, []), y_range_start)
            second = bisect.bisect_right(x_houses.get(current_x, []), y_range_end)
            count = second - first
            for i in range(first, second):
                y = x_houses[current_x][i]
                visited.add((current_x, y))
            current_y = new_y
        elif direction == 'R':
            new_x = current_x + C
            x_range_start = current_x + 1
            x_range_end = current_x + C
            first = bisect.bisect_left(y_houses.get(current_y, []), x_range_start)
            second = bisect.bisect_right(y_houses.get(current_y, []), x_range_end)
            count = second - first
            for i in range(first, second):
                x = y_houses[current_y][i]
                visited.add((x, current_y))
            current_x = new_x
        elif direction == 'L':
            new_x = current_x - C
            x_range_start = current_x - C
            x_range_end = current_x - 1
            first = bisect.bisect_left(y_houses.get(current_y, []), x_range_start)
            second = bisect.bisect_right(y_houses.get(current_y, []), x_range_end)
            count = second - first
            for i in range(first, second):
                x = y_houses[current_y][i]
                visited.add((x, current_y))
            current_x = new_x
    print(f'{current_x} {current_y} {len(visited)}')
if __name__ == '__main__':
    main()
