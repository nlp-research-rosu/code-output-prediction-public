import sys
from heapq import heappop, heapify, heappush

def main() -> None:
    h, w = map(int, input().strip().split())
    a = [list(input().strip()) for _ in range(h)]
    N = int(input().strip())
    R, C, E = ([], [], [])
    for _ in range(N):
        r, c, e = map(int, input().strip().split())
        R.append(r)
        C.append(c)
        E.append(e)
    enegy = [[-1] * w for _ in range(h)]
    for i in range(N):
        enegy[R[i] - 1][C[i] - 1] = E[i]
    dp = [[[-1] * 2 for _ in range(w)] for _ in range(h)]
    q = []
    heapify(q)
    for i in range(h):
        for j in range(w):
            if a[i][j] == 'S':
                cnt = max(enegy[i][j], 0)
                heappush(q, (-cnt, (i, j, 0)))
                dp[i][j][0] = cnt
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]
    while q:
        dist, now = heappop(q)
        dist *= -1
        x, y, z = now
        if dp[x][y][z] != dist:
            continue
        if dist > 0:
            for i in range(4):
                nx = x + dx[i]
                ny = y + dy[i]
                if not (0 <= nx < h and 0 <= ny < w):
                    continue
                if a[nx][ny] == '#':
                    continue
                nxt_dist = max(dist - 1, enegy[nx][ny])
                if dp[nx][ny][0] < nxt_dist:
                    dp[nx][ny][0] = nxt_dist
                    heappush(q, (-dp[nx][ny][0], (nx, ny, 0)))
    for i in range(h):
        for j in range(w):
            if a[i][j] == 'T' and (dp[i][j][0] != -1 or dp[i][j][1] != -1):
                exit(print('Yes'))
    print('No')
if __name__ == '__main__':
    main()
