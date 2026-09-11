import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import json, sys

class SortedList:
    BUCKET_RATIO = 50
    REBUILD_RATIO = 170

    def __init__(self, values=()):
        self._build(sorted(values))

    def _build(self, values=None):
        if values is None:
            values = list(self)
        self.size = len(values)
        bucket_count = int((self.size / self.BUCKET_RATIO) ** 0.5) + 1
        self.buckets = [values[self.size * i // bucket_count:self.size * (i + 1) // bucket_count] for i in list(range(bucket_count))]

    def __iter__(self):
        for bucket in self.buckets:
            yield from bucket

    def __len__(self):
        return self.size

    def __getitem__(self, index):
        if index < 0:
            index += self.size
        for bucket in self.buckets:
            if index < len(bucket):
                return bucket[index]
            index -= len(bucket)
        raise IndexError

    def _bucket(self, value):
        for bucket in self.buckets:
            if not bucket or value <= bucket[-1]:
                return bucket
        return self.buckets[-1]

    def add(self, value):
        import bisect
        bucket = self._bucket(value)
        bisect.insort(bucket, value)
        self.size += 1
        if len(bucket) > len(self.buckets) * self.REBUILD_RATIO:
            self._build()

    def index(self, value):
        import bisect
        result = 0
        for bucket in self.buckets:
            if bucket and bucket[-1] >= value:
                return result + bisect.bisect_left(bucket, value)
            result += len(bucket)
        return result
    bisect_left = index

    def pop(self, index=-1):
        if index < 0:
            index += self.size
        for bucket in self.buckets:
            if index < len(bucket):
                value = bucket.pop(index)
                self.size -= 1
                if not bucket:
                    self._build()
                return value
            index -= len(bucket)
        raise IndexError

class Solution(object):

    def numberOfAlternatingGroups(self, colors, queries):

        class BIT(object):

            def __init__(self, n):
                self.__bit = [0] * (n + 1)

            def add(self, i, val):
                i += 1
                while i < len(self.__bit):
                    self.__bit[i] += val
                    i += i & -i

            def query(self, i):
                i += 1
                ret = 0
                while i > 0:
                    ret += self.__bit[i]
                    i -= i & -i
                return ret

        def update(i, d):
            if d == +1:
                sl.add(i)
                if len(sl) == 1:
                    bit1.add(n, +1)
                    bit2.add(n, +n)
            curr = sl.index(i)
            prv, nxt = ((curr - 1) % len(sl), (curr + 1) % len(sl))
            if len(sl) != 1:
                l = (sl[nxt] - sl[prv] - 1) % n + 1
                bit1.add(l, d * -1)
                bit2.add(l, d * -l)
                l = (sl[curr] - sl[prv]) % n
                bit1.add(l, d * +1)
                bit2.add(l, d * +l)
                l = (sl[nxt] - sl[curr]) % n
                bit1.add(l, d * +1)
                bit2.add(l, d * +l)
            if d == -1:
                if len(sl) == 1:
                    bit1.add(n, -1)
                    bit2.add(n, -n)
                sl.pop(curr)
        n = len(colors)
        sl = SortedList()
        bit1, bit2 = (BIT(n + 1), BIT(n + 1))
        for i in list(range(n)):
            if colors[i] == colors[(i + 1) % n]:
                update(i, +1)
        result = []
        for q in queries:
            _lcb_count[0] += 1
            if _lcb_count[0] == 502:
                _lcb_sys.stdout.write(_lcb_json.dumps({'bit1._BIT__bit': bit1._BIT__bit, 'bit2._BIT__bit': bit2._BIT__bit, 'colors': colors, 'len(result)': len(result), 'len(sl)': len(sl), 'q': q}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
                raise SystemExit
            if q[0] == 1:
                l = q[1]
                result.append(bit2.query(n) - bit2.query(l - 1) - (l - 1) * (bit1.query(n) - bit1.query(l - 1)) if sl else n)
                continue
            _, i, c = q
            if colors[i] == c:
                continue
            colors[i] = c
            update((i - 1) % n, +1 if colors[i] == colors[(i - 1) % n] else -1)
            update(i, +1 if colors[i] == colors[(i + 1) % n] else -1)
        return result

def function(colors, queries):
    return Solution().numberOfAlternatingGroups(colors=colors, queries=queries)

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
    data = _read_lcb_input(('colors', 'queries'))
    result = function(**data)
    sys.stdout.write(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
if __name__ == '__main__':
    main()
