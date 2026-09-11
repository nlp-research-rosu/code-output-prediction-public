import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    T = data[1]
    strings = data[2:2 + N]
    len_T = len(T)
    pre = []
    suf = []
    for s in strings:
        p = 0
        for ch in s:
            if p < len_T and ch == T[p]:
                p += 1
        pre.append(p)
        q = 0
        for ch in reversed(s):
            if q < len_T and ch == T[len_T - 1 - q]:
                q += 1
        suf.append(q)
    from collections import defaultdict
    pre_freq = defaultdict(int)
    suf_freq = defaultdict(int)
    for p in pre:
        pre_freq[p] += 1
    for s in suf:
        suf_freq[s] += 1
    count = 0
    for p in pre_freq:
        for s in suf_freq:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'count': count, 'p': p, 'pre_freq': pre_freq, 's': s, 'suf_freq': suf_freq}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if p + s >= len_T:
                count += pre_freq[p] * suf_freq[s]
    print(count)
if __name__ == '__main__':
    main()
