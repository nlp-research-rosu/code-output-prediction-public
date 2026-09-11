import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import math
MOD = 998244353

def factorize(x: int):
    d = {}
    n = x
    p = 2
    while p * p <= n:
        while n % p == 0:
            d[p] = d.get(p, 0) + 1
            n //= p
        p += 1 if p == 2 else 2
    if n > 1:
        d[n] = d.get(n, 0) + 1
    return d

def contribution_of_prime(p: int, steps):
    """
    steps : list of length N-1, d_i for this prime (0 <= d_i <= 10)
    returns C(p)  (mod MOD)
    """
    totalE = sum(steps)
    if totalE == 0:
        return 1
    powp = [1] * (totalE + 1)
    for i in range(1, totalE + 1):
        powp[i] = powp[i - 1] * p % MOD
    dp0 = [0] * (totalE + 1)
    dp1 = [0] * (totalE + 1)
    for e in range(totalE + 1):
        val = powp[e]
        if e == 0:
            dp1[e] = val
        else:
            dp0[e] = val
    for d in steps:
        ndp0 = [0] * (totalE + 1)
        ndp1 = [0] * (totalE + 1)
        if d == 0:
            for e in range(totalE + 1):
                mult = powp[e]
                if dp0[e]:
                    ndp0[e] = (ndp0[e] + dp0[e] * mult) % MOD
                if dp1[e]:
                    ndp1[e] = (ndp1[e] + dp1[e] * mult) % MOD
            dp0, dp1 = (ndp0, ndp1)
            continue
        for e in range(totalE + 1):
            _lcb_count[0] += 1
            cur0 = dp0[e]
            cur1 = dp1[e]
            if cur0 == 0 and cur1 == 0:
                continue
            e_add = e + d
            if e_add <= totalE:
                mult = powp[e_add]
                if cur0:
                    ndp0[e_add] = (ndp0[e_add] + cur0 * mult) % MOD
                if cur1:
                    ndp1[e_add] = (ndp1[e_add] + cur1 * mult) % MOD
            if e >= d:
                e_sub = e - d
                mult = powp[e_sub]
                if cur0:
                    if e_sub == 0:
                        ndp1[e_sub] = (ndp1[e_sub] + cur0 * mult) % MOD
                    else:
                        ndp0[e_sub] = (ndp0[e_sub] + cur0 * mult) % MOD
                if cur1:
                    ndp1[e_sub] = (ndp1[e_sub] + cur1 * mult) % MOD
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'d': d, 'dp0': dp0, 'dp1': dp1, 'e': e, 'ndp0': ndp0, 'ndp1': ndp1, 'p': p, 'powp': powp, 'steps': steps, 'totalE': totalE}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        dp0, dp1 = (ndp0, ndp1)
    return sum(dp1) % MOD

def solve() -> None:
    it = iter(sys.stdin.read().strip().split())
    N = int(next(it))
    A = [int(next(it)) for _ in range(N - 1)]
    prime_steps = {}
    for idx, val in enumerate(A):
        fac = factorize(val)
        for p, e in fac.items():
            if p not in prime_steps:
                prime_steps[p] = [0] * (N - 1)
            prime_steps[p][idx] = e
    ans = 1
    for p, steps in prime_steps.items():
        ans = ans * contribution_of_prime(p, steps) % MOD
    print(ans)
if __name__ == '__main__':
    solve()
