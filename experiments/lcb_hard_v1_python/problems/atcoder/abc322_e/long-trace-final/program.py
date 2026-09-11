import sys
from collections import defaultdict

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    K = int(data[idx])
    idx += 1
    P = int(data[idx])
    idx += 1
    plans = []
    for _ in range(N):
        C = int(data[idx])
        idx += 1
        A = list(map(int, data[idx:idx + K]))
        idx += K
        plans.append((C, A))
    dp = defaultdict(lambda: float('inf'))
    dp[tuple([0] * K)] = 0
    for C, A in plans:
        new_dp = dp.copy()
        for state in dp:
            new_params = list(state)
            for i in range(K):
                new_params[i] += A[i]
                if new_params[i] > P:
                    new_params[i] = P
            new_state = tuple(new_params)
            if dp[state] + C < new_dp[new_state]:
                new_dp[new_state] = dp[state] + C
        dp = new_dp
    target = tuple([P] * K)
    if dp[target] == float('inf'):
        print(-1)
    else:
        print(dp[target])
if __name__ == '__main__':
    main()
