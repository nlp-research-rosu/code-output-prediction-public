import sys
input = sys.stdin.readline

def main() -> None:
    L, R = map(int, input().split())
    a, b = (L, -1)
    lr = []
    while b < R:
        i, j = (0, 0)
        flag = False
        for k in reversed(range(63)):
            if flag:
                continue
            if a % 2 ** k == 0:
                i = k
                j = a // 2 ** i
                a = 2 ** i * j
                b = 2 ** i * (j + 1)
                if b <= R:
                    flag = True
                    lr.append((a, b))
                    a = b
                    break
    print(len(lr))
    for l, r in lr:
        print(l, r)
if __name__ == '__main__':
    main()
