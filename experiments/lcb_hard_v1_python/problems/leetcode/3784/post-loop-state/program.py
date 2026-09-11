import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class Solution(object):

    def longestCommonPrefix(self, words, k):
        idxs = list(range(len(words)))
        idxs.sort(key=lambda x: words[x])

        def longest_common_prefix(k):
            lcp = [0] * len(words)
            for i in list(range(len(words) - (k - 1))):
                left = words[idxs[i]]
                right = words[idxs[i + (k - 1)]]
                l = min(len(left), len(right))
                lcp[i] = next((j for j in list(range(l)) if left[j] != right[j]), l)
            return lcp
        lcp = longest_common_prefix(k)
        prefix = [0] * len(words)
        prefix[0] = lcp[0]
        for i in list(range(len(prefix) - 1)):
            prefix[i + 1] = max(prefix[i], lcp[i + 1])
        suffix = [0] * len(words)
        suffix[-1] = lcp[-1]
        for i in reversed(list(range(len(suffix) - 1))):
            suffix[i] = max(suffix[i + 1], lcp[i])
        result = [0] * len(words)
        mx = max(longest_common_prefix(k + 1))
        for i in list(range(len(words))):
            _lcb_count[0] += 1
            idx = idxs[i]
            mx1 = prefix[i - k] if i - k >= 0 else 0
            mx2 = suffix[i + 1] if i + 1 < len(words) else 0
            result[idx] = max(mx, mx1, mx2)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'i': i, 'idx': idx, 'mx': mx, 'mx1': mx1, 'mx2': mx2, 'prefix': prefix, 'result': result, 'suffix': suffix}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        return result

def function(words, k):
    return Solution().longestCommonPrefix(words=words, k=k)

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
    data = _read_lcb_input(('words', 'k'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
