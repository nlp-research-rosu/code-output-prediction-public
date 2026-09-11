import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
from collections import defaultdict, deque

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    M = int(data[1])
    X = list(map(int, data[2:2 + M]))
    tour = X
    total_length = 0
    prev = tour[0]
    for i in range(1, M):
        a = prev
        b = tour[i]
        clockwise = (b - a + N) % N
        counter = (a - b + N) % N
        dist = min(clockwise, counter)
        total_length += dist
        prev = b
    consecutive_pairs = []
    for i in range(M - 1):
        a = tour[i]
        b = tour[i + 1]
        consecutive_pairs.append((a, b))
    diff = [0] * (N + 2)
    for a, b in consecutive_pairs:
        clockwise = (b - a + N) % N
        counter = (a - b + N) % N
        if clockwise < counter:
            extra = counter - clockwise
            if b > a:
                start = a
                end = b - 1
                diff[start] += extra
                diff[end + 1] -= extra
            else:
                diff[a] += extra
                diff[N + 1] -= extra
                if b > 1:
                    diff[1] += extra
                    diff[b] -= extra
        else:
            extra = clockwise - counter
            if a > b:
                start = b
                end = a - 1
                diff[start] += extra
                diff[end + 1] -= extra
            else:
                diff[b] += extra
                diff[N + 1] -= extra
                if a > 1:
                    diff[1] += extra
                    diff[a] -= extra
    extra_cost = [0] * (N + 1)
    for i in range(1, N + 1):
        extra_cost[i] = extra_cost[i - 1] + diff[i]
    min_total = float('inf')
    for i in range(1, N + 1):
        _lcb_count[0] += 1
        current = total_length + extra_cost[i]
        if current < min_total:
            min_total = current
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'current': current, 'extra_cost': extra_cost, 'i': i, 'min_total': min_total, 'total_length': total_length}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(min_total)
if __name__ == '__main__':
    main()
