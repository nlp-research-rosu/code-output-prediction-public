import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys

def remove_abc_substrings(s):
    stack = []
    for char in s:
        _lcb_count[0] += 1
        stack.append(char)
        if len(stack) >= 3 and stack[-3:] == ['A', 'B', 'C']:
            stack.pop()
            stack.pop()
            stack.pop()
    if _lcb_count[0] > 1000:
        _lcb_sys.stdout.write(_lcb_json.dumps({'char': char, 's': s, 'stack': stack}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
        raise SystemExit
    return ''.join(stack)

def main():
    s = sys.stdin.readline().strip()
    result = remove_abc_substrings(s)
    print(result)
if __name__ == '__main__':
    main()
