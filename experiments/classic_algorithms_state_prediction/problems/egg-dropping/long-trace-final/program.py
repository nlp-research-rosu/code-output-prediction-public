import json


def main():
    eggs, floors = map(int, input().split())
    dp = [[0] * (floors + 1) for _ in range(eggs + 1)]
    choice = [[0] * (floors + 1) for _ in range(eggs + 1)]
    for floor in range(floors + 1):
        dp[1][floor] = floor
    for egg in range(2, eggs + 1):
        for floor in range(1, floors + 1):
            dp[egg][floor] = 10**30
            for drop in range(1, floor + 1):
                candidate = 1 + max(dp[egg - 1][drop - 1], dp[egg][floor - drop])
                if candidate < dp[egg][floor]:
                    dp[egg][floor] = candidate
                    choice[egg][floor] = drop
    print(json.dumps({"minimum_trials": dp[eggs][floors]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
