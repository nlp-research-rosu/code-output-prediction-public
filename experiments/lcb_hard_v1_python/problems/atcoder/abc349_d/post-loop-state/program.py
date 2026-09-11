import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.readline

def main() -> None:
    L, R = map(int, input().split())
    a, b = (L, -1)
    lr = []
    while b < R:
        i, j = (0, 0)
        flag = False
        for k in reversed(range(63)):
            _lcb_count[0] += 1
            if flag:
                continue
            if a % 2 ** k == 0:
                i = k
                j = a // 2 ** i
                a = 2 ** i * j
                b = 2 ** i * (j + 1)
                if b <= R:
                    flag = True
                    lr.append((a, b))
                    a = b
                    break
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'a': a, 'b': b, 'k': k, 'lr': lr}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    print(len(lr))
    for l, r in lr:
        print(l, r)
if __name__ == '__main__':
    main()
