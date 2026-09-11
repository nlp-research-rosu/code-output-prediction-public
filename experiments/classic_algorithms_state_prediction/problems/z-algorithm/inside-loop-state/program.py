import json


def main():
    __target_count = 0
    text = input().strip()
    z = [0] * len(text)
    left = 0
    right = 0
    for index in range(1, len(text)):
        __target_count += 1
        if __target_count == 248:
            print(json.dumps({'left': left, 'right': right, 'text': text, 'z': z}, separators=(",", ":"), sort_keys=True))
            return
        if index <= right:
            z[index] = min(right - index + 1, z[index - left])
        while index + z[index] < len(text) and text[z[index]] == text[index + z[index]]:
            z[index] += 1
        if index + z[index] - 1 > right:
            left = index
            right = index + z[index] - 1
    print(json.dumps(z, separators=(",", ":")))


if __name__ == "__main__":
    main()
