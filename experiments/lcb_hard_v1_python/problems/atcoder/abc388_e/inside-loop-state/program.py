import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    A = list(map(int, input[1:N + 1]))

    def can_form_k(k):
        if k == 0:
            return True
        a_first = A[:k]
        a_last = A[-k:]
        j = 0
        for a in a_first:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'A': A, 'a': a, 'a_first': a_first, 'a_last': a_last, 'j': j, 'k': k}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            while j < len(a_last) and a_last[j] < 2 * a:
                j += 1
            if j >= len(a_last):
                return False
            j += 1
        return True
    low = 0
    high = N // 2
    ans = 0
    while low <= high:
        mid = (low + high) // 2
        if can_form_k(mid):
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    print(ans)
if __name__ == '__main__':
    main()
