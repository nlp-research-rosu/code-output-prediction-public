import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def canMakePalindromeQueries(self, s, queries):

        def check(left1, right1, left2, right2):

            def same(left, right):
                return all((prefixs1[right + 1][i] - prefixs1[left][i] == prefixs2[right + 1][i] - prefixs2[left][i] for i in list(range(d))))
            min_left, max_left = (min(left1, left2), max(left1, left2))
            min_right, max_right = (min(right1, right2), max(right1, right2))
            if not prefix[min_left] - prefix[0] == prefix[-1] - prefix[max_right + 1] == 0:
                return False
            if min_right < max_left:
                return prefix[max_left] - prefix[min_right + 1] == 0 and same(min_left, min_right) and same(max_left, max_right)
            if (left1 == min_left) == (right1 == max_right):
                return same(min_left, max_right)
            p1, p2 = (prefixs1, prefixs2) if min_left == left1 else (prefixs2, prefixs1)
            diff1 = [p1[min_right + 1][i] - p1[min_left][i] - (p2[max_left][i] - p2[min_left][i]) for i in list(range(d))]
            diff2 = [p2[max_right + 1][i] - p2[max_left][i] - (p1[max_right + 1][i] - p1[min_right + 1][i]) for i in list(range(d))]
            return diff1 == diff2 and all((x >= 0 for x in diff1))
        lookup = [-1] * 26
        d = 0
        for x in s:
            if lookup[ord(x) - ord('a')] != -1:
                continue
            lookup[ord(x) - ord('a')] = d
            d += 1
        prefix = [0] * (len(s) // 2 + 1)
        prefixs1 = [[0] * d for _ in list(range(len(s) // 2 + 1))]
        prefixs2 = [[0] * d for _ in list(range(len(s) // 2 + 1))]
        for i in list(range(len(s) // 2)):
            x, y = (lookup[ord(s[i]) - ord('a')], lookup[ord(s[~i]) - ord('a')])
            prefix[i + 1] = prefix[i] + int(x != y)
            for j in list(range(d)):
                _lcb_count[0] += 1
                if _lcb_count[0] > 501:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'j': j, 'prefix': prefix, 'x': x, 'y': y}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                prefixs1[i + 1][j] = prefixs1[i][j] + int(j == x)
                prefixs2[i + 1][j] = prefixs2[i][j] + int(j == y)
        return [check(q[0], q[1], len(s) - 1 - q[3], len(s) - 1 - q[2]) for q in queries]

def function(s, queries):
    return Solution().canMakePalindromeQueries(s=s, queries=queries)

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
        if isinstance(value, dict) and all((name in value for name in names)):
            return value
        if len(names) == 1:
            return {names[0]: value}
    if len(values) != len(names):
        raise ValueError('input argument count does not match the solution signature')
    return dict(zip(names, values))

def main():
    data = _read_lcb_input(('s', 'queries'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
