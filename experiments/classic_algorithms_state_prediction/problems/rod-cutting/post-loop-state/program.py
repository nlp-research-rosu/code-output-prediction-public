import json


def main():
    data = json.load(__import__("sys").stdin)
    prices = data["prices"]
    length = data["length"]
    best = [0] * (length + 1)
    first_cut = [0] * (length + 1)
    for current in range(1, length + 1):
        for cut in range(1, min(current, len(prices)) + 1):
            candidate = prices[cut - 1] + best[current - cut]
            if candidate > best[current]:
                best[current] = candidate
                first_cut[current] = cut
    print(json.dumps({'best': best, 'first_cut': first_cut, 'length': length, 'prices': prices}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
