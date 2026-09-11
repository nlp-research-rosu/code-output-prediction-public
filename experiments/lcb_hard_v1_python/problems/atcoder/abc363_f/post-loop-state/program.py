import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import functools
import math
import sys
n = int(sys.stdin.buffer.readline())

def usable(value):
    text = str(value)
    return '0' not in text

@functools.lru_cache(maxsize=None)
def build(value):
    text = str(value)
    if usable(value) and text == text[::-1]:
        return text
    limit = math.isqrt(value)
    for factor in range(2, limit + 1):
        _lcb_count[0] += 1
        if value % factor or not usable(factor):
            continue
        reverse = int(str(factor)[::-1])
        product = factor * reverse
        if value % product:
            continue
        inside = build(value // product)
        if inside is not None:
            return f'{factor}*{inside}*{reverse}'
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'factor': factor, 'limit': limit, 'text': text, 'value': value}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    return None
print(build(n) or -1)
