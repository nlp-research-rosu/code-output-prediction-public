import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    K = int(input[1])
    A = list(map(int, input[2:2 + N]))
    if N == 0:
        return
    max_A = max(A)
    freq = [0] * (max_A + 1)
    for x in A:
        freq[x] += 1
    cnt = [0] * (max_A + 1)
    for d in range(1, max_A + 1):
        for multiple in range(d, max_A + 1, d):
            cnt[d] += freq[multiple]
    ans = [0] * (max_A + 1)
    for d in range(max_A, 0, -1):
        if cnt[d] >= K:
            for multiple in range(d, max_A + 1, d):
                _lcb_count[0] += 1
                if ans[multiple] == 0:
                    ans[multiple] = d
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'K': K, 'ans[:80]': ans[:80], 'cnt[:80]': cnt[:80], 'd': d, 'max_A': max_A, 'multiple': multiple}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
    for x in A:
        print(ans[x])
if __name__ == '__main__':
    main()
