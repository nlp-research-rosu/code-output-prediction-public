import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys
from functools import reduce
import collections

class Solution(object):

    def longestValidSubstring(self, word, forbidden):
        _trie = lambda: collections.defaultdict(_trie)
        trie = _trie()
        for w in forbidden:
            reduce(dict.__getitem__, w, trie)['_end']
        result = 0
        right = len(word) - 1
        for left in reversed(list(range(len(word)))):
            node = trie
            for i in list(range(left, right + 1)):
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'left': left, 'len(node)': len(node), 'result': result, 'right': right, 'word[i]': word[i]}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                if word[i] not in node:
                    break
                node = node[word[i]]
                if '_end' in node:
                    right = i - 1
                    break
            result = max(result, right - left + 1)
        return result

def function(word, forbidden):
    return Solution().longestValidSubstring(word=word, forbidden=forbidden)

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
    data = _read_lcb_input(('word', 'forbidden'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
