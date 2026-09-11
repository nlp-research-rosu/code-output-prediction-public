import sys

def main():
    input = sys.stdin.read().split()
    ptr = 0
    N = int(input[ptr])
    ptr += 1
    contests = []
    for _ in range(N):
        L = int(input[ptr])
        R = int(input[ptr + 1])
        contests.append((L, R))
        ptr += 2
    Q = int(input[ptr])
    ptr += 1
    queries = []
    for _ in range(Q):
        queries.append(int(input[ptr]))
        ptr += 1
    for X in queries:
        c = 0
        for L, R in contests:
            if X + c >= L and X + c <= R:
                c += 1
        print(X + c)
if __name__ == '__main__':
    main()
