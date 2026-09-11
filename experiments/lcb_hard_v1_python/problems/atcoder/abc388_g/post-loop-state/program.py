import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    A = list(map(int, data[idx:idx + N]))
    idx += N
    Q = int(data[idx])
    idx += 1
    queries = []
    for _ in range(Q):
        L = int(data[idx])
        R = int(data[idx + 1])
        queries.append((L, R))
        idx += 2
    for L, R in queries:
        m = R - L + 1
        if m < 2:
            print(0)
            continue
        B = A[L - 1:R]
        left = 0
        right = m // 2
        ans = 0
        while left <= right:
            mid = (left + right) // 2
            ok = True
            for i in range(mid):
                _lcb_count[0] += 1
                if B[i] * 2 > B[m - mid + i]:
                    ok = False
                    break
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'B': B, 'ans': ans, 'i': i, 'left': left, 'm': m, 'mid': mid, 'ok': ok, 'right': right}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if ok:
                ans = mid
                left = mid + 1
            else:
                right = mid - 1
        print(ans)
if __name__ == '__main__':
    main()
