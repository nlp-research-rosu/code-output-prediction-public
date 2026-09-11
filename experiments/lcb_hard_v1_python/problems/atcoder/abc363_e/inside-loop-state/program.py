import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import heapq
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
height, width, years = data[:3]
elevation = data[3:]
visited = [False] * (height * width)
queue = []
for row in range(height):
    for column in range(width):
        if row not in (0, height - 1) and column not in (0, width - 1):
            continue
        index = row * width + column
        if not visited[index]:
            visited[index] = True
            heapq.heappush(queue, (elevation[index], index))
remaining = height * width
for year in range(1, years + 1):
    while queue and queue[0][0] <= year:
        _, index = heapq.heappop(queue)
        remaining -= 1
        row, column = divmod(index, width)
        for next_row, next_column in ((row - 1, column), (row + 1, column), (row, column - 1), (row, column + 1)):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'column': column, 'index': index, 'next_column': next_column, 'next_index': next_index, 'next_row': next_row, 'queue': queue, 'remaining': remaining, 'row': row}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if 0 <= next_row < height and 0 <= next_column < width:
                next_index = next_row * width + next_column
                if not visited[next_index]:
                    visited[next_index] = True
                    heapq.heappush(queue, (elevation[next_index], next_index))
    print(remaining)
