import bisect
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, q = data[:2]
points = sorted(data[2:2 + n])
index = 2 + n
answer = []
for _ in range(q):
    center, count = (data[index], data[index + 1])
    index += 2
    low = -1
    high = 200000001
    while high - low > 1:
        middle = (low + high) // 2
        inside = bisect.bisect_right(points, center + middle) - bisect.bisect_left(points, center - middle)
        if inside >= count:
            high = middle
        else:
            low = middle
    answer.append(high)
print(*answer, sep='\n')
