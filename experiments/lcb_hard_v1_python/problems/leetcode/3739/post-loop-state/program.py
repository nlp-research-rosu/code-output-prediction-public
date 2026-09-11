import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
MOD = 10 ** 9 + 7
FACT, INV, INV_FACT = [[1] * 2 for _ in list(range(3))]

def nCr(n, k):
    while len(INV) <= n:
        _lcb_count[0] += 1
        size = len(INV)
        factorial = FACT[-1] * size % MOD
        inverse = INV[MOD % size] * (MOD - MOD // size) % MOD
        inverse_factorial = INV_FACT[-1] * inverse % MOD
        FACT.append(factorial)
        INV.append(inverse)
        INV_FACT.append(inverse_factorial)
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'FACT[-5:]': FACT[-5:], 'INV[-5:]': INV[-5:], 'INV_FACT[-5:]': INV_FACT[-5:], 'factorial': factorial, 'inverse': inverse, 'inverse_factorial': inverse_factorial, 'len(INV)': len(INV), 'size': size}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    return FACT[n] * INV_FACT[n - k] % MOD * INV_FACT[k] % MOD

class Solution(object):

    def distanceSum(self, m, n, k):

        def sum_n(n):
            return (n + 1) * n // 2

        def sum_n_square(n):
            return n * (n + 1) * (2 * n + 1) // 6

        def f(n):
            return n * sum_n(n - 1) - sum_n_square(n - 1)
        return (f(n) * m * m + f(m) * n * n) * nCr(m * n - 2, k - 2) % MOD

def function(m, n, k):
    return Solution().distanceSum(m=m, n=n, k=k)

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
    data = _read_lcb_input(('m', 'n', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
