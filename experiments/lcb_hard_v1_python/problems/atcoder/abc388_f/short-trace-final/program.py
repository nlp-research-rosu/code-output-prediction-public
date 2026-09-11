import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, interval_count, minimum_step, maximum_step = data[:4]
intervals = [(data[index], data[index + 1]) for index in range(4, len(data), 2)]
window_mask = (1 << maximum_step) - 1
jump_mask = sum((1 << jump - 1 for jump in range(minimum_step, maximum_step + 1)))
state = 1
position = 1

def advance_safe(length, state):
    if length <= 0 or state == 0:
        return state
    if minimum_step == maximum_step:
        length %= maximum_step
    else:
        length = min(length, minimum_step * maximum_step + 2 * maximum_step)
    for _ in range(length):
        reachable = int(bool(state & jump_mask))
        state = state << 1 & window_mask | reachable
    return state
for left, right in intervals:
    state = advance_safe(left - position - 1, state)
    position = left - 1
    bad_length = right - left + 1
    if bad_length >= maximum_step:
        state = 0
        break
    for _ in range(bad_length):
        state = state << 1 & window_mask
    position = right
state = advance_safe(n - position, state)
print('Yes' if state & 1 else 'No')
