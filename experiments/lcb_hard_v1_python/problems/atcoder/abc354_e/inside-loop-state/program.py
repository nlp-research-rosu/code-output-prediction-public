import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
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
                    _lcb_count[0] += 1
                    if _lcb_count[0] == 502:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'cards': cards, 'i': i, 'j': j, 'mask': mask}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
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
