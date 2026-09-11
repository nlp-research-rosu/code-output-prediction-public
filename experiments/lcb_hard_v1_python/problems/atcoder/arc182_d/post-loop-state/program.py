import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def space(x, y):
    if x < y:
        return -1
    if x == y:
        return 0
    if x > y:
        return 1
N, M = map(int, input().split())
A = list(map(int, input().split()))
B = list(map(int, input().split()))
if M == 2:
    if A == B:
        print(0)
    else:
        print(-1)
    exit()
C = [B[0]]
for i in range(1, N):
    for j in range(C[-1] // M - 3, C[-1] // M + 3):
        if space(A[i - 1], A[i]) == space(C[-1], j * M + B[i]) and abs(C[-1] - (j * M + B[i])) < M:
            C.append(j * M + B[i])
            break
add = []
for i in range(N):
    add.append(C[i] - A[i])
add.sort()
mid = add[N // 2]
ans = 1 << 60
for i in range(mid // M - 3, mid // M + 3):
    now = 0
    for j in range(N):
        _lcb_count[0] += 1
        now += abs(A[j] + i * M - C[j])
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'C': C, 'ans': ans, 'i': i, 'j': j, 'mid': mid, 'now': now}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    ans = min(ans, now)
print(ans)
