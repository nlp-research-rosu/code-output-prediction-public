import sys

class FenwickTree:

    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 1)

    def update(self, idx, delta):
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def query(self, idx):
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

def find_kth(ft, k, n):
    low = 1
    high = n
    while low < high:
        mid = (low + high) // 2
        sum_mid = ft.query(mid)
        if sum_mid < k:
            low = mid + 1
        else:
            high = mid
    return low

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    P = list(map(int, input[1:N + 1]))
    ft = FenwickTree(N)
    for i in range(1, N + 1):
        ft.update(i, 1)
    res = [0] * N
    for i in range(N, 0, -1):
        k = P[i - 1]
        x = find_kth(ft, k, N)
        res[x - 1] = i
        ft.update(x, -1)
    print(' '.join(map(str, res)))
if __name__ == '__main__':
    main()
