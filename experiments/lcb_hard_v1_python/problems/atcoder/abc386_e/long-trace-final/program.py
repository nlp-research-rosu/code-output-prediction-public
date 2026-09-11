import sys
import itertools

def main():
    N, K = map(int, input().split())
    A = list(map(int, input().split()))
    max_xor = 0
    for subset in itertools.combinations(A, K):
        current_xor = 0
        for num in subset:
            current_xor ^= num
        max_xor = max(max_xor, current_xor)
    print(max_xor)
if __name__ == '__main__':
    main()
