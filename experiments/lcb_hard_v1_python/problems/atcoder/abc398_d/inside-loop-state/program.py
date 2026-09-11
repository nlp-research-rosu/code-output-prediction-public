import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    R = int(input[1])
    C = int(input[2])
    S = input[3]
    directions = {'N': (-1, 0), 'W': (0, -1), 'S': (1, 0), 'E': (0, 1)}
    current_r = 0
    current_c = 0
    seen = set()
    seen.add((0, 0))
    res = []
    for c in S:
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'c': c, 'current_c': current_c, 'current_r': current_r, 'res': res, 'sorted(seen)': sorted(seen), 'target_c': target_c, 'target_r': target_r}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        dr, dc = directions[c]
        current_r += dr
        current_c += dc
        target_r = current_r - R
        target_c = current_c - C
        if (target_r, target_c) in seen:
            res.append('1')
        else:
            res.append('0')
        seen.add((current_r, current_c))
    print(''.join(res))
if __name__ == '__main__':
    main()
