import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import heapq
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
test_count = data[0]
index = 1
answers = []
for _ in range(test_count):
    n, k = (data[index], data[index + 1])
    index += 2
    first = data[index:index + n]
    index += n
    second = data[index:index + n]
    index += n
    selected = []
    total = 0
    answer = 10 ** 30
    for maximum, value in sorted(zip(first, second)):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'k': k, 'maximum': maximum, 'selected': selected, 'total': total, 'value': value}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        heapq.heappush(selected, -value)
        total += value
        if len(selected) > k:
            total += heapq.heappop(selected)
        if len(selected) == k:
            answer = min(answer, maximum * total)
    answers.append(answer)
print(*answers, sep='\n')
