import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
MOD = 998244353

def main():
    import sys
    from collections import defaultdict
    N, K = map(int, sys.stdin.readline().split())
    A = list(map(int, sys.stdin.readline().split()))
    prefix = 0
    total = 1
    prefix_map = defaultdict(int)
    prefix_map[0] = 1
    for i in range(1, N + 1):
        _lcb_count[0] += 1
        prefix += A[i - 1]
        c = prefix - K
        sum_forbidden = prefix_map.get(c, 0)
        dp_i = (total - sum_forbidden) % MOD
        total = (total + dp_i) % MOD
        prefix_map[prefix] = (prefix_map[prefix] + dp_i) % MOD
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'c': c, 'dp_i': dp_i, 'i': i, 'prefix': prefix, 'sum_forbidden': sum_forbidden, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(dp_i % MOD)
if __name__ == '__main__':
    main()
