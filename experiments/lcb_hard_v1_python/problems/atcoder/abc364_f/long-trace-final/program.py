import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, q = data[:2]
queries = []
for index in range(2, len(data), 3):
    left, right, cost = (data[index] - 1, data[index + 1] - 1, data[index + 2])
    queries.append((cost, left, right))
parent = list(range(n))

def find(boundary):
    while parent[boundary] != boundary:
        parent[boundary] = parent[parent[boundary]]
        boundary = parent[boundary]
    return boundary
answer = sum((cost for cost, _, _ in queries))
removed = 0
for cost, left, right in sorted(queries):
    boundary = find(left)
    while boundary < right:
        answer += cost
        removed += 1
        parent[boundary] = find(boundary + 1)
        boundary = parent[boundary]
print(answer if removed == n - 1 else -1)
