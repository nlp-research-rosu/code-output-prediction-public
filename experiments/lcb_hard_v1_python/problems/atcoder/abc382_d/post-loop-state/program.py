import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    M = int(input[1])
    result = []
    current = []

    def backtrack(index):
        if index == N:
            result.append(current.copy())
            return
        min_val = 1 if index == 0 else current[-1] + 10
        max_val = M - (N - (index + 1)) * 10
        max_val = min(max_val, M)
        for val in range(min_val, max_val + 1):
            _lcb_count[0] += 1
            if val <= M:
                current.append(val)
                backtrack(index + 1)
                current.pop()
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'M': M, 'N': N, 'current': current, 'index': index, 'len(result)': len(result), 'max_val': max_val, 'min_val': min_val, 'val': val}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    backtrack(0)
    print(len(result))
    for seq in result:
        print(' '.join(map(str, seq)))
if __name__ == '__main__':
    main()
