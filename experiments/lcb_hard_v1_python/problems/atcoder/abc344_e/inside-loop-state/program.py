import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
input = sys.stdin.read

def main():
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    A = list(map(int, data[idx:idx + N]))
    idx += N
    Q = int(data[idx])
    idx += 1
    prev = {}
    next = {}
    for num in A:
        prev[num] = None
        next[num] = None
    head = A[0]
    for i in range(N - 1):
        prev[A[i + 1]] = A[i]
        next[A[i]] = A[i + 1]
    for _ in range(Q):
        query_type = data[idx]
        idx += 1
        if query_type == '1':
            x = int(data[idx])
            idx += 1
            y = int(data[idx])
            idx += 1
            nxt = next[x]
            next[x] = y
            prev[y] = x
            next[y] = nxt
            if nxt is not None:
                prev[nxt] = y
        elif query_type == '2':
            x = int(data[idx])
            idx += 1
            prev_x = prev[x]
            nxt_x = next[x]
            if prev_x is not None:
                next[prev_x] = nxt_x
            if nxt_x is not None:
                prev[nxt_x] = prev_x
            if head == x:
                head = nxt_x
    result = []
    current = head
    while current is not None:
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'current': current, 'head': head, 'num': num, 'result': result}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        result.append(str(current))
        current = next[current]
    print(' '.join(result))
if __name__ == '__main__':
    main()
