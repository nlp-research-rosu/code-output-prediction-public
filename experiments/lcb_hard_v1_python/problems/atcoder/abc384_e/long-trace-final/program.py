import heapq
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
height, width, multiplier = data[:3]
start_row, start_column = (data[3] - 1, data[4] - 1)
strengths = data[5:]
start = start_row * width + start_column
strength = strengths[start]
visited = [False] * (height * width)
visited[start] = True
queue = []

def expose(row, column):
    if 0 <= row < height and 0 <= column < width:
        index = row * width + column
        if not visited[index]:
            visited[index] = True
            heapq.heappush(queue, (strengths[index], index))
expose(start_row - 1, start_column)
expose(start_row + 1, start_column)
expose(start_row, start_column - 1)
expose(start_row, start_column + 1)
while queue and queue[0][0] * multiplier < strength:
    value, index = heapq.heappop(queue)
    strength += value
    row, column = divmod(index, width)
    expose(row - 1, column)
    expose(row + 1, column)
    expose(row, column - 1)
    expose(row, column + 1)
print(strength)
