import json


def main():
    __target_count = 0
    n = int(input())
    dist = [list(map(int, input().split())) for _ in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                __target_count += 1
                if __target_count == 1347:
                    print(json.dumps({'dist': dist, 'n': n}, separators=(",", ":"), sort_keys=True))
                    return
                candidate = dist[i][k] + dist[k][j]
                if candidate < dist[i][j]:
                    dist[i][j] = candidate
    print(json.dumps(dist, separators=(",", ":")))


if __name__ == "__main__":
    main()
