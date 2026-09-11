import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
heights = data[1:]
stack = []
area = 0
answer = []
for height in heights:
    width = 1
    while stack and stack[-1][0] <= height:
        previous_height, previous_width = stack.pop()
        area -= previous_height * previous_width
        width += previous_width
    stack.append((height, width))
    area += height * width
    answer.append(area + 1)
print(*answer)
