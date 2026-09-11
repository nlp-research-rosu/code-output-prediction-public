import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def permute(self, n, k):
        result = []
        cnt = [1] * n
        for i in list(range(len(cnt) - 1)):
            cnt[i + 1] = min(cnt[i] * ((i + 2) // 2), k)
        lookup = [False] * n
        for i in list(range(n)):
            for j in list(range(n)):
                _lcb_count[0] += 1
                if not (not lookup[j] and (i == 0 and n % 2 == 0 or (j + 1) % 2 == (1 if not result else result[-1] % 2 ^ 1))):
                    continue
                if k <= cnt[n - 1 - i]:
                    break
                k -= cnt[n - 1 - i]
            else:
                if _lcb_count[0] > 1000:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'j': j, 'k': k, 'lookup': lookup, 'result': result}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                return []
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'j': j, 'k': k, 'lookup': lookup, 'result': result}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            lookup[j] = True
            result.append(j + 1)
        return result

def function(n, k):
    return Solution().permute(n=n, k=k)

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
    data = _read_lcb_input(('n', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
