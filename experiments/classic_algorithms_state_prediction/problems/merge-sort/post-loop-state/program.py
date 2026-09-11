import json


def main():
    values = json.load(__import__("sys").stdin)
    n = len(values)
    buffer = [0] * n
    width = 1
    while width < n:
        for start in range(0, n, 2 * width):
            middle = min(start + width, n)
            end = min(start + 2 * width, n)
            left = start
            right = middle
            for target in range(start, end):
                if left < middle and (right >= end or values[left] <= values[right]):
                    buffer[target] = values[left]
                    left += 1
                else:
                    buffer[target] = values[right]
                    right += 1
        values, buffer = buffer, values
        width *= 2
    print(json.dumps({'buffer': buffer, 'values': values, 'width': width}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
