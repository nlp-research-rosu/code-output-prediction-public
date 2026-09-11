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
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
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
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'dp': dp, 'i': i, 'num': num}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        dp[i] = a[i] + p * num
        num += dp[i]
        dp[i] %= mod
        num %= mod
    print(dp[0])
if __name__ == '__main__':
    main()
