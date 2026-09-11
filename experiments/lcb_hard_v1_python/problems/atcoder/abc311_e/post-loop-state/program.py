import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.read

def main():
    data = input().split()
    H = int(data[0])
    W = int(data[1])
    N = int(data[2])
    holes = [[False] * (W + 1) for _ in range(H + 1)]
    index = 3
    for _ in range(N):
        a = int(data[index])
        b = int(data[index + 1])
        holes[a][b] = True
        index += 2
    dp = [[0] * (W + 1) for _ in range(H + 1)]
    count = 0
    for i in range(1, H + 1):
        for j in range(1, W + 1):
            _lcb_count[0] += 1
            if not holes[i][j]:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1])
                count += dp[i][j]
            else:
                dp[i][j] = 0
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'count': count, 'dp': dp, 'i': i, 'j': j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    print(count)
if __name__ == '__main__':
    main()
