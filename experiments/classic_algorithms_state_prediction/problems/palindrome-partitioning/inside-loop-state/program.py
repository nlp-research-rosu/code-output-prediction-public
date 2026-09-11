import json


def main():
    __target_count = 0
    text = input().strip()
    n = len(text)
    palindrome = [[False] * n for _ in range(n)]
    cuts = list(range(n))
    for right in range(n):
        for left in range(right + 1):
            __target_count += 1
            if __target_count == 639:
                print(json.dumps({'cuts': cuts, 'palindrome': palindrome, 'text': text}, separators=(",", ":"), sort_keys=True))
                return
            if text[left] == text[right] and (right - left <= 2 or palindrome[left + 1][right - 1]):
                palindrome[left][right] = True
                cuts[right] = 0 if left == 0 else min(cuts[right], cuts[left - 1] + 1)
    print(json.dumps({"minimum_cuts": cuts[-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
