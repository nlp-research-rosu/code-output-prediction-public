import sys

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    A = list(map(int, data[1:N + 1]))
    prefix = [0] * (N + 1)
    distinct = set()
    for i in range(1, N + 1):
        if A[i - 1] not in distinct:
            distinct.add(A[i - 1])
        prefix[i] = len(distinct)
    suffix = [0] * (N + 2)
    distinct = set()
    for i in range(N, 0, -1):
        if A[i - 1] not in distinct:
            distinct.add(A[i - 1])
        suffix[i] = len(distinct)
    max_sum = 0
    current_distinct = 0
    from collections import defaultdict
    count = defaultdict(int)
    present = set()
    for j in range(1, N + 1):
        current_distinct = 0
        present = set()
        max_current = 0
        for i in range(j - 1, -1, -1):
            if A[i] not in present:
                current_distinct += 1
                present.add(A[i])
            current_val = prefix[i] + current_distinct
            if current_val > max_current:
                max_current = current_val
        total = max_current + suffix[j + 1]
        if total > max_sum:
            max_sum = total
    print(max_sum)
if __name__ == '__main__':
    main()
