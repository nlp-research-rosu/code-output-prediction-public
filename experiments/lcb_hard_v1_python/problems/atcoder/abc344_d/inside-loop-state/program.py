import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read
    data = input().splitlines()
    T = data[0]
    N = int(data[1])
    bags = []
    idx = 2
    for _ in range(N):
        parts = data[idx].split()
        A_i = int(parts[0])
        strings = parts[1:]
        bags.append(strings)
        idx += 1
    len_T = len(T)
    INF = float('inf')
    dp = [[INF] * (len_T + 1) for _ in range(N + 1)]
    dp[0][0] = 0
    for i in range(1, N + 1):
        for j in range(len_T + 1):
            dp[i][j] = min(dp[i][j], dp[i - 1][j])
            for s in bags[i - 1]:
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'T': T, 'bags': bags, 'i': i, 'j': j, 'len_s': len_s, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                len_s = len(s)
                if j + len_s <= len_T and T[j:j + len_s] == s:
                    dp[i][j + len_s] = min(dp[i][j + len_s], dp[i - 1][j] + 1)
    result = dp[N][len_T]
    print(result if result != INF else -1)
if __name__ == '__main__':
    main()
