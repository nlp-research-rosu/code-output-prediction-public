import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n = data[0]
events = [(data[index], data[index + 1]) for index in range(1, 2 * n + 1, 2)]
needed = [0] * (n + 1)
chosen = [0] * n
for index in range(n - 1, -1, -1):
    event_type, potion_type = events[index]
    if event_type == 2:
        needed[potion_type] += 1
    elif needed[potion_type]:
        chosen[index] = 1
        needed[potion_type] -= 1
if any(needed):
    print(-1)
    raise SystemExit
inventory = [0] * (n + 1)
held = 0
peak = 0
actions = []
for index, (event_type, potion_type) in enumerate(events):
    _lcb_count[0] += 1
    if event_type == 1:
        action = chosen[index]
        actions.append(action)
        if action:
            inventory[potion_type] += 1
            held += 1
            peak = max(peak, held)
    else:
        inventory[potion_type] -= 1
        held -= 1
if _lcb_count[0] > 1000:
    _lcb_sys.stdout.write(_lcb_json.dumps({'actions': actions, 'held': held, 'index': index, 'inventory': inventory, 'peak': peak, 'potion_type': potion_type}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
    raise SystemExit
print(peak)
print(*actions)
