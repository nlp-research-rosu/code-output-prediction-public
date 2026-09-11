from itertools import accumulate
import sys
sys.setrecursionlimit(int(1000000.0))
input = lambda: sys.stdin.readline().rstrip('\r\n')
from functools import lru_cache
INF = int(4e+18)

def min2(a: int, b: int) -> int:
    return a if a < b else b
if __name__ == '__main__':
    N, K, X = map(int, input().split())
    T = list(map(int, input().split()))
    T.sort()
    preSum = [0] + list(accumulate(T))

    @lru_cache(None)
    def dfs(index: int, time: int) -> int:
        if index == N:
            return 0
        res = INF
        for j in range(K):
            if index + j >= N:
                break
            if time >= T[index + j]:
                curCost = time * (j + 1) - (preSum[index + j + 1] - preSum[index])
                res = min2(res, dfs(index + j + 1, time + X) + curCost)
            else:
                res = min2(res, dfs(index, T[index + j]))
        return res
    res = dfs(0, 0)
    dfs.cache_clear()
    print(res)
