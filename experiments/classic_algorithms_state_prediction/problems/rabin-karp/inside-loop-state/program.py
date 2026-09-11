import json


def main():
    __target_count = 0
    text = input().strip()
    pattern = input().strip()
    base = 257
    modulus = 1000000007
    length = len(pattern)
    power = pow(base, length - 1, modulus)
    pattern_hash = 0
    window_hash = 0
    for index in range(length):
        pattern_hash = (pattern_hash * base + ord(pattern[index])) % modulus
        window_hash = (window_hash * base + ord(text[index])) % modulus
    matches = []
    for start in range(len(text) - length + 1):
        __target_count += 1
        if __target_count == 238:
            print(json.dumps({'matches': matches, 'pattern': pattern, 'pattern_hash': pattern_hash, 'text': text, 'window_hash': window_hash}, separators=(",", ":"), sort_keys=True))
            return
        if window_hash == pattern_hash and text[start:start + length] == pattern:
            matches.append(start)
        if start + length < len(text):
            window_hash = (window_hash - ord(text[start]) * power) % modulus
            window_hash = (window_hash * base + ord(text[start + length])) % modulus
    print(json.dumps(matches, separators=(",", ":")))


if __name__ == "__main__":
    main()
