import sys

def main():
    H, W = map(int, sys.stdin.readline().split())
    rows = [sys.stdin.readline().strip() for _ in range(H)]
    size = 1 << W
    count = [0] * size
    for row in rows:
        mask = int(row, 2)
        count[mask] += 1
    g = [0] * size
    for x in range(size):
        bits = bin(x).count('1')
        g[x] = min(bits, W - bits)

    def walsh_hadamard_transform(a, invert):
        n = len(a)
        h = 1
        while h < n:
            for i in range(0, n, h * 2):
                for j in range(i, i + h):
                    x = a[j]
                    y = a[j + h]
                    a[j] = x + y
                    a[j + h] = x - y
            h <<= 1
        if invert:
            for i in range(n):
                a[i] //= n
    walsh_hadamard_transform(count, invert=False)
    walsh_hadamard_transform(g, invert=False)
    product = [count[i] * g[i] for i in range(size)]
    walsh_hadamard_transform(product, invert=True)
    print(min(product))
if __name__ == '__main__':
    main()
