import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys

class Solution:

    def minimumCost(self, target, words, costs):
        children = [{}]
        failure = [0]
        outputs = [[]]
        for word, cost in zip(words, costs):
            node = 0
            for character in word:
                if character not in children[node]:
                    children[node][character] = len(children)
                    children.append({})
                    failure.append(0)
                    outputs.append([])
                node = children[node][character]
            outputs[node].append((len(word), cost))
        queue = list(children[0].values())
        cursor = 0
        while cursor < len(queue):
            node = queue[cursor]
            cursor += 1
            for character, child in children[node].items():
                fallback = failure[node]
                while fallback and character not in children[fallback]:
                    fallback = failure[fallback]
                failure[child] = children[fallback].get(character, 0)
                outputs[child].extend(outputs[failure[child]])
                queue.append(child)
        infinity = 10 ** 30
        dp = [infinity] * (len(target) + 1)
        dp[0] = 0
        node = 0
        for index, character in enumerate(target):
            while node and character not in children[node]:
                node = failure[node]
            node = children[node].get(character, 0)
            for length, cost in outputs[node]:
                _lcb_count[0] += 1
                if _lcb_count[0] == 502:
                    _lcb_sys.stdout.write(_lcb_json.dumps({'character': character, 'cost': cost, 'dp[index]': dp[index], 'index': index, 'length': length, 'node': node, 'outputs[node]': outputs[node], 'start': start, 'target': target}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                    raise SystemExit
                start = index + 1 - length
                dp[index + 1] = min(dp[index + 1], dp[start] + cost)
        return dp[-1] if dp[-1] < infinity else -1

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
    data = _read_lcb_input(('target', 'words', 'costs'))
    result = Solution().minimumCost(data['target'], data['words'], data['costs'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
