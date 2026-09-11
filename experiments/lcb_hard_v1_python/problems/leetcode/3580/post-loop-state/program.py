import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def minStartingIndex(self, s, pattern):
        K = 1

        def z_function(s):
            z = [0] * len(s)
            l, r = (0, 0)
            for i in list(range(1, len(z))):
                if i <= r:
                    z[i] = min(r - i + 1, z[i - l])
                while i + z[i] < len(z) and s[z[i]] == s[i + z[i]]:
                    _lcb_count[0] += 1
                    z[i] += 1
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'l': l, 'r': r, 's': s, 'z': z}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if i + z[i] - 1 > r:
                    l, r = (i, i + z[i] - 1)
            return z
        z1 = z_function(pattern + s)
        z2 = z_function(pattern[::-1] + s[::-1])
        return next((i for i in list(range(len(s) - len(pattern) + 1)) if z1[len(pattern) + i] + K + z2[len(s) - i] >= len(pattern)), -1)

def function(s, pattern):
    return Solution().minStartingIndex(s=s, pattern=pattern)

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
    data = _read_lcb_input(('s', 'pattern'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
