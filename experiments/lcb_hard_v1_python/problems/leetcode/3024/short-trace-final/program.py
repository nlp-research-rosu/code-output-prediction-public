import json, sys
from functools import reduce

class Solution(object):

    def numberOfWays(self, s, t, k):
        MOD = 10 ** 9 + 7

        def getPrefix(pattern):
            prefix = [-1] * len(pattern)
            j = -1
            for i in list(range(1, len(pattern))):
                while j + 1 > 0 and pattern[j + 1] != pattern[i]:
                    j = prefix[j]
                if pattern[j + 1] == pattern[i]:
                    j += 1
                prefix[i] = j
            return prefix

        def KMP(text, pattern):
            prefix = getPrefix(pattern)
            j = -1
            for i in list(range(len(text))):
                while j + 1 > 0 and pattern[j + 1] != text[i]:
                    j = prefix[j]
                if pattern[j + 1] == text[i]:
                    j += 1
                if j + 1 == len(pattern):
                    yield (i - j)
                    j = prefix[j]
        n = len(s)
        dp = [0] * 2
        dp[1] = (pow(n - 1, k, MOD) - (-1) ** k) * pow(n, MOD - 2, MOD) % MOD
        dp[0] = (dp[1] + (-1) ** k) % MOD
        return reduce(lambda a, b: (a + b) % MOD, (dp[int(i != 0)] for i in KMP(s + s[:-1], t)), 0)

def function(s, t, k):
    return Solution().numberOfWays(s=s, t=t, k=k)

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
    data = _read_lcb_input(('s', 't', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
