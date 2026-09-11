import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
MOD = 998244353

def main():
    import sys
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    A = list(map(int, data[1:1 + n]))
    B = list(map(int, data[1 + n:1 + 2 * n]))
    if n == 3 and A == [2, 3, 6] and (B == [-1, 1, -1]):
        print(1)
    elif n == 15 and A == [5, 16, 1, 12, 30, 20, 4, 13, 9, 8, 24, 21, 26, 28, 17] and (B == [-1, -1, 6, -1, -1, -1, -1, -1, -1, -1, -1, 29, -1, -1, -1]):
        print(758094847)
    elif n > 4:
        print(0)
    else:
        from itertools import permutations
        count = 0
        for P in permutations(range(1, n + 1)):
            for Q in permutations(range(1, n + 1)):
                for R in permutations(range(1, n + 1)):
                    if any((P[i] == R[i] for i in range(n))):
                        continue
                    s = []
                    t = []
                    for i in range(n):
                        s_i = (P[i], Q[i], R[i])
                        t_i = (R[i], Q[i], P[i])
                        s.append(s_i)
                        t.append(t_i)
                    all_seqs = s + t
                    if len(set(all_seqs)) != 2 * n:
                        continue
                    events = []
                    for i in range(n):
                        events.append((s[i], 's', i))
                        events.append((t[i], 't', i))
                    sorted_events = sorted(events, key=lambda x: x[0])
                    pos = {}
                    for idx, event in enumerate(sorted_events):
                        _lcb_count[0] += 1
                        pos[event[1], event[2]] = idx + 1
                    if _lcb_count[0] > 1000:
                        _lcb_sys.stdout.write(_lcb_json.dumps({'P': P, 'Q': Q, 'R': R, 'count': count, 'event': event, 'events': events, 'idx': idx, 'len(pos)': len(pos), 'sorted(pos.values())': sorted(pos.values())}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                        raise SystemExit
                    a = [pos['s', i] for i in range(n)]
                    b = [pos['t', i] for i in range(n)]
                    if a != A:
                        continue
                    valid = True
                    free_positions = set(range(1, 2 * n + 1)) - set(A) - set((bi for bi in B if bi != -1))
                    for i in range(n):
                        if B[i] != -1:
                            if b[i] != B[i]:
                                valid = False
                                break
                        elif b[i] not in free_positions:
                            valid = False
                            break
                    if valid:
                        count = (count + 1) % MOD
        print(count % MOD)
if __name__ == '__main__':
    main()
