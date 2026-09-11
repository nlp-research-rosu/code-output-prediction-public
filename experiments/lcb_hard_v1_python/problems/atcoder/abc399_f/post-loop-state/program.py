import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
MOD = 998244353

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    K = int(input[1])
    A = list(map(int, input[2:2 + N]))
    max_k = K
    comb = [[0] * (max_k + 1) for _ in range(max_k + 1)]
    for j in range(max_k + 1):
        comb[j][0] = 1
        comb[j][j] = 1
        for m in range(1, j):
            comb[j][m] = comb[j - 1][m - 1] + comb[j - 1][m]
    dp_prev = [0] * (K + 1)
    total = 0
    for a in A:
        pow_a = [1] * (K + 1)
        for p in range(1, K + 1):
            pow_a[p] = pow_a[p - 1] * a % MOD
        curr_dp = [0] * (K + 1)
        for j in range(K + 1):
            temp_sum = 0
            for m in range(j + 1):
                _lcb_count[0] += 1
                c = comb[j][m]
                exponent = j - m
                term = c * pow_a[exponent] % MOD
                term = term * dp_prev[m] % MOD
                temp_sum = (temp_sum + term) % MOD
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'c': c, 'curr_dp': curr_dp, 'dp_prev': dp_prev, 'exponent': exponent, 'j': j, 'm': m, 'pow_a': pow_a, 'temp_sum': temp_sum, 'term': term}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            curr_dp[j] = (temp_sum + pow_a[j]) % MOD
        total = (total + curr_dp[K]) % MOD
        dp_prev = curr_dp.copy()
    print(total % MOD)
if __name__ == '__main__':
    main()
