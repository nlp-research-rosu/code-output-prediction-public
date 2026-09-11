import math


n = int(input())

low, high = 0, 1_000_001
while high - low > 1:
    middle = (low + high) // 2
    if middle**3 <= n:
        low = middle
    else:
        high = middle

for difference in range(1, low + 1):
    if n % difference:
        continue
    discriminant = 12 * (n // difference) - 3 * difference * difference
    root = math.isqrt(discriminant)
    numerator = root - 3 * difference
    if root * root != discriminant or numerator < 0 or numerator % 6:
        continue
    y = numerator // 6
    x = y + difference
    if x**3 - y**3 == n:
        print(x, y)
        break
else:
    print(-1)
