import json


def sign(value):
    return (value > 0) - (value < 0)


def main():
    n, steps = map(int, input().split())
    rows = [list(map(int, input().split())) for _ in range(n)]
    positions = [[row[0], row[1]] for row in rows]
    velocities = [[row[2], row[3]] for row in rows]
    for step in range(steps):
        acceleration = [[0, 0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx = positions[j][0] - positions[i][0]
                dy = positions[j][1] - positions[i][1]
                sx, sy = sign(dx), sign(dy)
                acceleration[i][0] += sx
                acceleration[i][1] += sy
                acceleration[j][0] -= sx
                acceleration[j][1] -= sy
        for i in range(n):
            velocities[i][0] += acceleration[i][0]
            velocities[i][1] += acceleration[i][1]
            positions[i][0] += velocities[i][0]
            positions[i][1] += velocities[i][1]
    print(json.dumps({'positions': positions, 'velocities': velocities}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
