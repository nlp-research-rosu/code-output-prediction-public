import json


def main():
    __target_count = 0
    data = json.load(__import__("sys").stdin)
    coins = data["coins"]
    amount = data["amount"]
    infinity = amount + 1
    dp = [0] + [infinity] * amount
    choice = [-1] * (amount + 1)
    for current in range(1, amount + 1):
        for coin in coins:
            __target_count += 1
            if __target_count == 674:
                print(json.dumps({'amount': amount, 'choice': choice, 'coins': coins, 'dp': dp}, separators=(",", ":"), sort_keys=True))
                return
            if coin <= current and dp[current - coin] + 1 < dp[current]:
                dp[current] = dp[current - coin] + 1
                choice[current] = coin
    print(json.dumps({"minimum_coins": -1 if dp[amount] == infinity else dp[amount]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
