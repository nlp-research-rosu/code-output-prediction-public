import sys

def main():
    input = sys.stdin.read().split()
    idx = 0
    N = int(input[idx])
    idx += 1
    X = int(input[idx])
    idx += 1
    U = []
    D = []
    for _ in range(N):
        u = int(input[idx])
        idx += 1
        d = int(input[idx])
        idx += 1
        U.append(u)
        D.append(d)
    h_max = min((u + d for u, d in zip(U, D)))
    sum_total = sum((u + d for u, d in zip(U, D)))
    low = 0
    high = h_max
    best_H = 0

    def is_possible(H):
        current_L = max(0, H - D[0])
        current_R = min(U[0], H)
        if current_L > current_R:
            return False
        low_prev = current_L
        high_prev = current_R
        for i in range(1, N):
            current_L_i = max(0, H - D[i])
            current_R_i = min(U[i], H)
            new_low = max(current_L_i, low_prev - X)
            new_high = min(current_R_i, high_prev + X)
            if new_low > new_high:
                return False
            low_prev = new_low
            high_prev = new_high
        return True
    while low <= high:
        mid = (low + high) // 2
        if is_possible(mid):
            best_H = mid
            low = mid + 1
        else:
            high = mid - 1
    ans = sum_total - N * best_H
    print(ans)
if __name__ == '__main__':
    main()
