import bisect
import json


def main():
    intervals = json.load(__import__("sys").stdin)
    intervals.sort(key=lambda item: (item[1], item[0], item[2]))
    finishes = [item[1] for item in intervals]
    predecessor = [bisect.bisect_right(finishes, item[0]) - 1 for item in intervals]
    dp = [0] * (len(intervals) + 1)
    take = [False] * len(intervals)
    for index, (_, _, weight) in enumerate(intervals, start=1):
        include = weight + dp[predecessor[index - 1] + 1]
        exclude = dp[index - 1]
        if include > exclude:
            dp[index] = include
            take[index - 1] = True
        else:
            dp[index] = exclude
    print(json.dumps({"maximum_weight": dp[-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
