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
    if color == 0:
        maximum_black_column = max(maximum_black_column, column)
    elif maximum_black_column >= column:
        possible = False
        break
print('Yes' if possible else 'No')
