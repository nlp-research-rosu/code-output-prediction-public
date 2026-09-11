import sys
from functools import lru_cache

def solve():
    N = int(sys.stdin.readline())
    A = sys.stdin.readline().strip()
    current = list(A)
    for _ in range(N):
        new_current = []
        length = len(current)
        for i in range(0, length, 3):
            group = current[i:i + 3]
            count_0 = group.count('0')
            count_1 = group.count('1')
            if count_0 > count_1:
                new_current.append('0')
            else:
                new_current.append('1')
        current = new_current
    original_result = current[0]

    @lru_cache(maxsize=None)
    def min_changes(start, level, target):
        if level == 0:
            return 0 if A[start] == str(target) else 1
        else:
            len_group = 3 ** level
            third = len_group // 3
            costT1 = min_changes(start, level - 1, target)
            costNT1 = min_changes(start, level - 1, 1 - target)
            costT2 = min_changes(start + third, level - 1, target)
            costNT2 = min_changes(start + third, level - 1, 1 - target)
            costT3 = min_changes(start + 2 * third, level - 1, target)
            costNT3 = min_changes(start + 2 * third, level - 1, 1 - target)
            case1_1 = costT1 + costT2 + costNT3
            case1_2 = costT1 + costT3 + costNT2
            case1_3 = costT2 + costT3 + costNT1
            case1 = min(case1_1, case1_2, case1_3)
            case2 = costT1 + costT2 + costT3
            return min(case1, case2)
    if original_result == '0':
        answer = min_changes(0, N, 1)
    else:
        answer = min_changes(0, N, 0)
    print(answer)
if __name__ == '__main__':
    solve()
