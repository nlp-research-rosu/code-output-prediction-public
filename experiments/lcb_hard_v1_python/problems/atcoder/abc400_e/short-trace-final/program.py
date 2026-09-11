import sys
import math

def main():
    input = sys.stdin.read().split()
    Q = int(input[0])
    queries = list(map(int, input[1:Q + 1]))
    max_s = 10 ** 6
    cnt = [0] * (max_s + 1)
    for i in range(2, max_s + 1):
        if cnt[i] == 0:
            for j in range(i, max_s + 1, i):
                cnt[j] += 1
    valid = [False] * (max_s + 1)
    for x in range(2, max_s + 1):
        if cnt[x] == 2:
            valid[x] = True
    max_valid = [0] * (max_s + 1)
    current_max = 0
    for x in range(1, max_s + 1):
        if valid[x]:
            current_max = x
        max_valid[x] = current_max
    for A in queries:
        S = int(math.isqrt(A))
        X = max_valid[S]
        print(X * X)
if __name__ == '__main__':
    main()
