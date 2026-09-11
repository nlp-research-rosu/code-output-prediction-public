import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import bisect

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    A = list(map(int, data[1:N + 1]))
    Q = int(data[N + 1])
    queries = [(int(data[N + 2 + 2 * i]), int(data[N + 2 + 2 * i + 1])) for i in range(Q)]
    sleep_intervals = []
    for i in range((N - 1) // 2):
        start = A[2 * i + 1]
        end = A[2 * i + 2]
        sleep_intervals.append((start, end))
    prefix_sleep = [0] * (len(sleep_intervals) + 1)
    for i, (s, e) in enumerate(sleep_intervals):
        prefix_sleep[i + 1] = prefix_sleep[i] + (e - s)

    def total_sleep_time(t):
        idx = bisect.bisect_right(A, t) - 1
        if idx < 0:
            return 0
        i = idx // 2
        if i >= len(sleep_intervals):
            return prefix_sleep[-1]
        s, e = sleep_intervals[i]
        if t < s:
            return prefix_sleep[i]
        return prefix_sleep[i] + (t - s)

    def sleep_in_range(l, r):
        total_r = total_sleep_time(r)
        total_l = total_sleep_time(l)
        return total_r - total_l
    results = []
    for l, r in queries:
        _lcb_count[0] += 1
        result = sleep_in_range(l, r)
        results.append(str(result))
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'l': l, 'r': r, 'results': results}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print('\n'.join(results))
if __name__ == '__main__':
    main()
