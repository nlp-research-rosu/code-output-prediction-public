import sys
from itertools import permutations

def count_swaps(perm):
    swaps = 0
    for i in range(len(perm)):
        for j in range(i + 1, len(perm)):
            if perm[i] > perm[j]:
                swaps += 1
    return swaps

def main():
    input = sys.stdin.read
    data = input().split()
    H = int(data[0])
    W = int(data[1])
    A = []
    for i in range(H):
        A.append(list(map(int, data[2 + i * W:2 + i * W + W])))
    B = []
    for i in range(H):
        B.append(list(map(int, data[2 + H * W + i * W:2 + H * W + i * W + W])))
    flat_A = [num for row in A for num in row]
    flat_B = [num for row in B for num in row]
    if sorted(flat_A) != sorted(flat_B):
        print(-1)
        return
    min_swaps = float('inf')
    for row_perm in permutations(range(H)):
        for col_perm in permutations(range(W)):
            transformed = []
            for r in row_perm:
                new_row = [A[r][c] for c in col_perm]
                transformed.append(new_row)
            if transformed == B:
                row_swaps = count_swaps(row_perm)
                col_swaps = count_swaps(col_perm)
                total_swaps = row_swaps + col_swaps
                if total_swaps < min_swaps:
                    min_swaps = total_swaps
    if min_swaps == float('inf'):
        print(-1)
    else:
        print(min_swaps)
if __name__ == '__main__':
    main()
