import sys

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    K = int(input[1])
    A = list(map(int, input[2:2 + N]))
    if N == 0:
        return
    max_A = max(A)
    freq = [0] * (max_A + 1)
    for x in A:
        freq[x] += 1
    cnt = [0] * (max_A + 1)
    for d in range(1, max_A + 1):
        for multiple in range(d, max_A + 1, d):
            cnt[d] += freq[multiple]
    ans = [0] * (max_A + 1)
    for d in range(max_A, 0, -1):
        if cnt[d] >= K:
            for multiple in range(d, max_A + 1, d):
                if ans[multiple] == 0:
                    ans[multiple] = d
    for x in A:
        print(ans[x])
if __name__ == '__main__':
    main()
