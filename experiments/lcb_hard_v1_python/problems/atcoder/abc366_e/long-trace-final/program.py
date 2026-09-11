import bisect
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, limit = data[:2]
xs = sorted(data[2::2])
ys = sorted(data[3::2])

def distance_values(coordinates):
    median = coordinates[len(coordinates) // 2]

    def distance(position):
        return sum((abs(position - value) for value in coordinates))
    if distance(median) > limit:
        return []
    low = coordinates[0] - limit - 1
    high = median
    while high - low > 1:
        middle = (low + high) // 2
        if distance(middle) <= limit:
            high = middle
        else:
            low = middle
    left = high
    low = median
    high = coordinates[-1] + limit + 1
    while high - low > 1:
        middle = (low + high) // 2
        if distance(middle) <= limit:
            low = middle
        else:
            high = middle
    right = low
    current = distance(left)
    count_left = bisect.bisect_right(coordinates, left)
    result = []
    for position in range(left, right + 1):
        result.append(current)
        current += count_left - (len(coordinates) - count_left)
        count_left = bisect.bisect_right(coordinates, position + 1)
    return result
x_values = distance_values(xs)
y_values = sorted(distance_values(ys))
answer = sum((bisect.bisect_right(y_values, limit - value) for value in x_values))
print(answer)
