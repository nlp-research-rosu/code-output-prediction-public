import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import math
import sys

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    M = int(input[1])
    P = list(map(int, input[2:2 + N]))
    P.sort()
    sum_inv = sum((1.0 / p for p in P))

    def is_possible(S):
        if S == 0:
            return True
        x_list = [S * (1.0 / p) / sum_inv for p in P]
        k_list = [int(math.floor(xi)) for xi in x_list]
        T = sum(k_list)
        R = S - T
        additional_costs = []
        for i in range(N):
            ki = k_list[i]
            additional = (2 * ki + 1) * P[i]
            additional_costs.append(additional)
        additional_costs.sort()
        sum_additional = sum(additional_costs[:R])
        sum_k2p = 0
        for ki, p in zip(k_list, P):
            _lcb_count[0] += 1
            sum_k2p += ki * ki * p
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'P': P, 'S': S, 'k_list': k_list, 'ki': ki, 'p': p, 'sum_k2p': sum_k2p}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        total_cost = sum_k2p + sum_additional
        return total_cost <= M
    low = 0
    high = 10 ** 18
    answer = 0
    while low <= high:
        mid = (low + high) // 2
        if is_possible(mid):
            answer = mid
            low = mid + 1
        else:
            high = mid - 1
    print(answer)
if __name__ == '__main__':
    main()
