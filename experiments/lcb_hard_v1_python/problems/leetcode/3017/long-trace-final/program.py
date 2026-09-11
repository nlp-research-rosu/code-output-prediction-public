import json, sys

class Solution(object):

    def numberOfBeautifulIntegers(self, low, high, k):
        TIGHT, UNTIGHT, UNBOUND = list(range(3))

        def f(x):
            digits = list(map(int, str(x)))
            lookup = [[[[-1] * k for _ in list(range(2 * len(digits) + 1))] for _ in list(range(3))] for _ in list(range(len(digits)))]

            def memoization(i, state, diff, total):
                if i == len(digits):
                    return int(state != UNBOUND and diff == total == 0)
                if lookup[i][state][diff][total] == -1:
                    result = int(i != 0 and diff == total == 0)
                    for d in list(range(1 if i == 0 else 0, 10)):
                        new_state = state
                        if state == TIGHT and d != digits[i]:
                            new_state = UNTIGHT if d < digits[i] else UNBOUND
                        new_diff = diff + (1 if d % 2 == 0 else -1)
                        new_total = (total * 10 + d) % k
                        result += memoization(i + 1, new_state, new_diff, new_total)
                    lookup[i][state][diff][total] = result
                return lookup[i][state][diff][total]
            return memoization(0, TIGHT, 0, 0)
        return f(high) - f(low - 1)

def function(low, high, k):
    return Solution().numberOfBeautifulIntegers(low=low, high=high, k=k)

def _read_lcb_input(names):
    text = sys.stdin.read()
    decoder = json.JSONDecoder()
    values = []
    offset = 0
    while offset < len(text):
        while offset < len(text) and text[offset].isspace():
            offset += 1
        if offset == len(text):
            break
        value, offset = decoder.raw_decode(text, offset)
        values.append(value)
    if len(values) == 1:
        value = values[0]
        if isinstance(value, dict) and all(name in value for name in names):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError("input argument count does not match the solution signature")
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('low', 'high', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
