"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc365/tasks/abc365_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc365/tasks/abc365_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.readline

def check(arg):
    if 1:
        return True
    else:
        return False

def binary_search(left: int, right: int) -> int:
    while right - left > 1:
        mid = (left + right) // 2
        if check(mid):
            left = mid
        else:
            right = mid
    return left

def main() -> None:
    N = int(input())
    A = list(map(int, input().split()))
    ans = 0
    for k in range(40):
        x = [0] * N
        for j in range(N):
            x[j] = A[j] >> k & 1
        dp = [[0] * 2 for _ in range(N + 1)]
        for i in range(N):
            if x[i] == 0:
                dp[i + 1][0] += dp[i][0] + 1
                dp[i + 1][1] += dp[i][1]
            else:
                dp[i + 1][0] += dp[i][1]
                dp[i + 1][1] += dp[i][0] + 1
        cnt = 0
        for i in range(N + 1):
            cnt += dp[i][1]
        for i in range(N):
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'cnt': cnt, 'dp': dp, 'i': i, 'k': k, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            cnt -= x[i]
        ans += cnt * (1 << k)
    print(ans)
if __name__ == '__main__':
    main()
