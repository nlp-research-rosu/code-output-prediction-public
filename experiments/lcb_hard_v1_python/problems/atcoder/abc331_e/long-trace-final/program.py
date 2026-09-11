import sys

def main() -> None:
    n, m, l = map(int, input().split())
    a = list(map(int, input().split()))
    b = list(map(int, input().split()))
    out = set()
    for i in range(l):
        c, d = map(int, input().split())
        out.add(c * 10 ** 6 + d)
    bb = [(b[i], i + 1) for i in range(m)]
    bb.sort()
    ans = []
    for i in range(n):
        t = m - 1
        while True:
            if t < 0:
                break
            num = (i + 1) * 10 ** 6 + bb[t][1]
            if num in out:
                t -= 1
            else:
                ans.append(a[i] + bb[t][0])
                break
    print(max(ans))
if __name__ == '__main__':
    main()
