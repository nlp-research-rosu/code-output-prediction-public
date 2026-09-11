import json


def main():
    __target_count = 0
    n = int(input())
    dimensions = list(map(int, input().split()))
    infinity = 10**30
    dp = [[0] * n for _ in range(n)]
    for chain_length in range(2, n + 1):
        for left in range(n - chain_length + 1):
            right = left + chain_length - 1
            dp[left][right] = infinity
            for split in range(left, right):
                __target_count += 1
                if __target_count == 1037:
                    print(json.dumps({'dimensions': dimensions, 'dp': dp}, separators=(",", ":"), sort_keys=True))
                    return
                cost = dp[left][split] + dp[split + 1][right] + dimensions[left] * dimensions[split + 1] * dimensions[right + 1]
                if cost < dp[left][right]:
                    dp[left][right] = cost
    print(json.dumps({"minimum_cost": dp[0][n - 1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
