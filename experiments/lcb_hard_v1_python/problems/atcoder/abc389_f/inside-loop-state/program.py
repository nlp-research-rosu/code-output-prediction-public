import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    input = sys.stdin.read().split()
    ptr = 0
    N = int(input[ptr])
    ptr += 1
    contests = []
    for _ in range(N):
        L = int(input[ptr])
        R = int(input[ptr + 1])
        contests.append((L, R))
        ptr += 2
    Q = int(input[ptr])
    ptr += 1
    queries = []
    for _ in range(Q):
        queries.append(int(input[ptr]))
        ptr += 1
    for X in queries:
        c = 0
        for L, R in contests:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'L': L, 'R': R, 'X': X, 'c': c, 'contests': contests}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if X + c >= L and X + c <= R:
                c += 1
        print(X + c)
if __name__ == '__main__':
    main()
