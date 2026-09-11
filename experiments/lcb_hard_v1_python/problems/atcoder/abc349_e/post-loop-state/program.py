import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import functools

def main():
    grid = []
    for _ in range(3):
        row = list(map(int, sys.stdin.readline().split()))
        grid.append(row)

    def check_win(state, player):
        grid = [[0] * 3 for _ in range(3)]
        for i in range(3):
            for j in range(3):
                grid[i][j] = state[i * 3 + j]
        for i in range(3):
            if all((grid[i][j] == player for j in range(3))):
                return True
        for j in range(3):
            if all((grid[i][j] == player for i in range(3))):
                return True
        if all((grid[i][i] == player for i in range(3))):
            return True
        if all((grid[i][2 - i] == player for i in range(3))):
            return True
        return False

    def get_score(state):
        score_takahashi = 0
        score_aoki = 0
        for i in range(3):
            for j in range(3):
                val = state[i * 3 + j]
                if val == 1:
                    score_takahashi += grid[i][j]
                elif val == 2:
                    score_aoki += grid[i][j]
        return (score_takahashi, score_aoki)

    def get_available_moves(state):
        moves = []
        for i in range(3):
            for j in range(3):
                _lcb_count[0] += 1
                pos = i * 3 + j
                if state[pos] == 0:
                    moves.append(pos)
            if _lcb_count[0] > 1000:
                _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'moves': moves, 'pos': pos, 'state': state}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
        return moves

    @functools.lru_cache(maxsize=None)
    def game_result(state):
        if check_win(state, 1):
            return 1
        if check_win(state, 2):
            return 2
        if all((cell != 0 for cell in state)):
            score_t, score_a = get_score(state)
            if score_t > score_a:
                return 1
            else:
                return 2
        current_player = 1 if (state.count(1) + state.count(2)) % 2 == 0 else 2
        available_moves = get_available_moves(state)
        if current_player == 1:
            best = 2
            for move in available_moves:
                new_state = list(state)
                new_state[move] = 1
                res = game_result(tuple(new_state))
                if res == 1:
                    return 1
                best = min(best, res)
            return best
        else:
            best = 1
            for move in available_moves:
                new_state = list(state)
                new_state[move] = 2
                res = game_result(tuple(new_state))
                if res == 2:
                    return 2
                best = max(best, res)
            return best
    initial_state = tuple([0] * 9)
    winner = game_result(initial_state)
    print('Takahashi' if winner == 1 else 'Aoki')
if __name__ == '__main__':
    main()
