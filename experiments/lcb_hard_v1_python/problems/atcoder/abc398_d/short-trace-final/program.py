import sys

def main():
    input = sys.stdin.read().split()
    N = int(input[0])
    R = int(input[1])
    C = int(input[2])
    S = input[3]
    directions = {'N': (-1, 0), 'W': (0, -1), 'S': (1, 0), 'E': (0, 1)}
    current_r = 0
    current_c = 0
    seen = set()
    seen.add((0, 0))
    res = []
    for c in S:
        dr, dc = directions[c]
        current_r += dr
        current_c += dc
        target_r = current_r - R
        target_c = current_c - C
        if (target_r, target_c) in seen:
            res.append('1')
        else:
            res.append('0')
        seen.add((current_r, current_c))
    print(''.join(res))
if __name__ == '__main__':
    main()
