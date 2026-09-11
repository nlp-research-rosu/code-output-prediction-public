import json, sys
import heapq
import itertools

class Solution(object):

    def maximumValueSum(self, board):
        k = 3
        min_heaps = [[] for _ in list(range(len(board[0])))]
        for i in list(range(len(board))):
            min_heap = []
            for j in list(range(len(board[0]))):
                heapq.heappush(min_heap, (board[i][j], i, j))
                if len(min_heap) == k + 1:
                    heapq.heappop(min_heap)
            for v, i, j in min_heap:
                heapq.heappush(min_heaps[j], (v, i, j))
                if len(min_heaps[j]) == k + 1:
                    heapq.heappop(min_heaps[j])
        min_heap = []
        for h in min_heaps:
            for x in h:
                heapq.heappush(min_heap, x)
                if len(min_heap) == (k - 1) * (2 * k - 1) + 1 + 1:
                    heapq.heappop(min_heap)
        return max((sum((x[0] for x in c)) for c in itertools.combinations(min_heap, k) if len({x[1] for x in c}) == k == len({x[2] for x in c})))

def function(board):
    return Solution().maximumValueSum(board=board)

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
    data = _read_lcb_input(('board',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
