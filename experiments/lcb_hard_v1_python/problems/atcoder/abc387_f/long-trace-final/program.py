"""
 ______________________
< this is hidehic0's code >
 ----------------------
   \\
    \\
        .--.
       |o_o |
       |:_/ |
      //   \\ \\
     (|     | )
    /'\\_   _/`\\
    \\___)=(___/

┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳
┃                 ┳━━━━┳       ┃
┃    私は人間です ┃ ✔  ┃       ┃
┃                 ┻━━━━┻       ┃
┻━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┻
"""
import bisect
import copy
import heapq
import math
import sys
from collections import Counter, defaultdict, deque
from itertools import accumulate, combinations, permutations
from math import gcd, lcm, pi
from operator import itemgetter
from typing import Any
sys.setrecursionlimit(5 * 10 ** 5)
import io
import os
import sys
from typing import Any

def s() -> str:
    """一行に一つのstringをinput"""
    return input()

def sl() -> list[str]:
    """一行に複数のstringをinput"""
    return s().split()

def ii() -> int:
    """一つのint"""
    return int(s())

def il(add_num: int=0) -> list[int]:
    """一行に複数のint"""
    return list(map(lambda i: int(i) + add_num, sl()))

def li(n: int, func, *args: list[Any]) -> list[list[Any]]:
    """複数行の入力をサポート"""
    return [func(*args) for _ in [0] * n]

def is_prime(n: int) -> int:
    """素数判定

    計算量は定数時間です。正確には、繰り返し二乗法の計算量によりです
    アルゴリズムはミラーラビンの素数判定を使用しています
    nが2^64を越えると動作しません
    """
    if n == 1:
        return False

    def f(a, t, n):
        x = pow(a, t, n)
        nt = n - 1
        while t != nt and x not in (1, nt):
            x = pow(x, 2, n)
            t <<= 1
        return t & 1 or x == nt
    if n == 2:
        return True
    elif n % 2 == 0:
        return False
    d = n - 1
    d >>= 1
    while d & 1 == 0:
        d >>= 1
    checklist = [2, 7, 61] if 2 ** 32 > n else [2, 325, 9375, 28178, 450775, 9780504, 1795265022]
    for i in checklist:
        if i >= n:
            break
        if not f(i, d, n):
            return False
    return True

def eratosthenes(n: int) -> list[int]:
    """エラトステネスの篩

    n以下の素数を列挙します
    計算量は、O(n log log n)です
    先程の素数判定法で列挙するよりも、少し速いです
    列挙した素数は昇順に並んでいます
    """
    primes = [True] * (n + 1)
    primes[0], primes[1] = (False, False)
    i = 2
    while i ** 2 <= n:
        if primes[i]:
            for k in range(i * 2, n + 1, i):
                primes[k] = False
        i += 1
    return [i for i, p in enumerate(primes) if p]

