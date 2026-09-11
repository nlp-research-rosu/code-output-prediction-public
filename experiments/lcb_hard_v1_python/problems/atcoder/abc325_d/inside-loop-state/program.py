import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import heapq
N = int(input())
TD = []
for i in range(N):
    t, d = map(int, input().split())
    TD.append((t, t + d))
TD.sort()
ans = 0
it = 0
now = 0
hq = []
while True:
    if len(hq) == 0:
        if it == N:
            break
        now = TD[it][0]
    while it < N and TD[it][0] == now:
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'hq': hq, 'it': it, 'now': now}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        heapq.heappush(hq, TD[it][1])
        it += 1
    while len(hq) > 0 and hq[0] < now:
        heapq.heappop(hq)
    if len(hq) > 0:
        heapq.heappop(hq)
        ans += 1
    now += 1
print(ans)
