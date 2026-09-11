import json


def main():
    text = input().strip()
    n = len(text)
    dp = [[0] * n for _ in range(n)]
    for left in range(n - 1, -1, -1):
        dp[left][left] = 1
        for right in range(left + 1, n):
            if text[left] == text[right]:
                dp[left][right] = 2 + (dp[left + 1][right - 1] if right - left > 1 else 0)
            else:
                dp[left][right] = max(dp[left + 1][right], dp[left][right - 1])
    print(json.dumps({"length": dp[0][n - 1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
