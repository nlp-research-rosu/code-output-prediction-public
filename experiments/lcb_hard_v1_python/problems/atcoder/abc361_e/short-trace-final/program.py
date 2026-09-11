import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
graph = [[] for _ in range(n)]
total = 0
for index in range(1, len(data), 3):
    left, right, cost = (data[index] - 1, data[index + 1] - 1, data[index + 2])
    graph[left].append((right, cost))
    graph[right].append((left, cost))
    total += cost

def farthest(start):
    best = (0, start)
    stack = [(start, -1, 0)]
    while stack:
        node, parent, distance = stack.pop()
        if distance > best[0]:
            best = (distance, node)
        for neighbor, cost in graph[node]:
            if neighbor != parent:
                stack.append((neighbor, node, distance + cost))
    return best
_, endpoint = farthest(0)
diameter, _ = farthest(endpoint)
print(2 * total - diameter)
