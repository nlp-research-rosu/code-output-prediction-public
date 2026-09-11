import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import itertools

def main():
    N, K = map(int, input().split())
    A = list(map(int, input().split()))
    max_xor = 0
    for subset in itertools.combinations(A, K):
        current_xor = 0
        for num in subset:
            _lcb_count[0] += 1
            current_xor ^= num
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'current_xor': current_xor, 'max_xor': max_xor, 'num': num, 'subset': subset}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        max_xor = max(max_xor, current_xor)
    print(max_xor)
if __name__ == '__main__':
    main()
