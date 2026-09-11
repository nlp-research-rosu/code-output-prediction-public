import json


def prefix_function(pattern):
    lps = [0] * len(pattern)
    matched = 0
    for i in range(1, len(pattern)):
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = lps[matched - 1]
        if pattern[i] == pattern[matched]:
            matched += 1
        lps[i] = matched
    return lps


def main():
    text = input().strip()
    pattern = input().strip()
    lps = prefix_function(pattern)
    matched = 0
    matches = []
    for index in range(len(text)):
        ch = text[index]
        while matched > 0 and ch != pattern[matched]:
            matched = lps[matched - 1]
        if ch == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            matches.append(index - len(pattern) + 1)
            matched = lps[matched - 1]
    print(json.dumps({'lps': lps, 'matched': matched, 'matches': matches, 'pattern': pattern, 'text': text}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
