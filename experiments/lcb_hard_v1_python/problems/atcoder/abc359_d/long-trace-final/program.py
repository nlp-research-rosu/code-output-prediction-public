import sys
import itertools
from collections import deque
MOD = 998244353

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    K = int(data[1])
    S = data[2]
    dp = [{} for _ in range(N + 1)]
    dp[0][tuple()] = 1
    for i in range(N):
        current_char = S[i]
        current_states = dp[i]
        next_states = dp[i + 1]
        for state in current_states:
            count = current_states[state]
            possible_chars = []
            if current_char == 'A':
                possible_chars = ['A']
            elif current_char == 'B':
                possible_chars = ['B']
            else:
                possible_chars = ['A', 'B']
            for ch in possible_chars:
                new_state = list(state)
                new_state.append(ch)
                if len(new_state) > K - 1:
                    new_state.pop(0)
                new_state = tuple(new_state)
                if len(state) == K - 1:
                    new_substring = list(state) + [ch]
                    is_palindrome = True
                    for j in range(K):
                        if new_substring[j] != new_substring[K - 1 - j]:
                            is_palindrome = False
                            break
                    if is_palindrome:
                        continue
                next_states[new_state] = (next_states.get(new_state, 0) + count) % MOD
    total = sum(dp[N].values()) % MOD
    print(total)
if __name__ == '__main__':
    main()
