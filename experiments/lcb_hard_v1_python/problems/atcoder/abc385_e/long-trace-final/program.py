import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
graph = [[] for _ in range(n)]
for index in range(1, len(data), 2):
    left, right = (data[index] - 1, data[index + 1] - 1)
    graph[left].append(right)
    graph[right].append(left)
degrees = [len(neighbors) for neighbors in graph]
largest = 0
for center in range(n):
    capacities = sorted((degrees[neighbor] - 1 for neighbor in graph[center]), reverse=True)
    for branch_count, leaves in enumerate(capacities, 1):
        if leaves == 0:
            break
        largest = max(largest, 1 + branch_count * (leaves + 1))
print(n - largest)
