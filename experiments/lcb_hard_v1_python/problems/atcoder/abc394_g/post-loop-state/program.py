import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import heapq

def main():
    input = sys.stdin.read().split()
    idx = 0
    H = int(input[idx])
    idx += 1
    W = int(input[idx])
    idx += 1
    F = []
    for _ in range(H):
        row = list(map(int, input[idx:idx + W]))
        F.append(row)
        idx += W
    Q = int(input[idx])
    idx += 1
    queries = []
    for _ in range(Q):
        A = int(input[idx]) - 1
        B = int(input[idx + 1]) - 1
        Y = int(input[idx + 2])
        C = int(input[idx + 3]) - 1
        D = int(input[idx + 4]) - 1
        Z = int(input[idx + 5])
        queries.append((A, B, Y, C, D, Z))
        idx += 6
    for A, B, Y, C, D, Z in queries:
        dist = [[-1 for _ in range(W)] for _ in range(H)]
        heap = []
        initial_x = F[A][B]
        dist[A][B] = initial_x
        heapq.heappush(heap, (-initial_x, A, B))
        found = False
        while heap:
            current_neg_x, i, j = heapq.heappop(heap)
            current_x = -current_neg_x
            if i == C and j == D:
                x_max = current_x
                found = True
                break
            if current_x < dist[i][j]:
                continue
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                _lcb_count[0] += 1
                ni = i + di
                nj = j + dj
                if 0 <= ni < H and 0 <= nj < W:
                    new_x = min(current_x, F[ni][nj])
                    if dist[ni][nj] < new_x:
                        dist[ni][nj] = new_x
                        heapq.heappush(heap, (-new_x, ni, nj))
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'current_x': current_x, 'di': di, 'dist': dist, 'dj': dj, 'heap': heap, 'i': i, 'j': j, 'ni': ni, 'nj': nj}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
        if not found:
            x_max = 1
        min_yz = min(Y, Z)
        if x_max >= min_yz:
            ans = abs(Y - Z)
        else:
            ans = Y - x_max + (Z - x_max)
        print(ans)
if __name__ == '__main__':
    main()