def calc_divisors(n: int) -> list[int]:
    """約数列挙

    Nの約数列挙します
    計算量は、√Nです
    約数は昇順に並んでいます
    """
    result = []
    for i in range(1, n + 1):
        if i * i > n:
            break
        if n % i != 0:
            continue
        result.append(i)
        if n // i != i:
            result.append(n // i)
    return sorted(result)

def factorization(n: int) -> list[list[int]]:
    """素因数分解

    nを素因数分解します
    計算量は、√Nです(要改善)
    複数回素因数分解を行なう場合は、√N以下の素数を列挙したので試し割りした法が速いです
    """
    result = []
    tmp = n
    for i in range(2, int(-(-n ** 0.5 // 1)) + 1):
        if tmp % i == 0:
            cnt = 0
            while tmp % i == 0:
                cnt += 1
                tmp //= i
            result.append([i, cnt])
    if tmp != 1:
        result.append([tmp, 1])
    if result == []:
        result.append([n, 1])
    return result

def factorization_plural(L: list[int]) -> list[list[list[int]]]:
    """複数の数の素因数分解

    計算量は、O(N * (√max(L) log log √max(L)))
    みたいな感じです

    最初に素数を列挙するため、普通の素因数分解より効率がいいです
    """
    primes = eratosthenes(int(max(L) ** 0.5) + 20)

    def solve(n):
        t = []
        for p in primes:
            if n % p == 0:
                cnt = 0
                while n % p == 0:
                    cnt += 1
                    n //= p
                t.append([p, cnt])
        if n != 1:
            t.append([n, 1])
        if t == []:
            t.append([n, 1])
        return t
    return [solve(n) for n in L]

def simple_sigma(n: int) -> int:
    """1からnまでの和

    つまり和の公式
    """
    return n * (n + 1) // 2

def comb(n: int, r: int, mod: int | None=None) -> int:
    """二項係数

    高速なはずの二項係数
    modを指定すれば、mod付きになる
    """
    a = 1
    for i in range(n - r + 1, n + 1):
        a *= i
        if mod:
            a %= mod
    b = 1
    for i in range(1, r + 1):
        b *= i
        if mod:
            b %= mod
    if mod:
        return a * pow(b, -1, mod) % mod
    else:
        return a * b
from typing import Any

def create_array1(n: int, default=0) -> list[Any]:
    """1次元配列を初期化する関数"""
    return [default] * n

def create_array2(a: int, b: int, default=0) -> list[list[Any]]:
    """2次元配列を初期化する関数"""
    return [[default] * b for _ in [0] * a]

def create_array3(a: int, b: int, c: int, default=0) -> list[list[list[Any]]]:
    """3次元配列を初期化する関数"""
    return [[[default] * c for _ in [0] * b] for _ in [0] * a]
from collections.abc import Callable

def binary_search(fn: Callable[[int], bool], right: int=0, left: int=-1, return_left: bool=True) -> int:
    """二分探索の抽象的なライブラリ

    評価関数の結果に応じて、二分探索する
    最終的にはleftを出力します

    関数のテンプレート
    def check(mid:int):
        if A[mid] > x:
            return True
        else:
            return False

    midは必須です。それ以外はご自由にどうぞ
    """
    while right - left > 1:
        mid = (left + right) // 2
        if fn(mid):
            left = mid
        else:
            right = mid
    return left if return_left else right

def mod_add(a: int, b: int, mod: int) -> int:
    """足し算してmodを取った値を出力

    O(1)
    """
    return (a + b) % mod

def mod_sub(a: int, b: int, mod: int) -> int:
    """引き算してmodを取った値を出力

    O(1)
    """
    return (a - b) % mod

def mod_mul(a: int, b: int, mod: int) -> int:
    """掛け算してmodを取った値を出力

    O(1)
    """
    return a * b % mod

def mod_div(a: int, b: int, mod: int) -> int:
    """割り算してmodを取った値を出力

    フェルマーの小定理を使って計算します
    O(log mod)
    """
    return a * pow(b, -1, mod) % mod

class ModInt:

    def __init__(self, x: int, mod: int=998244353) -> None:
        """ModInt

        リストで使うと参照渡しになるので注意
        """
        self.x = x % mod
        self.mod = mod

    def val(self) -> int:
        return self.x

    def rhs(self, rhs) -> int:
        return rhs.x if isinstance(rhs, ModInt) else rhs

    def __add__(self, rhs) -> int:
        return mod_add(self.x, self.rhs(rhs), self.mod)

    def __iadd__(self, rhs) -> 'ModInt':
        self.x = self.__add__(rhs)
        return self

    def __sub__(self, rhs) -> int:
        return mod_sub(self.x, self.rhs(rhs), self.mod)

    def __isub__(self, rhs) -> 'ModInt':
        self.x = self.__sub__(rhs)
        return self

    def __mul__(self, rhs):
        return mod_mul(self.x, self.rhs(rhs), self.mod)

    def __imul__(self, rhs):
        self.x = self.__mul__(rhs)
        return self

    def __truediv__(self, rhs):
        return mod_div(self.x, self.rhs(rhs), self.mod)

    def __itruediv__(self, rhs):
        self.x = self.__truediv__(rhs)
        return self

    def __floordiv__(self, rhs):
        return self.x // self.rhs(rhs) % self.mod

    def __ifloordiv__(self, rhs):
        self.x = self.__floordiv__(rhs)
        return self

    def __pow__(self, rhs):
        return pow(self.x, self.rhs(rhs), self.mod)

    def __eq__(self, rhs) -> bool:
        return self.rhs(rhs) == self.x

    def __ne__(self, rhs) -> bool:
        return self.rhs(rhs) != self.x

    def __hash__(self) -> int:
        return hash(self.x)

def YesNoTemplate(state: bool, upper: bool=False) -> str:
    """YesNo関数のテンプレート

    stateがTrueなら、upperに応じてYes,YESをreturn
    stateがFalseなら、upperに応じてNo,NOをreturnする
    """
    YES = ['Yes', 'YES']
    NO = ['No', 'NO']
    if state:
        return YES[int(upper)]
    else:
        return NO[int(upper)]

def YN(state: bool, upper: bool=False) -> None:
    """
    先程のYesNoTemplate関数の結果を出力する
    """
    res = YesNoTemplate(state, upper)
    print(res)

def YE(state: bool, upper: bool=False) -> bool | None:
    """
    boolがTrueならYesを出力してexit
    """
    if not state:
        return False
    YN(True, upper)
    exit()

def NE(state: bool, upper: bool=False) -> bool | None:
    """
    boolがTrueならNoを出力してexit
    """
    if not state:
        return False
    YN(False, upper)
    exit()
from collections.abc import Callable

def coordinate_check(x: int, y: int, H: int, W: int) -> bool:
    """座標がグリッドの範囲内にあるかチェックする関数

    0-indexedが前提
    """
    return 0 <= x < H and 0 <= y < W

def grid_moves(x: int, y: int, H: int, W: int, moves: list[tuple[int]] | None=None, *check_funcs: list[Callable[[int, int], bool]]) -> list[tuple[int]]:
    """現在の座標から、移動可能な座標をmovesをもとに列挙します。

    xとyは現在の座標
    HとWはグリッドのサイズ
    movesは移動する座標がいくつかを保存する
    check_funcsは、その座標の点が#だとかを自前で実装して判定はこちらでするみたいな感じ
    なおcheck_funcsは引数がxとyだけというのが条件
    追加の判定関数は、弾く場合は、False それ以外ならTrueで
    """
    if moves is None:
        moves = ([(0, 1), (0, -1), (1, 0), (-1, 0)],)
    res = []
    for mx, my in moves:
        nx, ny = (x + mx, y + my)
        if not coordinate_check(nx, ny, H, W):
            continue
        for f in check_funcs:
            if not f(nx, ny):
                break
        else:
            res.append((nx, ny))
    return res

def coordinates_to_id(h: int, w: int) -> tuple[list[list[int]], list[tuple[int, int]]]:
    """座標を一次元のindexに変換する関数

    返り値は、
    最初のが、座標からid
    二つめのが、idから座標
    です
    """
    ItC = [[-1] * w for _ in [0] * h]
    CtI = [(-1, -1) for _ in [0] * (h * w)]
    i = 0
    for x in range(h):
        for y in range(w):
            ItC[x][y] = i
            CtI[i] = (x, y)
            i += 1
    return (CtI, ItC)
import heapq

def dijkstra(graph: list[list[tuple[int]]], startpoint: int=0, output_prev: bool=False) -> list[int] | tuple[list[int], list[int]]:
    """ダイクストラ法のライブラリ

    GraphW構造体を使う場合は、allメソッドで、そんまま入れてください
    定数倍速いのかは分かりません(いつも使っているフォーマット)
    経路復元したい場合は、output_prevをTrueにすればprevも返ってくるので、それを使用して復元してください
    0-indexedが前提です
    """
    used = [1 << 63] * len(graph)
    prev = [-1] * len(graph)
    if not 0 <= startpoint < len(graph):
        raise IndexError('あのー0-indexedですか?')
    used[startpoint] = 0
    PQ = [(0, startpoint)]
    while PQ:
        cos, cur = heapq.heappop(PQ)
        if used[cur] < cos:
            continue
        for nxt, w in graph[cur]:
            new_cos = cos + w
            if new_cos >= used[nxt]:
                continue
            used[nxt] = new_cos
            prev[nxt] = cur
            heapq.heappush(PQ, (new_cos, nxt))
    if not output_prev:
        return used
    return (used, prev)

def getpath(prev_lis: list[int], goal_point: int) -> list[int]:
    """経路復元ライブラリ

    dijkstra関数を使う場合、output_prevをTrueにして返ってきた、prevを引数として用います
    他の場合は、移動の時、usedを付けるついでに、prevに現在の頂点を付けてあげるといいです
    """
    res = []
    cur = goal_point
    while cur != -1:
        res.append(cur)
        cur = prev_lis[cur]
    return res[::-1]

def partial_sum_dp(lis: list[int], X: int) -> list[bool]:
    """部分和dpのテンプレート

    lisは品物です
    dp配列の長さは、Xにします
    計算量は、O(X*len(L))みたいな感じ

    返り値は、dp配列で中身は到達できたかを、示すboolです
    """
    dp = [False] * (X + 1)
    dp[0] = True
    for a in lis:
        for k in reversed(range(len(dp))):
            if not dp[k]:
                continue
            if k + a >= len(dp):
                continue
            dp[k + a] = True
    return dp

def knapsack_dp(lis: list[list[int]], W: int) -> int:
    """ナップサックdpのテンプレート

    lis: 品物のリスト [[重さ, 価値], ...]
    W: ナップサックの容量
    戻り値: 最大価値
    """
    if W < 0 or not lis:
        return 0
    dp = [0] * (W + 1)
    for w, v in lis:
        if w < 0 or v < 0:
            msg = 'Weight and value must be non-negative'
            raise ValueError(msg)
        for k in reversed(range(W - w + 1)):
            dp[k + w] = max(dp[k + w], dp[k] + v)
    return dp[W]

def article_breakdown(lis: list[list[int]]) -> list[list[int]]:
    """個数制限付きナップサック問題用の品物を分解する関数

    個数の値が、各品物の一番右にあれば正常に動作します
    """
    res = []
    for w, v, c in lis:
        k = 1
        while c > 0:
            res.append([w * k, v * k])
            c -= k
            k = min(2 * k, c)
    return res

def compress_1d(points: list[int] | tuple[int]) -> list[int]:
    """一次元座標圧縮

    計算量は、O(N log N)です

    lとrは、まとめて入れる事で、座圧できます
    """
    d = {num: ind for ind, num in enumerate(sorted(set(points)))}
    return [d[a] for a in points]

def compress_2d(points) -> list[tuple[int, int]]:
    """二次元座標圧縮

    入力: points - [(x1, y1), (x2, y2), ...] の形式の座標リスト
    出力: 圧縮後の座標リストと、元の座標から圧縮後の座標へのマッピング
    """
    x_coords = sorted({x for x, y in points})
    y_coords = sorted({y for x, y in points})
    x_map = {val: idx for idx, val in enumerate(x_coords)}
    y_map = {val: idx for idx, val in enumerate(y_coords)}
    return [(x_map[x], y_map[y]) for x, y in points]
'\nsegtree\n\n初期化するとき\nSegtree(op,e,v)\n\nopはマージする関数\n例\n\ndef op(a,b):\n    return a+b\n\neは初期化する値\n\nvは配列の長さまたは、初期化する内容\n'
from collections.abc import Callable
from typing import Any

def rerooting(G: list[list[int]], merge: Callable[[Any, Any], Any], add_root: Callable[[int, Any], Any], e) -> list[Any]:
    """全方位木dp"""
    _n = len(G)
    dp: list[list[Any]] = [[]] * _n
    ans: list[Any] = [e] * _n

    def _dfs(u: int, p: int=-1):
        nonlocal dp, merge, add_root, e
        res: Any = e
        dp[u] = [e] * len(G[u])
        for i, v in enumerate(G[u]):
            if v == p:
                continue
            dp[u][i] = _dfs(v, u)
            res = merge(res, dp[u][i])
        return add_root(u, res)

    def _bfs(u: int, cur: Any, p: int=-1):
        nonlocal dp, merge, add_root, e, ans
        deg = len(G[u])
        for i in range(deg):
            if G[u][i] == p:
                dp[u][i] = cur
        dp_l, dp_r = ([e] * (deg + 1), [e] * (deg + 1))
        for i in range(deg):
            dp_l[i + 1] = merge(dp_l[i], dp[u][i])
        for i in reversed(range(deg)):
            dp_r[i] = merge(dp_r[i + 1], dp[u][i])
        ans[u] = add_root(u, dp_l[deg])
        for i in range(deg):
            if G[u][i] != p:
                _bfs(G[u][i], add_root(u, merge(dp_l[i], dp_r[i + 1])), u)
    _dfs(0)
    _bfs(0, e)
    return ans

def manacher_algorithm(S: str) -> list[int]:
    """Manacher algorithm

    res_i = S_iを中心とした最長の回文の半径
    """
    _n = len(S)
    res = [0] * _n
    i = k = 0
    while i < _n:
        while i - k >= 0 and i + k < _n and (S[i - k] == S[i + k]):
            k += 1
        res[i] = k
        a = 1
        while i - a >= 0 and a + res[i - a] < k:
            res[i + a] = res[i - a]
            a += 1
        i += a
        k -= a
    return res

class RollingHash:
    string: str
    mod: int
    base: int
    n: int

    def __init__(self, string: str, mod: int=(1 << 61) - 1) -> None:
        """RollingHash構造体

        衝突する可能性があるのでmodが違う二つで比較するのが有効

        string: 文字列
        mod: mod デフォルト値は2^61 - 1
        """
        self.string = string
        self.mod = mod
        self.base = len(set(string))
        self.n = n = len(string)
        self.pow = [1] * (n + 1)
        self.hash = [0] * (n + 1)
        for i in range(n):
            self.hash[i + 1] = (self.hash[i] * self.base + ord(string[i])) % mod
        for i in range(n):
            self.pow[i + 1] = self.pow[i] * self.base % mod

    def get(self, l: int, r: int) -> int:
        """区間[l,r)のハッシュ値を取得する"""
        return (self.hash[r] - self.hash[l] * self.pow[r - l]) % self.mod

    def lcp(self, b: int, bn: int) -> int:
        """2つのRollingHashの最長共通接頭辞を返す

        bがhashでbnがそのhashの長さです
        """
        left, right = (0, min(self.n, bn))
        while right - left > 1:
            mid = (left + right) // 2
            if self.get(0, mid) == b:
                left = mid
            else:
                right = mid
        return left
from collections import deque

class Graph:

    def __init__(self, N: int, dire: bool=False) -> None:
        """グラフ構造体

        Nは頂点数、direは有向グラフかです
        """
        self.N = N
        self.dire = dire
        self.grath = [[] for _ in [0] * self.N]
        self.in_deg = [0] * N

    def new_side(self, a: int, b: int) -> None:
        """aとbを辺で繋ぎます

        有向グラフなら、aからbだけ、無向グラフなら、aからbと、bからaを繋ぎます
        注意\u30000-indexedが前提
        """
        self.grath[a].append(b)
        if self.dire:
            self.in_deg[b] += 1
        if not self.dire:
            self.grath[b].append(a)

    def side_input(self) -> None:
        """標準入力で、新しい辺を追加します"""
        a, b = map(lambda x: int(x) - 1, input().split())
        self.new_side(a, b)

    def input(self, M: int) -> None:
        """標準入力で複数行受け取り、各行の内容で辺を繋ぎます"""
        for _ in [0] * M:
            self.side_input()

    def get(self, a: int) -> list[int]:
        """頂点aの隣接頂点を出力します"""
        return self.grath[a]

    def all(self) -> list[list[int]]:
        """グラフの隣接リストをすべて出力します"""
        return self.grath

    def topological(self, unique: bool=False) -> list[int]:
        """トポロジカルソートします

        有向グラフ限定です

        引数のuniqueは、トポロジカルソート結果が、一意に定まらないとエラーを吐きます
        閉路がある、または、uniqueがTrueで一意に定まらなかった時は、[-1]を返します
        """
        if not self.dire:
            msg = 'グラフが有向グラフでは有りません (╥﹏╥)'
            raise ValueError(msg)
        in_deg = self.in_deg[:]
        S: deque[int] = deque([])
        order: list[int] = []
        for i in range(self.N):
            if in_deg[i] == 0:
                S.append(i)
        while S:
            if unique and len(S) != 1:
                return [-1]
            cur = S.pop()
            order.append(cur)
            for nxt in self.get(cur):
                in_deg[nxt] -= 1
                if in_deg[nxt] == 0:
                    S.append(nxt)
        if sum(in_deg) > 0:
            return [-1]
        return [x for x in order]

class GraphW:

    def __init__(self, N: int, dire: bool=False) -> None:
        """重み付きグラフ"""
        self.N = N
        self.dire = dire
        self.grath = [[] for _ in [0] * self.N]

    def new_side(self, a: int, b: int, w: int) -> None:
        """aとbを辺で繋ぎます

        有向グラフなら、aからbだけ、無向グラフなら、aからbと、bからaを繋ぎます
        注意\u30000-indexedが前提
        """
        self.grath[a].append((b, w))
        if not self.dire:
            self.grath[b].append((a, w))

    def side_input(self) -> None:
        """標準入力で、新しい辺を追加します"""
        a, b, w = map(lambda x: int(x) - 1, input().split())
        self.new_side(a, b, w + 1)

    def input(self, M: int) -> None:
        """標準入力で複数行受け取り、各行の内容で辺を繋ぎます"""
        for _ in [0] * M:
            self.side_input()

    def get(self, a: int) -> list[tuple[int]]:
        """頂点aの隣接頂点を出力します"""
        return self.grath[a]

    def all(self) -> list[list[tuple[int]]]:
        """グラフの隣接リストをすべて出力します"""
        return self.grath
from collections import defaultdict

class UnionFind:

    def __init__(self, n: int) -> None:
        """UnionFind

        rollbackをデフォルトで装備済み
        計算量は経路圧縮を行わないため、基本的なUnionFindの動作は、一回あたり、O(log N)
        rollbackは、一回あたり、O(1)で行える。
        """
        self.size = n
        self.data = [-1] * n
        self.hist = []

    def leader(self, vtx: int) -> int:
        """頂点vtxの親を出力します"""
        if self.data[vtx] < 0:
            return vtx
        return self.leader(self.data[vtx])

    def same(self, a: int, b: int) -> bool:
        """aとbが連結しているかどうか判定します"""
        return self.leader(a) == self.leader(b)

    def merge(self, a: int, b: int) -> bool:
        """aとbを結合します

        leaderが同じでも、履歴には追加します
        """
        ra, rb = (self.leader(a), self.leader(b))
        new_hist = [ra, rb, self.data[ra], self.data[rb]]
        self.hist.append(new_hist)
        if ra == rb:
            return False
        if self.data[ra] > self.data[rb]:
            ra, rb = (rb, ra)
        self.data[ra] += self.data[rb]
        self.data[rb] = ra
        return True

    def rollback(self) -> bool:
        """Undo

        redoはありません
        """
        if not self.hist:
            return False
        ra, rb, da, db = self.hist.pop()
        self.data[ra] = da
        self.data[rb] = db
        return True

    def all(self) -> list[list[int]]:
        D = defaultdict(list)
        for i in range(self.size):
            D[self.leader(i)].append(i)
        return [l for l in D.values()]

class EulerTour:

    def __init__(self, edges: list[tuple[int, int, int]], root: int=0) -> None:
        """オイラーツアーのライブラリ

        edges[i] = (u, v, w)
        なお閉路がない、連結という前提 エラー処理をしていない

        木上の最短経路は、path_query関数を使うこと

        初期化にO(N + M) それ以外は、$O(log n)$

        Warning:
        ac-library-pythonを__init__内で使用しているので注意
        定数倍が遅い事に注意 あとメモリも注意 結構リストを使用している

        """
        from atcoder.segtree import SegTree
        self.edges = edges
        self._n = max([max(u, v) for u, v, w in edges]) + 1
        self.root = root
        self.graph: list[list[tuple[int, int, int]]] = [[] for _ in [0] * self._n]
        for i, (u, v, w) in enumerate(edges):
            self.graph[u].append((v, w, i))
            self.graph[v].append((u, w, i))
        self._build()
        self.segtree_edgecost = SegTree(lambda a, b: a + b, 0, self.edge_cost)
        self.segtree_depth = SegTree(min, (1 << 63, 1 << 63), [(d, i) for i, d in enumerate(self.depth)])

    def _build(self) -> None:
        self.euler_tour: list[tuple[int, int]] = [(0, -1)]
        self.edge_cost: list[int] = [0]
        self.depth: list[int] = [0]

        def dfs(cur: int, p: int=-1, d: int=0) -> None:
            for nxt, w, i in self.graph[cur]:
                if nxt == p:
                    continue
                self.euler_tour.append((nxt, i))
                self.edge_cost.append(w)
                self.depth.append(d + 1)
                dfs(nxt, cur, d + 1)
                self.euler_tour.append((cur, i))
                self.edge_cost.append(-w)
                self.depth.append(d)
        dfs(self.root)
        self.first_arrival = [-1] * self._n
        self.last_arrival = [-1] * self._n
        self.first_arrival[self.root] = 0
        self.last_arrival[self.root] = len(self.euler_tour) - 1
        self.edge_plus = [-1] * (self._n - 1)
        self.edge_minus = [-1] * (self._n - 1)
        for i, (u, edge_ind) in enumerate(self.euler_tour):
            if self.edge_cost[i] >= 0:
                self.edge_plus[edge_ind] = i
            else:
                self.edge_minus[edge_ind] = i
            if self.first_arrival[u] == -1:
                self.first_arrival[u] = i
            self.last_arrival[u] = i

    def lca(self, a: int, b: int) -> int:
        l, r = (min(self.first_arrival[a], self.first_arrival[b]), max(self.last_arrival[a], self.last_arrival[b]))
        return self.euler_tour[self.segtree_depth.prod(l, r)[1]][0]

    def path_query_from_root(self, u: int) -> int:
        assert 0 <= u < self._n
        return self.segtree_edgecost.prod(0, self.first_arrival[u] + 1)

    def path_query(self, a: int, b: int) -> int:
        """aからbへの最短経路"""
        try:
            l = self.lca(a, b)
        except IndexError:
            return 0
        return self.path_query_from_root(a) + self.path_query_from_root(b) - 2 * self.path_query_from_root(l)

    def change_edge_cost(self, i: int, w: int) -> None:
        self.segtree_edgecost.set(self.edge_plus[i], w)
        self.segtree_edgecost.set(self.edge_minus[i], -w)

class PotentialUnionFind:

    def __init__(self, n: int) -> None:
        """重み付きunionfind

        俗に言う、牛ゲー

        uniteは、差を指定して、uniteします
        """
        self.data: list[int] = [-1] * n
        self.pot: list[int] = [0] * n

    def root(self, vtx: int) -> int:
        """頂点vtxの親を出力します

        ポテンシャルは出力しません
        """
        if self.data[vtx] < 0:
            return vtx
        rt = self.root(self.data[vtx])
        self.pot[vtx] += self.pot[self.data[vtx]]
        self.data[vtx] = rt
        return rt

    def potential(self, vtx: int) -> int:
        """頂点vtxのポテンシャルを出力します"""
        self.root(vtx)
        return self.pot[vtx]

    def same(self, a: int, b: int) -> bool:
        """頂点aと頂点bが同じ連結成分かを判定します"""
        return self.root(a) == self.root(b)

    def unite(self, a: int, b: int, p: int) -> bool:
        """頂点aから頂点bを、pの距離でmergeします

        計算量はlog nです
        """
        p += self.potential(b) - self.potential(a)
        a, b = (self.root(a), self.root(b))
        if a == b:
            return False
        if self.data[a] < self.data[b]:
            a, b = (b, a)
            p *= -1
        self.data[b] += self.data[a]
        self.data[a] = b
        self.pot[a] = p
        return True

    def diff(self, a: int, b: int) -> int:
        """頂点aから頂点bの距離を、出力します"""
        return self.potential(a) - self.potential(b)
from collections.abc import Callable
from typing import Any

def _keys_for_heapq(x: Any):
    """先頭の値を取得する"""
    cur = x
    while True:
        try:
            cur = cur[0]
        except TypeError:
            break
    return cur

class HeapBase:

    def __init__(self, arr: list[Any]=[], key: Callable[[Any], Any]=_keys_for_heapq) -> None:
        """arrはソート済みが前提です"""
        self.key: Callable[Any, Any] = key
        self.lis: list[tuple[Any, Any]] = [(self.key(x), x) for x in arr]

    def _op(self, a: int, b: int) -> bool:
        assert 0 <= a < b < len(self.lis)
        return True

    def push(self, x: Any) -> None:
        self.lis.append((self.key(x), x))
        i = len(self.lis) - 1
        while i != 0:
            p = (i - 1) // 2
            if self._op(p, i):
                self.lis[i], self.lis[p] = (self.lis[p], self.lis[i])
                i = p
            else:
                break

    def pop(self) -> Any:
        assert len(self.lis) > 0
        res = self.lis[0][1]
        self.lis[0] = self.lis[-1]
        self.lis.pop()
        if not self.lis:
            return res
        i = 0
        while i * 2 + 1 < len(self.lis):
            c1 = i * 2 + 1
            c2 = i * 2 + 2
            smallest = c1
            if c2 < len(self.lis) and self._op(c1, c2):
                smallest = c2
            if self._op(i, smallest):
                self.lis[i], self.lis[smallest] = (self.lis[smallest], self.lis[i])
                i = smallest
            else:
                break
        return res

    def __len__(self) -> int:
        return len(self.lis)

    def __getitem__(self, i: int):
        return self.lis[i][1]

class HeapMin(HeapBase):

    def _op(self, a: int, b: int) -> bool:
        return self.lis[a][0] > self.lis[b][0]

class HeapMax(HeapBase):

    def _op(self, a: int, b: int) -> bool:
        return self.lis[a][0] < self.lis[b][0]

class Trie:

    class Data:
        """trie木のノード"""

        def __init__(self, value, ind):
            """trie木のノード"""
            self.count = 1
            self.value = value
            self.childs = {}
            self.ind = ind

    def __init__(self):
        """Trie木"""
        self.data = [self.Data('ab', 0)]

    def add(self, value: str) -> int:
        cur = 0
        result = 0
        for t in value:
            childs = self.data[cur].childs
            if t in childs:
                self.data[childs[t]].count += 1
            else:
                nd = self.Data(t, len(self.data))
                childs[t] = len(self.data)
                self.data.append(nd)
            result += self.data[childs[t]].count - 1
            cur = childs[t]
        return result

    def lcp_max(self, value: str) -> int:
        cur = 0
        result = 0
        for t in value:
            childs = self.data[cur].childs
            if t not in childs:
                break
            if self.data[childs[t]].count == 1:
                break
            cur = childs[t]
            result += 1
        return result

    def lcp_sum(self, value: str) -> int:
        cur = 0
        result = 0
        for t in value:
            childs = self.data[cur].childs
            if t not in childs:
                break
            if self.data[childs[t]].count == 1:
                break
            cur = childs[t]
            result += self.data[childs[t]].count - 1
        return result
import math
from collections.abc import Callable
from typing import Any

def mo_algorithm(N: int, queries: list[Any], add: Callable[[int], Any], delete: Callable[[int], Any], getvalue: Callable[[], Any]) -> list[Any]:
    """Mo's algorithm

    queriesは、(左端, 右端)で1-indexed
    addはあるindexが追加される時の値を現在の値にする
    deleteはあるindexが削除される時の値を現在の値にする
    getvalueは現在の値を返す
    """
    Q = len(queries)
    res = [None] * Q
    M = int(max(1, 1.0 * N / max(1, math.sqrt(Q * 2.0 / 3.0))))
    queries = [(l, r, i) for i, (l, r) in enumerate(queries)]
    queries.sort(key=lambda x: (x[0] // M, x[1] if x[0] // M % 2 == 0 else -x[1]))
    cl, cr = (0, -1)
    for l, r, ind in queries:
        l -= 1
        r -= 1
        while cl > l:
            cl -= 1
            add(cl)
        while cr < r:
            cr += 1
            add(cr)
        while cl < l:
            delete(cl)
            cl += 1
        while cr > r:
            delete(cr)
            cr -= 1
        res[ind] = getvalue()
    return res
import math
from collections.abc import Callable
from typing import Any

class SquareDivision:

    def __init__(self, lis: list[Any], op: Callable[[Any, Any], Any]) -> None:
        """平方分割ライブラリ

        ほぼACLのセグ木と同じ
        """
        self.n = len(lis)
        self.op = op
        self.block_size = math.isqrt(self.n)
        self.blocks = []
        self.lis = lis[:]
        for i in range(0, self.n, self.block_size):
            block_val = lis[i]
            for k in range(i + 1, min(i + self.block_size, self.n)):
                block_val = self.op(block_val, lis[k])
            self.blocks.append(block_val)
        self.m = len(self.blocks)

    def get_block_index_left(self, i: int) -> int:
        return i // self.block_size

    def get_block_index_right(self, i: int) -> int:
        return (i + self.block_size - 1) // self.block_size

    def prod(self, l: int, r: int) -> Any:
        """rは0-indexedなのに注意してください"""
        assert 0 <= l <= r < self.n
        l_block_left = self.get_block_index_left(l)
        r_block_left = self.get_block_index_left(r)
        if l_block_left == r_block_left:
            res = self.lis[l]
            for k in range(l + 1, r + 1):
                res = self.op(res, self.lis[k])
            return res
        res = self.lis[l]
        for i in range(l + 1, min((l_block_left + 1) * self.block_size, self.n)):
            res = self.op(res, self.lis[i])
        for block_ind in range(l_block_left + 1, r_block_left):
            res = self.op(res, self.blocks[block_ind])
        for i in range(r_block_left * self.block_size, r + 1):
            res = self.op(res, self.lis[i])
        return res

    def update(self, i: int, x: Any) -> None:
        assert 0 <= i < self.n
        self.lis[i] = x
        block_ind = self.get_block_index_left(i)
        start = block_ind * self.block_size
        end = min(start + self.block_size, self.n)
        if start < self.n:
            self.blocks[block_ind] = self.lis[start]
            for j in range(start + 1, end):
                self.blocks[block_ind] = self.op(self.blocks[block_ind], self.lis[j])

    def get(self, i: int) -> Any:
        assert 0 <= i < self.n
        return self.lis[i]

class SquareDivisionSpeedy(SquareDivision):

    def __init__(self, lis: list[Any], op: Callable[[Any, Any], Any], delete: Callable[[Any, Any], Any]) -> None:
        """その値を削除する関数がある場合の平方分割ライブラリ

        更新は高速だがクエリがボトルネックなのであまり変わらない
        """
        self.delete = delete
        super().__init__(lis, op)

    def update(self, i: int, x: Any) -> None:
        assert 0 <= i < self.n
        block_ind = self.get_block_index_left(i)
        self.blocks[block_ind] = self.delete(self.blocks[block_ind], self.lis[i])
        self.lis[i] = x
        self.blocks[block_ind] = self.op(self.blocks[block_ind], self.lis[i])

class PrefixSum2D:

    def __init__(self, h: int, w: int) -> None:
        """二次元累積和のライブラリ"""
        self.data = [[0] * (w + 1) for _ in [0] * (h + 1)]
        self.builded = False
        self.h = h
        self.w = w

    def add(self, x: int, y: int, a: int) -> None:
        assert 0 <= x < self.h and 0 <= y < self.w
        self.data[x + 1][y + 1] += a

    def build(self) -> None:
        assert not self.builded
        for i in range(self.h + 1):
            for k in range(self.w):
                self.data[i][k + 1] += self.data[i][k]
        for k in range(self.w + 1):
            for i in range(self.h):
                self.data[i + 1][k] += self.data[i][k]
        self.builded = True

    def prod(self, ax: int, ay: int, bx: int, by: int) -> int:
        assert 0 <= ax <= bx < self.h and 0 <= ay <= by < self.w
        assert self.builded
        return self.data[bx + 1][by + 1] + self.data[ax][ay] - self.data[ax][by + 1] - self.data[bx + 1][ay]
from collections.abc import Callable
from typing import Any

class DualSegmentTree:

    def __init__(self, op: Callable[[Any, Any], Any], e, n: int) -> None:
        """区間作用/一点取得のセグメント木

        opは区間作用用の関数
        eは初期値
        vは長さ
        """
        self._op: Callable[[Any, Any], Any] = op
        self._e: Any = e
        self._n: int = n
        self.n: int = 1 << (n - 1).bit_length()
        self.data = [e] * (self.n * 2)

    def apply(self, l, r, x) -> None:
        """区間[l,r)にxを適用"""
        assert 0 <= l <= r <= self.n
        l += self.n
        r += self.n
        while l < r:
            if l & 1:
                self.data[l] = self._op(self.data[l], x)
                l += 1
            if r & 1:
                self.data[r - 1] = self._op(self.data[r - 1], x)
            l >>= 1
            r >>= 1

    def get(self, p: int) -> Any:
        """pの値を取得する"""
        assert 0 <= p < self.n
        res = self._e
        p += self.n
        while p:
            res = self._op(res, self.data[p])
            p >>= 1
        return res

def euclid_dis(x1: int, y1: int, x2: int, y2: int) -> int:
    """ユークリッド距離を計算する関数

    注意:
    この関数はsqrtを取りません(主に少数誤差用)
    sqrtを取りたい場合は、自分で計算してください
    """
    return (x1 - x2) ** 2 + (y1 - y2) ** 2

def manhattan_dis(x1: int, y1: int, x2: int, y2: int) -> int:
    """マンハッタン距離を計算する関数"""
    return abs(x1 - x2) + abs(y1 - y2)

def manhattan_45turn(x: int, y: int) -> tuple[int]:
    """マンハッタン距離用の座標を45度回転する関数

    回転すると、マンハッタン距離が、チェビシェフ距離になるので、距離の最大値などが簡単に求められます
    """
    res_x = x - y
    res_y = x + y
    return (res_x, res_y)

def chebyshev_dis(x1: int, y1: int, x2: int, y2: int) -> int:
    """チェビシェフ距離を計算する関数"""
    return max(abs(x1 - x2), abs(y1 - y2))
INF = 1 << 63
lowerlist = list('abcdefghijklmnopqrstuvwxyz')
upperlist = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
MOVES1 = [(0, 1), (0, -1), (1, 0), (-1, 0)]
MOVES2 = MOVES1 + [(1, 1), (1, -1), (-1, 1), (-1, -1)]
N, M = il()
A = il(-1)
MOD = 998244353
RG = [[] for _ in [0] * N]
deg = [0] * N
UF = UnionFind(N)
for i in range(N):
    UF.merge(i, A[i])
    RG[A[i]].append(i)
    deg[A[i]] += 1
D = defaultdict(list)
for i in range(N):
    D[UF.leader(i)].append(i)
ans = ModInt(1)
for l in D.values():
    if len([i for i in l if deg[i] == 0]) == 0:
        ans *= M
        continue
    for i in l:
        if deg[i] == 0:
            break
    used = set([i])
    while A[i] not in used:
        used.add(A[i])
        i = A[i]
    used = set()
    while A[i] not in used:
        used.add(A[i])
        i = A[i]

    def f(cur):
        dp = [1] * M
        for nxt in RG[cur]:
            if nxt in used:
                continue
            ndp = f(nxt)
            su = 0
            for k in range(M):
                su += ndp[k]
                dp[k] *= su
                dp[k] %= MOD
        return dp
    dp = [1] * M
    for t in used:
        ndp = f(t)
        for k in range(M):
            dp[k] *= ndp[k]
            dp[k] %= MOD
    ans *= sum(dp) % MOD
print(ans.val())
