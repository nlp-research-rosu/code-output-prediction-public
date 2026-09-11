"""
oj（online-judge-tools）の使い方について

1. テストケースをダウンロード
2. サンプルが合っているかジャッジする
3. 提出する

oj d https://atcoder.jp/contests/abc369/tasks/abc369_e
oj t -c "python3 E.py"
oj s https://atcoder.jp/contests/abc369/tasks/abc369_e E.py --guess-python-interpreter pypy

※test/ が既に作成されている場合は下記コマンドで test/ を削除する
rm -rf test/
"""
import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from itertools import permutations
input = sys.stdin.readline
sys.setrecursionlimit(10 ** 6)
N, M = map(int, input().split())
G = [[] for _ in range(N)]
bridges = []
for _ in range(M):
    a, b, c = map(int, input().split())
    a -= 1
    b -= 1
    G[a].append((b, c))
    G[b].append((a, c))
    bridges.append((a, b, c))
Q = int(input())
Z = []
for _ in range(Q):
    k = int(input())
    query = sorted(list(map(lambda x: int(x) - 1, input().split())))
    Z.append(query)

def warshall_floyd(G: list) -> list:
    N = len(G)
    INF = 10 ** 18
    dist = [[INF] * N for _ in range(N)]
    for i in range(N):
        dist[i][i] = 0
        for b, c in G[i]:
            dist[i][b] = min(c, dist[i][b])
    for k in range(N):
        for i in range(N):
            for j in range(N):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
    return dist

def main() -> None:
    dist = warshall_floyd(G)
    for i in range(Q):
        ans = 10 ** 18
        query = Z[i]
        k = len(query)
        for perm in permutations(query):
            x = [bridges[v] for v in perm]
            for bit in range(1 << k):
                sum_ = 0
                y = []
                for j in range(k):
                    if bit & 1 << j:
                        y.append((x[j][1], x[j][0], x[j][2]))
                    else:
                        y.append(x[j])
                for a, b, c in y:
                    sum_ += c
                for j in range(k - 1):
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'bit': bit, 'j': j, 'perm': perm, 'sum_': sum_, 'y': y}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    sum_ += dist[y[j][1]][y[j + 1][0]]
                sum_ += dist[0][y[0][0]]
                sum_ += dist[y[-1][1]][N - 1]
                ans = min(ans, sum_)
        print(ans)
if __name__ == '__main__':
    main()
