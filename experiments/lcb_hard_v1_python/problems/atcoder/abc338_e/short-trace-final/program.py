import sys
import math
N = int(input())
AB = [list(map(int, input().split())) for _ in range(N)]
events = []
for i, (a, b) in enumerate(AB):
    s, l = (min(a, b), max(a, b))
    events.append(((s, -l), 1, i))
    events.append(((l, s), -1, i))
stamp = [0] * N
cur = 0
for (x, _), t, i in sorted(events):
    if t == 1:
        stamp[i] = cur
        cur += 1
    else:
        cur -= 1
        if stamp[i] != cur:
            print('Yes')
            sys.exit()
print('No')
