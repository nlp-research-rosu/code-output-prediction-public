import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def countSubstrings(self, s):
        result = 0
        for i in list(range(len(s))):
            if s[i] in ('1', '2', '5'):
                result += i + 1
        remain = 0
        cnt = [0] * 3
        cnt[0] = 1
        for i in list(range(len(s))):
            remain = (remain + (ord(s[i]) - ord('0'))) % 3
            if s[i] in ('3', '6'):
                result += cnt[remain]
            cnt[remain] += 1
        remain = 0
        cnt = [0] * 9
        cnt[0] = 1
        for i in list(range(len(s))):
            remain = (remain + (ord(s[i]) - ord('0'))) % 9
            if s[i] == '9':
                result += cnt[remain]
            cnt[remain] += 1
        for i in list(range(len(s))):
            if s[i] == '4':
                result += 1
                if i - 1 >= 0 and int(s[i - 1:i + 1]) % 4 == 0:
                    result += i
        for i in list(range(len(s))):
            if s[i] == '8':
                result += 1
                if i - 1 >= 0 and int(s[i - 1:i + 1]) % 8 == 0:
                    result += 1
                if i - 2 >= 0 and int(s[i - 2:i + 1]) % 8 == 0:
                    result += i - 1
        base = 1
        remain = 0
        cnt = [0] * 7
        for i in list(range(len(s))):
            _lcb_count[0] += 1
            remain = (remain + base * (ord(s[~i]) - ord('0'))) % 7
            result += cnt[remain]
            if s[~i] == '7':
                result += 1
                cnt[remain] += 1
            base = base * 10 % 7
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'base': base, 'cnt': cnt, 'i': i, 'remain': remain, 'result': result, 's': s}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        return result

def function(s):
    return Solution().countSubstrings(s=s)

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
    data = _read_lcb_input(('s',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
