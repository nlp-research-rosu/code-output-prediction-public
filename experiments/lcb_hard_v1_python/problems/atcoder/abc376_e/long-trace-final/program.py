import heapq
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
test_count = data[0]
index = 1
answers = []
for _ in range(test_count):
    n, k = (data[index], data[index + 1])
    index += 2
    first = data[index:index + n]
    index += n
    second = data[index:index + n]
    index += n
    selected = []
    total = 0
    answer = 10 ** 30
    for maximum, value in sorted(zip(first, second)):
        heapq.heappush(selected, -value)
        total += value
        if len(selected) > k:
            total += heapq.heappop(selected)
        if len(selected) == k:
            answer = min(answer, maximum * total)
    answers.append(answer)
print(*answers, sep='\n')
