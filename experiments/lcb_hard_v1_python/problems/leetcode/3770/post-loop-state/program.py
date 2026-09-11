import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys

class Solution:

    def generateString(self, s: str, t: str) -> str:
        n, m = (len(s), len(t))
        ans = ['a'] * (n + m - 1)
        fixed = [False] * (n + m - 1)
        for i, b in enumerate(s):
            if b != 'T':
                continue
            for j, c in enumerate(t):
                _lcb_count[0] += 1
                k = i + j
                if fixed[k] and ans[k] != c:
                    return ''
                ans[k] = c
                fixed[k] = True
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'ans': ans, 'b': b, 'c': c, 'fixed': fixed, 'i': i, 'j': j, 'k': k, 't': t}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
        for i, b in enumerate(s):
            if b != 'F':
                continue
            if ''.join(ans[i:i + m]) != t:
                continue
            for j in range(i + m - 1, i - 1, -1):
                if not fixed[j]:
                    ans[j] = 'b'
                    break
            else:
                return ''
        return ''.join(ans)

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
    data = _read_lcb_input(('str1', 'str2'))
    result = Solution().generateString(data['str1'], data['str2'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
