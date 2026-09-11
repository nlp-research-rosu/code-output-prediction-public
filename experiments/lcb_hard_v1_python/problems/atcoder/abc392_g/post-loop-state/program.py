import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import numpy as np

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    it = iter(data)
    n = int(next(it))
    arr = [int(next(it)) for _ in range(n)]
    max_val = max(arr)
    size = 1
    while size <= 2 * max_val:
        size <<= 1
    f = np.zeros(size, dtype=np.float64)
    for x in arr:
        f[x] = 1.0
    F = np.fft.rfft(f)
    G = F * F
    conv = np.fft.irfft(G, n=size)
    conv = np.rint(conv).astype(np.int64)
    ans = 0
    for b in arr:
        _lcb_count[0] += 1
        ans += conv[2 * b] // 2
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'arr': arr, 'b': b, 'conv[:40].tolist()': conv[:40].tolist(), 'int(ans)': int(ans), 'size': size}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    print(ans)
if __name__ == '__main__':
    solve()
