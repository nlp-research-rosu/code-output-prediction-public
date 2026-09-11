import json


def main():
    n = int(input())
    dist = [list(map(int, input().split())) for _ in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                candidate = dist[i][k] + dist[k][j]
                if candidate < dist[i][j]:
                    dist[i][j] = candidate
    print(json.dumps(dist, separators=(",", ":")))


if __name__ == "__main__":
    main()
