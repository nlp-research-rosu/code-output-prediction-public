import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json
import sys

class Solution:

    def minOperations(self, nums, x, k):
        values = sorted(set(nums))
        rank = {value: index + 1 for index, value in enumerate(values)}
        count_tree = [0] * (len(values) + 1)
        sum_tree = [0] * (len(values) + 1)

        def add(value, delta):
            index = rank[value]
            while index < len(count_tree):
                count_tree[index] += delta
                sum_tree[index] += delta * value
                index += index & -index

        def prefix(tree, index):
            total = 0
            while index:
                total += tree[index]
                index -= index & -index
            return total

        def kth(order):
            index = 0
            step = 1 << len(values).bit_length() - 1
            while step:
                following = index + step
                if following < len(count_tree) and count_tree[following] < order:
                    index = following
                    order -= count_tree[following]
                step >>= 1
            return index + 1
        infinity = 10 ** 30
        cost = [infinity] * (len(nums) + 1)
        for index, value in enumerate(nums):
            _lcb_count[0] += 1
            add(value, 1)
            if index >= x:
                add(nums[index - x], -1)
            if index + 1 >= x:
                median_rank = kth((x + 1) // 2)
                median = values[median_rank - 1]
                left_count = prefix(count_tree, median_rank)
                left_sum = prefix(sum_tree, median_rank)
                total_sum = prefix(sum_tree, len(values))
                cost[index + 1] = median * left_count - left_sum + total_sum - left_sum - median * (x - left_count)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'count_tree': count_tree, 'index': index, 'left_sum': left_sum, 'median': median, 'median_rank': median_rank, 'sum_tree': sum_tree, 'total_sum': total_sum, 'value': value, 'x': x}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        dp = [0] * (len(nums) + 1)
        for group in range(k):
            following = [infinity] * (len(nums) + 1)
            for end in range((group + 1) * x, len(nums) + 1):
                following[end] = min(following[end - 1], dp[end - x] + cost[end])
            dp = following
        return dp[-1]

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
    data = _read_lcb_input(('nums', 'x', 'k'))
    result = Solution().minOperations(data['nums'], data['x'], data['k'])
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
