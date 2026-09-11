import json, sys

class Solution(object):

    def maxMoves(self, kx, ky, positions):
        N = 50
        DIRECTIONS = ((1, 2), (-1, 2), (1, -2), (-1, -2), (2, 1), (-2, 1), (2, -1), (-2, -1))
        POS_INF = float('inf')
        NEG_INF = float('-inf')

        def popcount(r):
            return bin(r)[2:].count('1')

        def bfs(r, c):
            dist = [[POS_INF] * N for _ in list(range(N))]
            dist[r][c] = 0
            q = [(r, c)]
            while q:
                new_q = []
                for r, c in q:
                    for dr, dc in DIRECTIONS:
                        nr, nc = (r + dr, c + dc)
                        if not (0 <= nr < N and 0 <= nc < N and (dist[nr][nc] == POS_INF)):
                            continue
                        dist[nr][nc] = dist[r][c] + 1
                        new_q.append((nr, nc))
                q = new_q
            return dist
        p = len(positions)
        positions.append([kx, ky])
        dist = [[0] * (p + 1) for _ in list(range(p + 1))]
        for i, (r, c) in enumerate(positions):
            d = bfs(r, c)
            for j in list(range(i + 1, p + 1)):
                dist[j][i] = dist[i][j] = d[positions[j][0]][positions[j][1]]
        dp = [[POS_INF if popcount(mask) & 1 else NEG_INF] * p for mask in list(range(1 << p))]
        dp[-1] = [0] * p
        for mask in reversed(list(range(1, 1 << p))):
            fn = (max, min)[popcount(mask) & 1 ^ 1]
            for i in list(range(p)):
                if mask & 1 << i == 0:
                    continue
                for j in list(range(p)):
                    if j == i or mask & 1 << j == 0:
                        continue
                    dp[mask ^ 1 << i][j] = fn(dp[mask ^ 1 << i][j], dp[mask][i] + dist[i][j])
        return max((dp[1 << i][i] + dist[i][p] for i in list(range(p))))

def function(kx, ky, positions):
    return Solution().maxMoves(kx=kx, ky=ky, positions=positions)

def _read_lcb_input(names):
    text = sys.stdin.read()
    decoder = json.JSONDecoder()
    values = []
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset == len(text):
            break
        value, offset = decoder.raw_decode(text, offset)
        values.append(value)
    if len(values) == 1:
        value = values[0]
        if isinstance(value, dict) and all(name in value for name in names):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError("input argument count does not match the solution signature")
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('kx', 'ky', 'positions'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
