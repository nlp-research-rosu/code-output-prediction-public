import json, sys
FACT, INV, INV_FACT = [[1] * 2 for _ in list(range(3))]

class Solution(object):

    def numberOfSequence(self, n, sick):
        MOD = 10 ** 9 + 7

        def nCr(n, k):
            while len(INV) <= n:
                FACT.append(FACT[-1] * len(INV) % MOD)
                INV.append(INV[MOD % len(INV)] * (MOD - MOD // len(INV)) % MOD)
                INV_FACT.append(INV_FACT[-1] * INV[-1] % MOD)
            return FACT[n] * INV_FACT[n - k] % MOD * INV_FACT[k] % MOD
        result = 1
        total = cnt = 0
        for i in list(range(len(sick) + 1)):
            l = (sick[i] if i < len(sick) else n) - (sick[i - 1] if i - 1 >= 0 else -1) - 1
            if i not in (0, len(sick)):
                cnt += max(l - 1, 0)
            total += l
            result = result * nCr(total, l) % MOD
        result = result * pow(2, cnt, MOD) % MOD
        return result

def function(n, sick):
    return Solution().numberOfSequence(n=n, sick=sick)

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
    data = _read_lcb_input(('n', 'sick'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
