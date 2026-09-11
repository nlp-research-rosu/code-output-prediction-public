import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
lines = sys.stdin.buffer.readlines()
n, m = map(int, lines[0].split())
points = []
for line in lines[1:]:
    row, column, color = line.split()
    points.append((-int(row), 0 if color == b'B' else 1, int(column)))
maximum_black_column = 0
possible = True
for _, color, column in sorted(points):
    _lcb_count[0] += 1
    if _lcb_count[0] == 502:
        _lcb_sys.stdout.write(_lcb_json.dumps({'color': color, 'column': column, 'maximum_black_column': maximum_black_column, 'possible': possible, '_': _}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    if color == 0:
        maximum_black_column = max(maximum_black_column, column)
    elif maximum_black_column >= column:
        possible = False
        break
print('Yes' if possible else 'No')
