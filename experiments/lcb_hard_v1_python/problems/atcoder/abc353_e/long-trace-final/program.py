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
            stack.append(child)
    print(total)
if __name__ == '__main__':
    main()
