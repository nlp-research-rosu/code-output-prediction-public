import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
'\noj（online-judge-tools）の使い方について\n\n1. テストケースをダウンロード\n2. サンプルが合っているかジャッジする\n3. 提出する\n\noj d https://atcoder.jp/contests/abc326/tasks/abc326_d\noj t -c "python3 D.py"\noj s https://atcoder.jp/contests/abc326/tasks/abc326_d D.py --guess-python-interpreter pypy\n\n※test/ が既に作成されている場合は下記コマンドで test/ を削除する\nrm -rf test/\n'
from itertools import permutations

def main() -> None:
    n = int(input())
    h = input()
    w = input()
    if n == 5:
        for i1 in range(5):
            for j1 in permutations([e for e in range(i1 + 1, n)], 2):
                for i2 in range(5):
                    for j2 in permutations([e for e in range(i2 + 1, n)], 2):
                        for i3 in range(5):
                            for j3 in permutations([e for e in range(i3 + 1, n)], 2):
                                for i4 in range(5):
                                    for j4 in permutations([e for e in range(i4 + 1, n)], 2):
                                        for i5 in range(5):
                                            for j5 in permutations([e for e in range(i5 + 1, n)], 2):
                                                grid = [['.'] * n for _ in range(n)]
                                                grid[0][i1] = h[0]
                                                if grid[0][i1] == 'A':
                                                    grid[0][j1[0]], grid[0][j1[1]] = ('B', 'C')
                                                elif grid[0][i1] == 'B':
                                                    grid[0][j1[0]], grid[0][j1[1]] = ('A', 'C')
                                                elif grid[0][i1] == 'C':
                                                    grid[0][j1[0]], grid[0][j1[1]] = ('A', 'B')
                                                grid[1][i2] = h[1]
                                                if grid[1][i2] == 'A':
                                                    grid[1][j2[0]], grid[1][j2[1]] = ('B', 'C')
                                                elif grid[1][i2] == 'B':
                                                    grid[1][j2[0]], grid[1][j2[1]] = ('A', 'C')
                                                elif grid[1][i2] == 'C':
                                                    grid[1][j2[0]], grid[1][j2[1]] = ('A', 'B')
                                                grid[2][i3] = h[2]
                                                if grid[2][i3] == 'A':
                                                    grid[2][j3[0]], grid[2][j3[1]] = ('B', 'C')
                                                elif grid[2][i3] == 'B':
                                                    grid[2][j3[0]], grid[2][j3[1]] = ('A', 'C')
                                                elif grid[2][i3] == 'C':
                                                    grid[2][j3[0]], grid[2][j3[1]] = ('A', 'B')
                                                grid[3][i4] = h[3]
                                                if grid[3][i4] == 'A':
                                                    grid[3][j4[0]], grid[3][j4[1]] = ('B', 'C')
                                                elif grid[3][i4] == 'B':
                                                    grid[3][j4[0]], grid[3][j4[1]] = ('A', 'C')
                                                elif grid[3][i4] == 'C':
                                                    grid[3][j4[0]], grid[3][j4[1]] = ('A', 'B')
                                                grid[4][i5] = h[4]
                                                if grid[4][i5] == 'A':
                                                    grid[4][j5[0]], grid[4][j5[1]] = ('B', 'C')
                                                elif grid[4][i5] == 'B':
                                                    grid[4][j5[0]], grid[4][j5[1]] = ('A', 'C')
                                                elif grid[4][i5] == 'C':
                                                    grid[4][j5[0]], grid[4][j5[1]] = ('A', 'B')
                                                is_ok = True
                                                for i in range(n):
                                                    j = 0
                                                    while j < n:
                                                        if grid[i][j] == '.':
                                                            j += 1
                                                        else:
                                                            if grid[i][j] != h[i]:
                                                                is_ok = False
                                                            break
                                                if not is_ok:
                                                    continue
                                                for j in range(n):
                                                    i = 0
                                                    while i < n:
                                                        if grid[i][j] == '.':
                                                            i += 1
                                                        else:
                                                            if grid[i][j] != w[j]:
                                                                is_ok = False
                                                            break
                                                for i in range(n):
                                                    check = [0, 0, 0]
                                                    for j in range(n):
                                                        if grid[i][j] == 'A':
                                                            check[0] += 1
                                                        if grid[i][j] == 'B':
                                                            check[1] += 1
                                                        if grid[i][j] == 'C':
                                                            check[2] += 1
                                                    if check != [1, 1, 1]:
                                                        is_ok = False
                                                if not is_ok:
                                                    continue
                                                for j in range(n):
                                                    check = [0, 0, 0]
                                                    for i in range(n):
                                                        if grid[i][j] == 'A':
                                                            check[0] += 1
                                                        if grid[i][j] == 'B':
                                                            check[1] += 1
                                                        if grid[i][j] == 'C':
                                                            check[2] += 1
                                                    if check != [1, 1, 1]:
                                                        is_ok = False
                                                if is_ok:
                                                    print('Yes')
                                                    for i in range(n):
                                                        print(*grid[i], sep='')
                                                    exit()
    if n == 4:
        for i1 in range(4):
            for j1 in permutations([e for e in range(i1 + 1, n)], 2):
                for i2 in range(4):
                    for j2 in permutations([e for e in range(i2 + 1, n)], 2):
                        for i3 in range(4):
                            for j3 in permutations([e for e in range(i3 + 1, n)], 2):
                                for i4 in range(4):
                                    for j4 in permutations([e for e in range(i4 + 1, n)], 2):
                                        grid = [['.'] * n for _ in range(n)]
                                        grid[0][i1] = h[0]
                                        if grid[0][i1] == 'A':
                                            grid[0][j1[0]], grid[0][j1[1]] = ('B', 'C')
                                        elif grid[0][i1] == 'B':
                                            grid[0][j1[0]], grid[0][j1[1]] = ('A', 'C')
                                        elif grid[0][i1] == 'C':
                                            grid[0][j1[0]], grid[0][j1[1]] = ('A', 'B')
                                        grid[1][i2] = h[1]
                                        if grid[1][i2] == 'A':
                                            grid[1][j2[0]], grid[1][j2[1]] = ('B', 'C')
                                        elif grid[1][i2] == 'B':
                                            grid[1][j2[0]], grid[1][j2[1]] = ('A', 'C')
                                        elif grid[1][i2] == 'C':
                                            grid[1][j2[0]], grid[1][j2[1]] = ('A', 'B')
                                        grid[2][i3] = h[2]
                                        if grid[2][i3] == 'A':
                                            grid[2][j3[0]], grid[2][j3[1]] = ('B', 'C')
                                        elif grid[2][i3] == 'B':
                                            grid[2][j3[0]], grid[2][j3[1]] = ('A', 'C')
                                        elif grid[2][i3] == 'C':
                                            grid[2][j3[0]], grid[2][j3[1]] = ('A', 'B')
                                        grid[3][i4] = h[3]
                                        if grid[3][i4] == 'A':
                                            grid[3][j4[0]], grid[3][j4[1]] = ('B', 'C')
                                        elif grid[3][i4] == 'B':
                                            grid[3][j4[0]], grid[3][j4[1]] = ('A', 'C')
                                        elif grid[3][i4] == 'C':
                                            grid[3][j4[0]], grid[3][j4[1]] = ('A', 'B')
                                        is_ok = True
                                        for i in range(n):
                                            j = 0
                                            while j < n:
                                                if grid[i][j] == '.':
                                                    j += 1
                                                else:
                                                    if grid[i][j] != h[i]:
                                                        is_ok = False
                                                    break
                                        if not is_ok:
                                            continue
                                        for j in range(n):
                                            i = 0
                                            while i < n:
                                                if grid[i][j] == '.':
                                                    i += 1
                                                else:
                                                    if grid[i][j] != w[j]:
                                                        is_ok = False
                                                    break
                                        for i in range(n):
                                            check = [0, 0, 0]
                                            for j in range(n):
                                                _lcb_count[0] += 1
                                                if grid[i][j] == 'A':
                                                    check[0] += 1
                                                if grid[i][j] == 'B':
                                                    check[1] += 1
                                                if grid[i][j] == 'C':
                                                    check[2] += 1
                                            if _lcb_count[0] > 1000:
                                                _lcb_sys.stdout.write(_lcb_json.dumps({'check': check, 'grid': grid, 'i': i, 'i3': i3, 'j3': j3, 'j4': j4}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                                                raise SystemExit
                                            if check != [1, 1, 1]:
                                                is_ok = False
                                        if not is_ok:
                                            continue
                                        for j in range(n):
                                            check = [0, 0, 0]
                                            for i in range(n):
                                                if grid[i][j] == 'A':
                                                    check[0] += 1
                                                if grid[i][j] == 'B':
                                                    check[1] += 1
                                                if grid[i][j] == 'C':
                                                    check[2] += 1
                                            if check != [1, 1, 1]:
                                                is_ok = False
                                        if is_ok:
                                            print('Yes')
                                            for i in range(n):
                                                print(*grid[i], sep='')
                                            exit()
    if n == 3:
        for i1 in range(3):
            for j1 in permutations([e for e in range(i1 + 1, n)], 2):
                for i2 in range(3):
                    for j2 in permutations([e for e in range(i2 + 1, n)], 2):
                        for i3 in range(3):
                            for j3 in permutations([e for e in range(i3 + 1, n)], 2):
                                grid = [['.'] * n for _ in range(n)]
                                grid[0][i1] = h[0]
                                if grid[0][i1] == 'A':
                                    grid[0][j1[0]], grid[0][j1[1]] = ('B', 'C')
                                elif grid[0][i1] == 'B':
                                    grid[0][j1[0]], grid[0][j1[1]] = ('A', 'C')
                                elif grid[0][i1] == 'C':
                                    grid[0][j1[0]], grid[0][j1[1]] = ('A', 'B')
                                grid[1][i2] = h[1]
                                if grid[1][i2] == 'A':
                                    grid[1][j2[0]], grid[1][j2[1]] = ('B', 'C')
                                elif grid[1][i2] == 'B':
                                    grid[1][j2[0]], grid[1][j2[1]] = ('A', 'C')
                                elif grid[1][i2] == 'C':
                                    grid[1][j2[0]], grid[1][j2[1]] = ('A', 'B')
                                grid[2][i3] = h[2]
                                if grid[2][i3] == 'A':
                                    grid[2][j3[0]], grid[2][j3[1]] = ('B', 'C')
                                elif grid[2][i3] == 'B':
                                    grid[2][j3[0]], grid[2][j3[1]] = ('A', 'C')
                                elif grid[2][i3] == 'C':
                                    grid[2][j3[0]], grid[2][j3[1]] = ('A', 'B')
                                is_ok = True
                                for i in range(n):
                                    j = 0
                                    while j < n:
                                        if grid[i][j] == '.':
                                            j += 1
                                        else:
                                            if grid[i][j] != h[i]:
                                                is_ok = False
                                            break
                                if not is_ok:
                                    continue
                                for j in range(n):
                                    i = 0
                                    while i < n:
                                        if grid[i][j] == '.':
                                            i += 1
                                        else:
                                            if grid[i][j] != w[j]:
                                                is_ok = False
                                            break
                                for i in range(n):
                                    check = [0, 0, 0]
                                    for j in range(n):
                                        if grid[i][j] == 'A':
                                            check[0] += 1
                                        if grid[i][j] == 'B':
                                            check[1] += 1
                                        if grid[i][j] == 'C':
                                            check[2] += 1
                                    if check != [1, 1, 1]:
                                        is_ok = False
                                if not is_ok:
                                    continue
                                for j in range(n):
                                    check = [0, 0, 0]
                                    for i in range(n):
                                        if grid[i][j] == 'A':
                                            check[0] += 1
                                        if grid[i][j] == 'B':
                                            check[1] += 1
                                        if grid[i][j] == 'C':
                                            check[2] += 1
                                    if check != [1, 1, 1]:
                                        is_ok = False
                                if is_ok:
                                    print('Yes')
                                    for i in range(n):
                                        print(*grid[i], sep='')
                                    exit()
    print('No')
if __name__ == '__main__':
    main()
