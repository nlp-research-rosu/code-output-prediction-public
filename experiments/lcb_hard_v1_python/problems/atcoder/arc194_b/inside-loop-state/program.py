import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

class FenwickTree:

    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 1)

    def update(self, index, delta):
        while index <= self.n:
            self.tree[index] += delta
            index += index & -index

    def query(self, index):
        res = 0
        while index > 0:
            res += self.tree[index]
            index -= index & -index
        return res

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    P = list(map(int, input[1:N + 1]))
    ft = FenwickTree(N)
    total_cost = 0
    for i in range(N):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'P': P, 'count_less_or_equal': count_less_or_equal, 'i': i, 'original_pos': original_pos, 'total_cost': total_cost, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        x = P[i]
        original_pos = i + 1
        count_less_or_equal = ft.query(x)
        k = i - count_less_or_equal
        contribution = k * (2 * original_pos - k - 1) // 2
        total_cost += contribution
        ft.update(x, 1)
    print(total_cost)
if __name__ == '__main__':
    main()
