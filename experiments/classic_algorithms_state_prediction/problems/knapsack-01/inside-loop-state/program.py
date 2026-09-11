import json

def main():
    __target_count = 0
    n, capacity = map(int, input().split())
    items = [tuple(map(int, input().split())) for _ in range(n)]
    dp = [0] * (capacity + 1)
    for index, (weight, value) in enumerate(items):
        for current_capacity in range(capacity, 0, -1):
            __target_count += 1
            if __target_count == 1560:
                print(json.dumps({'dp': dp, 'items': items}, separators=(",", ":"), sort_keys=True))
                return
            if weight <= current_capacity:
                dp[current_capacity] = max(dp[current_capacity], dp[current_capacity - weight] + value)
    print(dp[capacity])


if __name__ == "__main__":
    main()
