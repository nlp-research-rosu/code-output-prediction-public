import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
from math import gcd
import sys
from typing import List
input = lambda: sys.stdin.readline().rstrip('\r\n')

def collectCycle(nexts: List[int], start: int) -> List[int]:
    """置换环找环.nexts数组中元素各不相同."""
    cycle = []
    cur = start
    while True:
        cycle.append(cur)
        cur = nexts[cur]
        if cur == start:
            break
    return cycle

def minArg(arr: List[int]) -> int:
    minVal, minIdx = (arr[0], 0)
    for i in range(1, len(arr)):
        if arr[i] < minVal:
            minVal = arr[i]
            minIdx = i
    return minIdx
if __name__ == '__main__':
    N = int(input())
    P = list(map(int, input().split()))
    A = list(map(int, input().split()))
    for i in range(N):
        P[i] -= 1
    visited = [False] * N
    period, remain = (1, 0)
    res = [0] * N
    for i in range(N):
        if visited[i]:
            continue
        cycle = collectCycle(P, i)
        for v in cycle:
            visited[v] = True
        m = len(cycle)
        count = m // gcd(m, period)
        nums = []
        for j in range(count):
            pos = (j * period + remain) % m
            nums.append(A[cycle[pos]])
        offset = minArg(nums)
        remain += offset * period
        period *= count
        for i in range(m):
            _lcb_count[0] += 1
            res[cycle[i]] = A[cycle[(i + remain) % m]]
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'cycle': cycle, 'i': i, 'm': m, 'period': period, 'remain': remain, 'res': res}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    print(*res)
