import json


def main():
    frequencies = json.load(__import__("sys").stdin)
    n = len(frequencies)
    prefix = [0]
    for value in frequencies:
        prefix.append(prefix[-1] + value)
    cost = [[0] * n for _ in range(n)]
    root = [[-1] * n for _ in range(n)]
    for length in range(1, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            total = prefix[right + 1] - prefix[left]
            cost[left][right] = 10**30
            for candidate_root in range(left, right + 1):
                candidate = total
                if candidate_root > left:
                    candidate += cost[left][candidate_root - 1]
                if candidate_root < right:
                    candidate += cost[candidate_root + 1][right]
                if candidate < cost[left][right]:
                    cost[left][right] = candidate
                    root[left][right] = candidate_root
    print(json.dumps({'cost': cost, 'frequencies': frequencies, 'root': root}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
