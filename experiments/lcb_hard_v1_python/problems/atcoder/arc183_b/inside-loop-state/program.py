import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
T = int(input())
for t in range(T):
    N, K = map(int, input().split())
    A = list(map(int, input().split()))
    B = list(map(int, input().split()))
    sA = set(A)
    judge = True
    if A == B:
        print('Yes')
        continue
    for b in B:
        if b not in sA:
            judge = False
            break
    if judge == False:
        print('No')
    elif K > 1:
        sB = set(B)
        if len(sB) == len(B):
            print('No')
        else:
            judge = False
            kakunin = {}
            for n in range(N):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'B': B, 'K': K, 'N': N, 'judge': judge, 'kakunin': kakunin, 'n': n}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if B[n] not in kakunin:
                    kakunin[B[n]] = [n]
                else:
                    if kakunin[B[n]][-1] >= n - K:
                        judge = True
                    kakunin[B[n]].append(n)
            if judge:
                print('Yes')
            else:
                print('No')
    else:
        ind = 0
        for b in B:
            judge = False
            while ind < N:
                if A[ind] == b:
                    judge = True
                    break
                ind += 1
            if not judge:
                break
        if not judge:
            print('No')
        else:
            print('Yes')
