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
        if value % factor or not usable(factor):
            continue
        reverse = int(str(factor)[::-1])
        product = factor * reverse
        if value % product:
            continue
        inside = build(value // product)
        if inside is not None:
            return f'{factor}*{inside}*{reverse}'
    return None
print(build(n) or -1)
