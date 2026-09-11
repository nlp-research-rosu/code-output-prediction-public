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
            if 0 <= next_row < height and 0 <= next_column < width:
                next_index = next_row * width + next_column
                if not visited[next_index]:
                    visited[next_index] = True
                    heapq.heappush(queue, (elevation[next_index], next_index))
    print(remaining)
