"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc346/tasks/abc346_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc346/tasks/abc346_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.readline
from collections import defaultdict

def main() -> None:
    h, w, m = map(int, input().split())
    l = [list(map(int, input().split())) for _ in range(m)][::-1]
    d = defaultdict(int)
    for i in range(2 * 10 ** 5 + 1):
        d[i] = 0
    d[0] = h * w
    sx, sy = (set(), set())
    for i in range(m):
        t, a, c = l[i]
        if t == 1:
            if not 1 <= a <= h:
                continue
            if a in sx:
                continue
            sx.add(a)
            d[c] += w - len(sy)
        if t == 2:
            if not 1 <= a <= w:
                continue
            if a in sy:
                continue
            sy.add(a)
            d[c] += h - len(sx)
    p = []
    cnt = 0
    for k, v in d.items():
        if v != 0 and k != 0:
            cnt += v
    d[0] = h * w - cnt
    for k, v in d.items():
        _lcb_count[0] += 1
        if v != 0:
            p.append((k, v))
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'k': k, 'p': p, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    p.sort(key=lambda x: x[0])
    print(len(p))
    for i in p:
        print(i[0], i[1])
if __name__ == '__main__':
    main()
