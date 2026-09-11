import sys

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    M = int(input[1])
    result = []
    current = []

    def backtrack(index):
        if index == N:
            result.append(current.copy())
            return
        min_val = 1 if index == 0 else current[-1] + 10
        max_val = M - (N - (index + 1)) * 10
        max_val = min(max_val, M)
        for val in range(min_val, max_val + 1):
            if val <= M:
                current.append(val)
                backtrack(index + 1)
                current.pop()
    backtrack(0)
    print(len(result))
    for seq in result:
        print(' '.join(map(str, seq)))
if __name__ == '__main__':
    main()
