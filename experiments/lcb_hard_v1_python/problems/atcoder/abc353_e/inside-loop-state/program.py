import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
from collections import defaultdict

class TrieNode:

    def __init__(self):
        self.children = defaultdict(TrieNode)
        self.count = 0

def main():
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    strings = data[1:]
    root = TrieNode()
    for s in strings:
        node = root
        for ch in s:
            node = node.children[ch]
            node.count += 1
    total = 0
    stack = [root]
    while stack:
        node = stack.pop()
        if node.count >= 2:
            total += node.count * (node.count - 1) // 2
        for child in node.children.values():
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'child.count': child.count, 'node.count': node.count, 'total': total}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            stack.append(child)
    print(total)
if __name__ == '__main__':
    main()
