import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def minOperations(self, queries):
        result = 0
        for l, r in queries:
            total = 0
            base = i = 1
            while base <= r:
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'base': base, 'i': i, 'l': l, 'nl': nl, 'nr': nr, 'r': r, 'result': result, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                nl, nr = (max(l, base), min(r, 4 * base - 1))
                if nl <= nr:
                    total += i * (nr - nl + 1)
                i += 1
                base *= 4
            result += (total + 1) // 2
        return result

def function(queries):
    return Solution().minOperations(queries=queries)

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
    data = _read_lcb_input(('queries',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
