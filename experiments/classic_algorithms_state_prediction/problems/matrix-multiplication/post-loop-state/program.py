import json


def main():
    n = int(input())
    left = [list(map(int, input().split())) for _ in range(n)]
    right = [list(map(int, input().split())) for _ in range(n)]
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += left[i][k] * right[k][j]
            result[i][j] = total
    print(json.dumps({'left': left, 'n': n, 'result': result, 'right': right}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
