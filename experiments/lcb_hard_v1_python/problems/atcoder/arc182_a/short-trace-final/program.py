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
