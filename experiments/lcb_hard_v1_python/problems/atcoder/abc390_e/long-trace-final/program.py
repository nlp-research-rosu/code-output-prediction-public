import sys

def main():
    input = sys.stdin.read().split()
    idx = 0
    N = int(input[idx])
    idx += 1
    X = int(input[idx])
    idx += 1
    v1 = []
    v2 = []
    v3 = []
    for _ in range(N):
        V = int(input[idx])
        idx += 1
        A = int(input[idx])
        idx += 1
        C = int(input[idx])
        idx += 1
        if V == 1:
            v1.append((A, C))
        elif V == 2:
            v2.append((A, C))
        else:
            v3.append((A, C))

    def compute_maxA(items, X):
        INF = float('-inf')
        dp = [INF] * (X + 1)
        dp[0] = 0
        for a, c in items:
            for j in range(X, c - 1, -1):
                if dp[j - c] != INF:
                    if dp[j] < dp[j - c] + a:
                        dp[j] = dp[j - c] + a
        maxA = [0] * (X + 1)
        current_max = 0
        for i in range(X + 1):
            if dp[i] > current_max:
                current_max = dp[i]
            maxA[i] = current_max
        return maxA
    maxA1 = compute_maxA(v1, X)
    maxA2 = compute_maxA(v2, X)
    maxA3 = compute_maxA(v3, X)
    sum1 = sum((a for a, c in v1))
    sum2 = sum((a for a, c in v2))
    sum3 = sum((a for a, c in v3))
    upper_bound = min(sum1, sum2, sum3)
    low = 0
    high = upper_bound
    answer = 0

    def find_min_c(maxA, X, target):
        left = 0
        right = X
        res = -1
        while left <= right:
            m = (left + right) // 2
            if maxA[m] >= target:
                res = m
                right = m - 1
            else:
                left = m + 1
        return res
    while low <= high:
        mid = (low + high) // 2
        c1 = find_min_c(maxA1, X, mid)
        if c1 == -1:
            possible = False
        else:
            c2 = find_min_c(maxA2, X, mid)
            if c2 == -1:
                possible = False
            else:
                c3 = find_min_c(maxA3, X, mid)
                if c3 == -1:
                    possible = False
                else:
                    possible = c1 + c2 + c3 <= X
        if possible:
            answer = mid
            low = mid + 1
        else:
            high = mid - 1
    print(answer)
if __name__ == '__main__':
    main()
