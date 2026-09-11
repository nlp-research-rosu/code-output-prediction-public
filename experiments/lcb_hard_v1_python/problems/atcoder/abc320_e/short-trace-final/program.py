import sys
import heapq

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    M = int(data[1])
    events = []
    index = 2
    for _ in range(M):
        T = int(data[index])
        W = int(data[index + 1])
        S = int(data[index + 2])
        events.append((T, W, S))
        index += 3
    available = list(range(1, N + 1))
    heapq.heapify(available)
    unavailable = []
    result = [0] * (N + 1)
    for T, W, S in events:
        while unavailable and unavailable[0][0] <= T:
            return_time, person = heapq.heappop(unavailable)
            heapq.heappush(available, person)
        if available:
            person = heapq.heappop(available)
            result[person] += W
            heapq.heappush(unavailable, (T + S, person))
    for i in range(1, N + 1):
        print(result[i])
if __name__ == '__main__':
    main()
