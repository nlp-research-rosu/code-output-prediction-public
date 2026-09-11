import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main() -> None:
    n = int(input())
    s = input()
    t = [i for i in s]
    t.sort(reverse=True)
    t = int(''.join(t))
    num = [0] * 10
    for i in s:
        num[int(i)] += 1
    ans = 0
    for i in range(int(t ** 0.5) + 10):
        p = list((n - len(str(i ** 2))) * '0' + str(i ** 2))
        check = [0] * 10
        for j in p:
            check[int(j)] += 1
        is_ok = True
        for a, b in zip(num, check):
            _lcb_count[0] += 1
            if a != b:
                is_ok = False
                break
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'b': b, 'check': check, 'i': i, 'p': p}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if is_ok:
            ans += 1
    print(ans)
if __name__ == '__main__':
    main()
