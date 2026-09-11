import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
MOD = 10 ** 9 + 7
FACT, INV, INV_FACT = [[1] * 2 for _ in list(range(3))]

def nCr(n, k):
    while len(INV) <= n:
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'FACT[-5:]': FACT[-5:], 'INV[-5:]': INV[-5:], 'INV_FACT[-5:]': INV_FACT[-5:], 'factorial': factorial, 'inverse': inverse, 'inverse_factorial': inverse_factorial, 'len(INV)': len(INV), 'size': size}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        size = len(INV)
        factorial = FACT[-1] * size % MOD
        inverse = INV[MOD % size] * (MOD - MOD // size) % MOD
        inverse_factorial = INV_FACT[-1] * inverse % MOD
        FACT.append(factorial)
        INV.append(inverse)
        INV_FACT.append(inverse_factorial)
    return FACT[n] * INV_FACT[n - k] % MOD * INV_FACT[k] % MOD

class Solution(object):

    def countGoodArrays(self, n, m, k):
        return nCr(n - 1, k) * (m * pow(m - 1, n - 1 - k, MOD)) % MOD

def function(n, m, k):
    return Solution().countGoodArrays(n=n, m=m, k=k)

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
    data = _read_lcb_input(('n', 'm', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
