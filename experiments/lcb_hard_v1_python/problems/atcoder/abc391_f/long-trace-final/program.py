import sys
import heapq

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    n = int(data[0])
    k = int(data[1])
    A = list(map(int, data[2:n + 2]))
    B = list(map(int, data[n + 2:2 * n + 2]))
    C = list(map(int, data[2 * n + 2:3 * n + 2]))
    M = 700
    T = 700
    A_sorted = sorted(A, reverse=True)
    A_top = A_sorted[:M]
    C_sorted = sorted(C, reverse=True)
    C_top = C_sorted[:M]
    B_sorted = sorted(B, reverse=True)
    B_top = B_sorted[:T]
    heap = []
    for a in A_top:
        for c in C_top:
            if B_top:
                j = 0
                b = B_top[j]
                val = a * b + b * c + c * a
                heapq.heappush(heap, (-val, a, c, j))
    count = 0
    while heap:
        neg_val, a, c, j = heapq.heappop(heap)
        count += 1
        if count == k:
            print(-neg_val)
            return
        j += 1
        if j < len(B_top):
            b = B_top[j]
            val = a * b + b * c + c * a
            heapq.heappush(heap, (-val, a, c, j))
    print(0)
if __name__ == '__main__':
    main()
