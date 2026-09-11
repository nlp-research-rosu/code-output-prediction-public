import json, sys

class Solution(object):

    def makeStringGood(self, s):
        cnt = [0] * 26
        for x in s:
            cnt[ord(x) - ord('a')] += 1
        result = len(s)
        for f in list(range(min((x for x in cnt if x)), max(cnt) + 1)):
            dp1 = dp2 = 0
            for i in list(range(26)):
                if not cnt[i]:
                    continue
                if cnt[i] >= f:
                    new_dp1 = len(s)
                    new_dp2 = min(dp1, dp2) + (cnt[i] - f)
                else:
                    free = (cnt[i - 1] - f if cnt[i - 1] >= f else cnt[i - 1]) if i - 1 >= 0 else 0
                    new_dp1 = min(min(dp1, dp2) + (f - cnt[i]), dp2 + max(f - cnt[i] - free, 0))
                    new_dp2 = min(dp1, dp2) + cnt[i]
                dp1, dp2 = (new_dp1, new_dp2)
            result = min(result, dp1, dp2)
        return result

def function(s):
    return Solution().makeStringGood(s=s)

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
    data = _read_lcb_input(('s',))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
