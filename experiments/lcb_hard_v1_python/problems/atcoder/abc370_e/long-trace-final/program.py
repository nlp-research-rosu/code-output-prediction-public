import sys
MOD = 998244353

def main():
    import sys
    from collections import defaultdict
    N, K = map(int, sys.stdin.readline().split())
    A = list(map(int, sys.stdin.readline().split()))
    prefix = 0
    total = 1
    prefix_map = defaultdict(int)
    prefix_map[0] = 1
    for i in range(1, N + 1):
        prefix += A[i - 1]
        c = prefix - K
        sum_forbidden = prefix_map.get(c, 0)
        dp_i = (total - sum_forbidden) % MOD
        total = (total + dp_i) % MOD
        prefix_map[prefix] = (prefix_map[prefix] + dp_i) % MOD
    print(dp_i % MOD)
if __name__ == '__main__':
    main()
