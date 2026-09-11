import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys
from functools import cmp_to_key
from functools import cmp_to_key

class Solution:

    def minDamage(self, power, damage, health):
        hits = [(value + power - 1) // power for value in health]

        def compare(left, right):
            return hits[left] * damage[right] - hits[right] * damage[left]
        order = sorted(range(len(damage)), key=cmp_to_key(compare))
        elapsed = 0
        answer = 0
        for index in order:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'answer': answer, 'damage[index]': damage[index], 'elapsed': elapsed, 'hits[index]': hits[index], 'index': index, 'len(order)': len(order)}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            elapsed += hits[index]
            answer += elapsed * damage[index]
        return answer

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
    data = _read_lcb_input(('power', 'damage', 'health'))
    result = Solution().minDamage(data['power'], data['damage'], data['health'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
