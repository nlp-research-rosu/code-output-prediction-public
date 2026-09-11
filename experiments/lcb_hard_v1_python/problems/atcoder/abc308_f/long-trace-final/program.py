import sys
import heapq

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    M = int(data[1])
    P = list(map(int, data[2:2 + N]))
    L = list(map(int, data[2 + N:2 + N + M]))
    D = list(map(int, data[2 + N + M:2 + N + M + M]))
    P.sort()
    coupons = sorted(zip(L, D), key=lambda x: x[0])
    max_heap = []
    total_cost = 0
    for price in P:
        while coupons and coupons[0][0] <= price:
            l, d = coupons.pop(0)
            heapq.heappush(max_heap, -d)
        if max_heap:
            max_discount = -heapq.heappop(max_heap)
            total_cost += price - max_discount
        else:
            total_cost += price
    print(total_cost)
if __name__ == '__main__':
    main()
