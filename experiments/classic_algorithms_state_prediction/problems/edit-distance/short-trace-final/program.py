def main():
    source = input().strip()
    target = input().strip()
    previous = list(range(len(target) + 1))
    for i in range(1, len(source) + 1):
        current = [i] + [0] * len(target)
        for j in range(1, len(target) + 1):
            if source[i - 1] == target[j - 1]:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        previous = current
    print(previous[-1])


if __name__ == "__main__":
    main()
