import sys

def remove_abc_substrings(s):
    stack = []
    for char in s:
        stack.append(char)
        if len(stack) >= 3 and stack[-3:] == ['A', 'B', 'C']:
            stack.pop()
            stack.pop()
            stack.pop()
    return ''.join(stack)

def main():
    s = sys.stdin.readline().strip()
    result = remove_abc_substrings(s)
    print(result)
if __name__ == '__main__':
    main()
