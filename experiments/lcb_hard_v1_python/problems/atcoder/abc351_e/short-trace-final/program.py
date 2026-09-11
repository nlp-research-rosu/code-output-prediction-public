"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc351/tasks/abc351_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc351/tasks/abc351_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import sys
input = sys.stdin.readline

def f1(a: list) -> int:
    a.sort()
    num = 0
    sum_ = 0
    len_ = len(a)
    for i in range(len_):
        num += i * a[i] - sum_
        sum_ += a[i]
    return num

def f2(a: list) -> int:
    len_ = len(a)
    for i in range(len_):
        cnt1, cnt2 = (a[i][0], a[i][1])
        a[i][0] = cnt1 + cnt2
        a[i][1] = cnt1 - cnt2
    vx = [x for x, y in a]
    vy = [y for x, y in a]
    return f1(vx) + f1(vy)
N = int(input())
A = [list(map(int, input().split())) for _ in range(N)]
odd, even = ([], [])
for i in range(N):
    if (A[i][0] + A[i][1]) % 2 == 0:
        even.append(A[i])
    else:
        odd.append(A[i])
print((f2(odd) + f2(even)) // 2)
