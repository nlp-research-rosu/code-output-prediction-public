import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from bisect import bisect_left
from bisect import bisect_left

class Solution:

    def shortestMatchingSubstring(self, s, p):
        first, middle, last = p.split('*')

        def occurrences(part):
            if not part:
                return list(range(len(s) + 1))
            positions = []
            start = s.find(part)
            while start >= 0:
                positions.append(start)
                start = s.find(part, start + 1)
            return positions
        first_positions = occurrences(first)
        middle_positions = occurrences(middle)
        last_positions = occurrences(last)
        answer = len(s) + 1
        for start in first_positions:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'first_positions': first_positions, 'last_index': last_index, 'last_positions': last_positions, 'middle_index': middle_index, 'middle_positions': middle_positions, 'middle_start': middle_start, 'start': start}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            middle_index = bisect_left(middle_positions, start + len(first))
            if middle_index == len(middle_positions):
                continue
            middle_start = middle_positions[middle_index]
            last_index = bisect_left(last_positions, middle_start + len(middle))
            if last_index == len(last_positions):
                continue
            answer = min(answer, last_positions[last_index] + len(last) - start)
        return answer if answer <= len(s) else -1

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
        if isinstance(value, dict) and all((name in value for name in names)):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError('input argument count does not match the solution signature')
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('s', 'p'))
    result = Solution().shortestMatchingSubstring(data['s'], data['p'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
