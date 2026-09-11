import json


def main():
    __target_count = 0
    data = json.load(__import__("sys").stdin)
    values = data["values"]
    target = data["target"]
    dp = [[False] * (target + 1) for _ in range(len(values) + 1)]
    dp[0][0] = True
    for index, value in enumerate(values, start=1):
        for total in range(target + 1):
            __target_count += 1
            if __target_count == 1263:
                print(json.dumps({'dp': dp, 'target': target, 'values': values}, separators=(",", ":"), sort_keys=True))
                return
            dp[index][total] = dp[index - 1][total] or (total >= value and dp[index - 1][total - value])
    print(json.dumps({"reachable": dp[-1][target]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
