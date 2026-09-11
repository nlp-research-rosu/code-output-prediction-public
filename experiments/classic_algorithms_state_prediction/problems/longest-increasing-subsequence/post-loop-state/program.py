import json


def main():
    values = json.load(__import__("sys").stdin)
    n = len(values)
    length = [1] * n
    parent = [-1] * n
    for right in range(n):
        for left in range(right):
            if values[left] < values[right] and length[left] + 1 > length[right]:
                length[right] = length[left] + 1
                parent[right] = left
    end = max(range(n), key=length.__getitem__)
    sequence = []
    while end != -1:
        sequence.append(values[end])
        end = parent[end]
    print(json.dumps({'length': length, 'parent': parent, 'values': values}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
