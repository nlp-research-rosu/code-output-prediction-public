import json


def main():
    __target_count = 0
    values = json.load(__import__("sys").stdin)
    n = len(values)

    def sift_down(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and values[child] < values[child + 1]:
                child += 1
            if values[root] >= values[child]:
                return
            values[root], values[child] = values[child], values[root]
            root = child

    for root in range(n // 2 - 1, -1, -1):
        sift_down(root, n)
    for end in range(n - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        __target_count += 1
        if __target_count == 198:
            print(json.dumps({'n': n, 'values': values}, separators=(",", ":"), sort_keys=True))
            return
        sift_down(0, end)
    print(json.dumps(values, separators=(",", ":")))


if __name__ == "__main__":
    main()
