import sys

def main():
    import sys
    input = sys.stdin.read().split()
    N = int(input[0])
    A = list(map(int, input[1:N + 1]))

    def can_form_k(k):
        if k == 0:
            return True
        a_first = A[:k]
        a_last = A[-k:]
        j = 0
        for a in a_first:
            while j < len(a_last) and a_last[j] < 2 * a:
                j += 1
            if j >= len(a_last):
                return False
            j += 1
        return True
    low = 0
    high = N // 2
    ans = 0
    while low <= high:
        mid = (low + high) // 2
        if can_form_k(mid):
            ans = mid
            low = mid + 1
        else:
            high = mid - 1
    print(ans)
if __name__ == '__main__':
    main()
