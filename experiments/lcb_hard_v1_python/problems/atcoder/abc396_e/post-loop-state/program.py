import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
from collections import deque
import sys

def main():
    input = sys.stdin.read().split()
    ptr = 0
    N = int(input[ptr])
    ptr += 1
    M = int(input[ptr])
    ptr += 1
    adj = [[] for _ in range(N + 1)]
    for _ in range(M):
        X = int(input[ptr])
        Y = int(input[ptr + 1])
        Z = int(input[ptr + 2])
        ptr += 3
        adj[X].append((Y, Z))
        adj[Y].append((X, Z))
    d = [-1] * (N + 1)
    A = [0] * (N + 1)
    possible = True
    for u in range(1, N + 1):
        if d[u] == -1:
            q = deque()
            q.append(u)
            d[u] = 0
            component = [u]
            while q:
                current = q.popleft()
                for v, z in adj[current]:
                    if d[v] == -1:
                        d[v] = d[current] ^ z
                        component.append(v)
                        q.append(v)
                    elif d[v] != d[current] ^ z:
                        possible = False
                        break
                if not possible:
                    break
            if not possible:
                break
            r = 0
            for k in range(31):
                count_1 = 0
                for v in component:
                    if d[v] >> k & 1:
                        count_1 += 1
                count_0 = len(component) - count_1
                if count_1 < count_0:
                    pass
                else:
                    r |= 1 << k
            for v in component:
                _lcb_count[0] += 1
                A[v] = r ^ d[v]
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'component': component, 'd': d, 'k': k, 'r': r, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
    if not possible:
        print(-1)
    else:
        print(' '.join(map(str, A[1:N + 1])))
if __name__ == '__main__':
    main()
