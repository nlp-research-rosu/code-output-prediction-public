import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
n, q = map(int, input().split())
p = []
v = []
for _ in range(q):
    a, b = map(int, input().split())
    p.append(a)
    v.append(b)
MOD = 998244353
ans_list = [2] * q
ops = [0] * q
for i in range(q - 1):
    for j in range(i + 1, q):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'ans_list': ans_list, 'i': i, 'j': j, 'ops': ops, 'p': p, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if v[i] <= v[j]:
            continue
        elif p[i] == p[j]:
            print(0)
            exit()
        elif p[i] < p[j]:
            if ops[i] != 1 and ops[j] != -1:
                ops[i] = -1
                ops[j] = 1
                ans_list[i] = 1
                ans_list[j] = 1
            else:
                print(0)
                exit()
        elif ops[i] != -1 and ops[j] != 1:
            ops[i] = 1
            ops[j] = -1
            ans_list[i] = 1
            ans_list[j] = 1
        else:
            print(0)
            exit()
ans = 1
for x in ans_list:
    ans *= x
    ans %= MOD
print(ans)
