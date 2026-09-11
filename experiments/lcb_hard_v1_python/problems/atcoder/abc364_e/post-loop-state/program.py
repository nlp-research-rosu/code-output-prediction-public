import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
data = list(map(int, sys.stdin.buffer.read().split()))
n, sweetness_limit, saltiness_limit = data[:3]
dishes = [(data[index], data[index + 1]) for index in range(3, len(data), 2)]
if sweetness_limit > saltiness_limit:
    sweetness_limit, saltiness_limit = (saltiness_limit, sweetness_limit)
    dishes = [(saltiness, sweetness) for sweetness, saltiness in dishes]
infinity = saltiness_limit + 1
minimum_salt = [[infinity] * (sweetness_limit + 1) for _ in range(n + 1)]
minimum_salt[0][0] = 0
largest = 0
for processed, (sweetness, saltiness) in enumerate(dishes):
    for count in range(processed, -1, -1):
        previous = minimum_salt[count]
        following = minimum_salt[count + 1]
        for total_sweetness in range(sweetness_limit - sweetness + 1):
            _lcb_count[0] += 1
            total_saltiness = previous[total_sweetness] + saltiness
            if total_saltiness < following[total_sweetness + sweetness]:
                following[total_sweetness + sweetness] = total_saltiness
                if total_saltiness <= saltiness_limit:
                    largest = max(largest, count + 1)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'count': count, 'following': following, 'largest': largest, 'previous': previous, 'processed': processed, 'total_saltiness': total_saltiness, 'total_sweetness': total_sweetness}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
print(min(n, largest + 1))
