import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import bisect

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    A = list(map(int, input[1:N + 1]))
    pos = [[] for _ in range(N + 1)]
    for idx, val in enumerate(A):
        pos[val].append(idx + 1)
    ans = 0
    for x in range(1, N + 1):
        prev = x - 1
        if prev == 0:
            prev_positions = []
        else:
            prev_positions = pos[prev]
        regions = []
        if not prev_positions:
            regions.append((1, N))
        else:
            regions.append((1, prev_positions[0] - 1))
            for i in range(1, len(prev_positions)):
                a = prev_positions[i - 1] + 1
                b = prev_positions[i] - 1
                regions.append((a, b))
            regions.append((prev_positions[-1] + 1, N))
        for a, b in regions:
            if a > b:
                continue
            x_positions = pos[x]
            left = bisect.bisect_left(x_positions, a)
            right_idx = bisect.bisect_right(x_positions, b)
            if left >= right_idx:
                continue
            sum_without = 0
            prev_gap_end = a - 1
            for pos_x in x_positions[left:right_idx]:
                _lcb_count[0] += 1
                l = prev_gap_end + 1
                r = pos_x - 1
                if l <= r:
                    length = r - l + 1
                    sum_without += length * (length + 1) // 2
                prev_gap_end = pos_x
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'ans': ans, 'b': b, 'left': left, 'pos_x': pos_x, 'prev_gap_end': prev_gap_end, 'right_idx': right_idx, 'sum_without': sum_without, 'x_positions': x_positions}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            l = prev_gap_end + 1
            r = b
            if l <= r:
                length = r - l + 1
                sum_without += length * (length + 1) // 2
            total = (b - a + 1) * (b - a + 2) // 2
            contribution = total - sum_without
            ans += contribution
    print(ans)
if __name__ == '__main__':
    main()
