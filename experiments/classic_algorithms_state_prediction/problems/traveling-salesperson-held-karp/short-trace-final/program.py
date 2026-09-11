import itertools


def main():
    n = int(input())
    distances = [list(map(int, input().split())) for _ in range(n)]
    dp = {(1, 0): 0}
    for subset_size in range(1, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            mask = 1
            for city in subset:
                mask |= 1 << city
            for last in subset:
                previous_mask = mask ^ (1 << last)
                best = 10**30
                for previous in range(n):
                    if previous == last:
                        continue
                    state = (previous_mask, previous)
                    if state in dp:
                        candidate = dp[state] + distances[previous][last]
                        if candidate < best:
                            best = candidate
                dp[(mask, last)] = best
    full_mask = (1 << n) - 1
    answer = min(dp[(full_mask, last)] + distances[last][0] for last in range(1, n))
    print(answer)


if __name__ == "__main__":
    main()
