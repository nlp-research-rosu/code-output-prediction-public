import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
sys.set_int_max_str_digits(0)
n = int(input())
s = input().strip()
powers = [1] * (n + 1)
for i in range(1, n + 1):
    powers[i] = powers[i - 1] * 10
total = 0
for i in range(n):
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'digit': digit, 'exponent': exponent, 'i': i, 'n': n, 'pos': pos, 'term': term, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    digit = int(s[i])
    pos = i
    exponent = n - pos
    term = digit * (pos + 1) * (powers[exponent] - 1) // 9
    total += term
print(total)
