import sys

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    A = list(map(int, data[idx:idx + N]))
    idx += N
    Q = int(data[idx])
    idx += 1
    queries = []
    for _ in range(Q):
        L = int(data[idx])
        R = int(data[idx + 1])
        queries.append((L, R))
        idx += 2
    for L, R in queries:
        m = R - L + 1
        if m < 2:
            print(0)
            continue
        B = A[L - 1:R]
        left = 0
        right = m // 2
        ans = 0
        while left <= right:
            mid = (left + right) // 2
            ok = True
            for i in range(mid):
                if B[i] * 2 > B[m - mid + i]:
                    ok = False
                    break
            if ok:
                ans = mid
                left = mid + 1
            else:
                right = mid - 1
        print(ans)
if __name__ == '__main__':
    main()
