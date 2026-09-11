import sys
sys.set_int_max_str_digits(0)
n = int(input())
s = input().strip()
powers = [1] * (n + 1)
for i in range(1, n + 1):
    powers[i] = powers[i - 1] * 10
total = 0
for i in range(n):
    digit = int(s[i])
    pos = i
    exponent = n - pos
    term = digit * (pos + 1) * (powers[exponent] - 1) // 9
    total += term
print(total)
