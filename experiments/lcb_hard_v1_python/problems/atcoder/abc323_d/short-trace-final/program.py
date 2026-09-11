import sys
import heapq
from collections import defaultdict

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    n = int(data[0])
    slimes = defaultdict(int)
    for i in range(n):
        s = int(data[1 + 2 * i])
        c = int(data[2 + 2 * i])
        slimes[s] = c
    heap = list(slimes.keys())
    heapq.heapify(heap)
    while heap:
        x = heapq.heappop(heap)
        if slimes[x] < 2:
            continue
        count = slimes[x] // 2
        slimes[2 * x] += count
        slimes[x] -= count * 2
        if slimes[2 * x] > 0:
            heapq.heappush(heap, 2 * x)
    total = sum(slimes.values())
    print(total)
if __name__ == '__main__':
    main()
