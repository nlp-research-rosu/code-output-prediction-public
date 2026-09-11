import json


def cross(origin, left, right):
    return (left[0] - origin[0]) * (right[1] - origin[1]) - (left[1] - origin[1]) * (right[0] - origin[0])


def main():
    points = sorted(set(map(tuple, json.load(__import__("sys").stdin))))
    if len(points) <= 1:
        print(json.dumps(points, separators=(",", ":")))
        return
    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    hull = lower[:-1] + upper[:-1]
    print(json.dumps({'lower': lower, 'points': points}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
