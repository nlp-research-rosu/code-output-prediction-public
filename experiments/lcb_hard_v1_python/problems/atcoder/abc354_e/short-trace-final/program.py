import sys
from functools import lru_cache

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    cards = []
    index = 1
    for _ in range(N):
        a = int(data[index])
        b = int(data[index + 1])
        cards.append((a, b))
        index += 2

    @lru_cache(maxsize=None)
    def dfs(mask):
        for i in range(N):
            if mask >> i & 1:
                for j in range(i + 1, N):
                    if mask >> j & 1:
                        if cards[i][0] == cards[j][0] or cards[i][1] == cards[j][1]:
                            new_mask = mask ^ (1 << i | 1 << j)
                            if not dfs(new_mask):
                                return True
        return False
    initial_mask = (1 << N) - 1
    if dfs(initial_mask):
        print('Takahashi')
    else:
        print('Aoki')
if __name__ == '__main__':
    main()
