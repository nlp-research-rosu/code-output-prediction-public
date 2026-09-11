import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from typing import List, Tuple

def avoidQueenAttack(n: int, m: int, queens: List[Tuple[int, int]]) -> int:
    R = set()
    C = set()
    D1_set = set()
    D2_set = set()
    for a_k, b_k in queens:
        R.add(a_k)
        C.add(b_k)
        D1_set.add(a_k - b_k)
        D2_set.add(a_k + b_k)
    N_R = len(R)
    N_C = len(C)
    S_size = (n - N_R) * (n - N_C)
    R_list = sorted(R)
    C_list = sorted(C)
    R_set = R
    C_set = C
    D1_count = 0
    for d in D1_set:
        length_d = n - abs(d)
        if length_d <= 0:
            continue
        positions_in_R_d = 0
        positions_in_C_d = 0
        positions_in_both_d = 0
        if d >= 0:
            i_min = 1 + d
            i_max = n
        else:
            i_min = 1
            i_max = n + d
        for i in R_list:
            if i < i_min or i > i_max:
                continue
            j = i - d
            if 1 <= j <= n:
                positions_in_R_d += 1
                if j in C_set:
                    positions_in_both_d += 1
        for j in C_list:
            i = j + d
            if i_min <= i <= i_max and 1 <= i <= n:
                positions_in_C_d += 1
        n_d = length_d - positions_in_R_d - positions_in_C_d + positions_in_both_d
        D1_count += n_d
    D2_count = 0
    for d in D2_set:
        if 2 <= d <= n + 1:
            length_d = d - 1
        elif n + 1 < d <= 2 * n:
            length_d = 2 * n - d + 1
        else:
            continue
        positions_in_R_d = 0
        positions_in_C_d = 0
        positions_in_both_d = 0
        i_min = max(1, d - n)
        i_max = min(n, d - 1)
        for i in R_list:
            if i < i_min or i > i_max:
                continue
            j = d - i
            if 1 <= j <= n:
                positions_in_R_d += 1
                if j in C_set:
                    positions_in_both_d += 1
        for j in C_list:
            i = d - j
            if i_min <= i <= i_max and 1 <= i <= n:
                positions_in_C_d += 1
        n_d = length_d - positions_in_R_d - positions_in_C_d + positions_in_both_d
        D2_count += n_d
    overlap_count = 0
    for d1 in D1_set:
        for d2 in D2_set:
            _lcb_count[0] += 1
            s_i = d1 + d2
            s_j = d2 - d1
            if s_i % 2 != 0 or s_j % 2 != 0:
                continue
            i = s_i // 2
            j = s_j // 2
            if 1 <= i <= n and 1 <= j <= n:
                if i not in R_set and j not in C_set:
                    overlap_count += 1
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'d1': d1, 'd2': d2, 'i': i, 'j': j, 'overlap_count': overlap_count, 's_i': s_i, 's_j': s_j}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    total_attacked_in_S = D1_count + D2_count - overlap_count
    answer = S_size - total_attacked_in_S
    return answer
if __name__ == '__main__':
    N, M = map(int, input().split())
    queens = [tuple(map(int, input().split())) for _ in range(M)]
    print(avoidQueenAttack(N, M, queens))
