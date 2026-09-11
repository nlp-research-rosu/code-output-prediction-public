import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def main():
    import sys
    input = sys.stdin.read().split()
    idx = 0
    N = int(input[idx])
    idx += 1
    X = int(input[idx])
    idx += 1
    Y = int(input[idx])
    idx += 1
    S = input[idx]
    idx += 1
    T = input[idx]
    idx += 1

    def get_runs(s):
        runs = []
        n = len(s)
        if n == 0:
            return runs
        current = s[0]
        count = 1
        for c in s[1:]:
            if c == current:
                count += 1
            else:
                runs.append((current, count))
                current = c
                count = 1
        runs.append((current, count))
        return runs
    runs_S = get_runs(S)
    runs_T = get_runs(T)
    if len(runs_S) != len(runs_T):
        print('No')
        return
    for i in range(len(runs_S)):
        _lcb_count[0] += 1
        if runs_S[i][0] != runs_T[i][0]:
            print('No')
            return
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'N': N, 'X': X, 'Y': Y, 'i': i, 'len(runs_S)': len(runs_S), 'len(runs_T)': len(runs_T), 'runs_S[i]': runs_S[i], 'runs_T[i]': runs_T[i]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    count_0_S = sum((run[1] for run in runs_S if run[0] == '0'))
    count_0_T = sum((run[1] for run in runs_T if run[0] == '0'))
    if count_0_S != count_0_T:
        print('No')
        return
    count_1_S = sum((run[1] for run in runs_S if run[0] == '1'))
    count_1_T = sum((run[1] for run in runs_T if run[0] == '1'))
    if Y != X:
        if (count_1_T - count_1_S) % (Y - X) != 0:
            print('No')
            return
    elif count_1_T != count_1_S:
        print('No')
        return
    print('Yes')
if __name__ == '__main__':
    main()
