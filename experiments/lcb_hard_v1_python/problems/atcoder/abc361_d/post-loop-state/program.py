import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from collections import deque
from itertools import product

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    S = data[1]
    T = data[2]
    initial_state = list(S + '..')
    target_state = list(T + '..')
    if sorted(S) != sorted(T):
        print(-1)
        return
    visited = set()
    initial_tuple = tuple(initial_state)
    target_tuple = tuple(target_state)
    queue = deque()
    queue.append((initial_tuple, 0))
    visited.add(initial_tuple)
    while queue:
        state, steps = queue.popleft()
        if state == target_tuple:
            print(steps)
            return
        empty_pos = [i for i in range(N + 2) if state[i] == '.']
        e1, e2 = empty_pos
        for x in range(N + 1):
            _lcb_count[0] += 1
            if state[x] != '.' and state[x + 1] != '.':
                new_state = list(state)
                new_state[e1], new_state[e2] = (new_state[x], new_state[x + 1])
                new_state[x], new_state[x + 1] = ('.', '.')
                new_tuple = tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    queue.append((new_tuple, steps + 1))
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'e1': e1, 'e2': e2, 'empty_pos': empty_pos, 'state': state, 'steps': steps, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    print(-1)
if __name__ == '__main__':
    main()
