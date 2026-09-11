"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc326/tasks/abc326_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc326/tasks/abc326_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import sys
input = sys.stdin.readline

def main() -> None:
    n = int(input())
    a = [0] + list(map(int, input().split()))
    mod = 998244353
    dp = [0] * (n + 1)
    p = pow(n, -1, mod)
    num = 0
    for i in reversed(range(n + 1)):
        dp[i] = a[i] + p * num
        num += dp[i]
        dp[i] %= mod
        num %= mod
    print(dp[0])
if __name__ == '__main__':
    main()
