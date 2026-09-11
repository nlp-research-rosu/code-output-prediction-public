import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import math
n = int(input())
low, high = (0, 1000001)
while high - low > 1:
    middle = (low + high) // 2
    if middle ** 3 <= n:
        low = middle
    else:
        high = middle
for difference in range(1, low + 1):
    _lcb_count[0] += 1
    if _lcb_count[0] > 501:
        _lcb_sys.stdout.write(_lcb_json.dumps({'difference': difference, 'discriminant': discriminant, 'high': high, 'low': low, 'middle': middle, 'n': n, 'numerator': numerator, 'root': root}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    if n % difference:
        continue
    discriminant = 12 * (n // difference) - 3 * difference * difference
    root = math.isqrt(discriminant)
    numerator = root - 3 * difference
    if root * root != discriminant or numerator < 0 or numerator % 6:
        continue
    y = numerator // 6
    x = y + difference
    if x ** 3 - y ** 3 == n:
        print(x, y)
        break
else:
    print(-1)
