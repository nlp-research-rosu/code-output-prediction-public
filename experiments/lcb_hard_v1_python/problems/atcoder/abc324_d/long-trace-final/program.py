import sys

def main() -> None:
    n = int(input())
    s = input()
    t = [i for i in s]
    t.sort(reverse=True)
    t = int(''.join(t))
    num = [0] * 10
    for i in s:
        num[int(i)] += 1
    ans = 0
    for i in range(int(t ** 0.5) + 10):
        p = list((n - len(str(i ** 2))) * '0' + str(i ** 2))
        check = [0] * 10
        for j in p:
            check[int(j)] += 1
        is_ok = True
        for a, b in zip(num, check):
            if a != b:
                is_ok = False
                break
        if is_ok:
            ans += 1
    print(ans)
if __name__ == '__main__':
    main()
