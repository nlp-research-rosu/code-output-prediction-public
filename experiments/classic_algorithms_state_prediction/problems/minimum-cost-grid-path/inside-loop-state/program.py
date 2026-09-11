import json


def main():
    __target_count = 0
    grid = json.load(__import__("sys").stdin)
    rows = len(grid)
    columns = len(grid[0])
    dp = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            __target_count += 1
            if __target_count == 312:
                print(json.dumps({'columns': columns, 'dp': dp, 'grid': grid, 'rows': rows}, separators=(",", ":"), sort_keys=True))
                return
            if row == 0 and column == 0:
                dp[row][column] = grid[row][column]
            elif row == 0:
                dp[row][column] = dp[row][column - 1] + grid[row][column]
            elif column == 0:
                dp[row][column] = dp[row - 1][column] + grid[row][column]
            else:
                dp[row][column] = min(dp[row - 1][column], dp[row][column - 1]) + grid[row][column]
    print(json.dumps({"minimum_cost": dp[-1][-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
