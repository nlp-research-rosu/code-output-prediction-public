import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
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
            _lcb_count[0] += 1
            if B_top:
                j = 0
                b = B_top[j]
                val = a * b + b * c + c * a
                heapq.heappush(heap, (-val, a, c, j))
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'A_top': A_top, 'B_top': B_top, 'C_top': C_top, 'a': a, 'c': c, 'heap[:8]': heap[:8], 'len(heap)': len(heap)}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
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
