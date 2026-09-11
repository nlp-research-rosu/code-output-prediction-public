import sys

def main():
    input = sys.stdin.read
    data = input().split()
    idx = 0
    t = int(data[idx])
    idx += 1
    results = []
    for _ in range(t):
        n = int(data[idx])
        idx += 1
        a = list(map(int, data[idx:idx + n]))
        idx += n
        max_even = -float('inf')
        max_odd = -float('inf')
        result = -float('inf')
        for num in a:
            if num % 2 == 0:
                max_even = max(num, max_odd + num)
                max_odd = -float('inf')
            else:
                max_odd = max(num, max_even + num)
                max_even = -float('inf')
            result = max(result, max_even, max_odd)
        results.append(str(result))
    print('\n'.join(results))
if __name__ == '__main__':
    main()
