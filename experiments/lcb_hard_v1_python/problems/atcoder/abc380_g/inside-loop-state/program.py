import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import decimal
import math
import random
import sys
from bisect import bisect_left, bisect_right
from collections import Counter, defaultdict, deque
from functools import cmp_to_key, lru_cache
from heapq import heapify, heappop, heappush

class FastIO:

    @staticmethod
    def read_int():
        return int(sys.stdin.readline().rstrip())

    @staticmethod
    def read_list_ints():
        return list(map(int, sys.stdin.readline().rstrip().split()))

    @staticmethod
    def read_list_ints_minus_one():
        return [int(value) - 1 for value in sys.stdin.readline().rstrip().split()]

    @staticmethod
    def read_str():
        return sys.stdin.readline().rstrip()

    @staticmethod
    def st(value):
        print(value)

    @staticmethod
    def lst(values):
        print(*values)

    @staticmethod
    def yes():
        print('Yes')

    @staticmethod
    def no():
        print('No')

    @staticmethod
    def accumulate(values):
        prefix = [0]
        for value in values:
            prefix.append(prefix[-1] + value)
        return prefix

class SortedList:

    def __init__(self, iterable=None, _load=200):
        """Initialize sorted list instance."""
        if iterable is None:
            iterable = []
        values = sorted(iterable)
        self._len = _len = len(values)
        self._load = _load
        self._lists = _lists = [values[i:i + _load] for i in range(0, _len, _load)]
        self._list_lens = [len(_list) for _list in _lists]
        self._min_s = [_list[0] for _list in _lists]
        self._fen_tree = []
        self._rebuild = True

    def _fen_build(self):
        """Build a fenwick tree instance."""
        self._fen_tree[:] = self._list_lens
        _fen_tree = self._fen_tree
        for i in range(len(_fen_tree)):
            if i | i + 1 < len(_fen_tree):
                _fen_tree[i | i + 1] += _fen_tree[i]
        self._rebuild = False

    def _fen_update(self, index, value):
        """Update `fen_tree[index] += value`."""
        if not self._rebuild:
            _fen_tree = self._fen_tree
            while index < len(_fen_tree):
                _fen_tree[index] += value
                index |= index + 1

    def _fen_query(self, end):
        """Return `sum(_fen_tree[:end])`."""
        if self._rebuild:
            self._fen_build()
        _fen_tree = self._fen_tree
        x = 0
        while end:
            x += _fen_tree[end - 1]
            end &= end - 1
        return x

    def _fen_findkth(self, k):
        """Return a pair of (the largest `idx` such that `sum(_fen_tree[:idx]) <= k`, `k - sum(_fen_tree[:idx])`)."""
        _list_lens = self._list_lens
        if k < _list_lens[0]:
            return (0, k)
        if k >= self._len - _list_lens[-1]:
            return (len(_list_lens) - 1, k + _list_lens[-1] - self._len)
        if self._rebuild:
            self._fen_build()
        _fen_tree = self._fen_tree
        idx = -1
        for d in reversed(range(len(_fen_tree).bit_length())):
            right_idx = idx + (1 << d)
            if right_idx < len(_fen_tree) and k >= _fen_tree[right_idx]:
                idx = right_idx
                k -= _fen_tree[idx]
        return (idx + 1, k)

    def _delete(self, pos, idx):
        """Delete value at the given `(pos, idx)`."""
        _lists = self._lists
        _mins = self._min_s
        _list_lens = self._list_lens
        self._len -= 1
        self._fen_update(pos, -1)
        del _lists[pos][idx]
        _list_lens[pos] -= 1
        if _list_lens[pos]:
            _mins[pos] = _lists[pos][0]
        else:
            del _lists[pos]
            del _list_lens[pos]
            del _mins[pos]
            self._rebuild = True

    def _loc_left(self, value):
        """Return an index pair that corresponds to the first position of `value` in the sorted list."""
        if not self._len:
            return (0, 0)
        _lists = self._lists
        _mins = self._min_s
        lo, pos = (-1, len(_lists) - 1)
        while lo + 1 < pos:
            mi = lo + pos >> 1
            if value <= _mins[mi]:
                pos = mi
            else:
                lo = mi
        if pos and value <= _lists[pos - 1][-1]:
            pos -= 1
        _list = _lists[pos]
        lo, idx = (-1, len(_list))
        while lo + 1 < idx:
            mi = lo + idx >> 1
            if value <= _list[mi]:
                idx = mi
            else:
                lo = mi
        return (pos, idx)

    def _loc_right(self, value):
        """Return an index pair that corresponds to the last position of `value` in the sorted list."""
        if not self._len:
            return (0, 0)
        _lists = self._lists
        _mins = self._min_s
        pos, hi = (0, len(_lists))
        while pos + 1 < hi:
            mi = pos + hi >> 1
            if value < _mins[mi]:
                hi = mi
            else:
                pos = mi
        _list = _lists[pos]
        lo, idx = (-1, len(_list))
        while lo + 1 < idx:
            mi = lo + idx >> 1
            if value < _list[mi]:
                idx = mi
            else:
                lo = mi
        return (pos, idx)

    def add(self, value):
        """Add `value` to sorted list."""
        _load = self._load
        _lists = self._lists
        _mins = self._min_s
        _list_lens = self._list_lens
        self._len += 1
        if _lists:
            pos, idx = self._loc_right(value)
            self._fen_update(pos, 1)
            _list = _lists[pos]
            _list.insert(idx, value)
            _list_lens[pos] += 1
            _mins[pos] = _list[0]
            if _load + _load < len(_list):
                _lists.insert(pos + 1, _list[_load:])
                _list_lens.insert(pos + 1, len(_list) - _load)
                _mins.insert(pos + 1, _list[_load])
                _list_lens[pos] = _load
                del _list[_load:]
                self._rebuild = True
        else:
            _lists.append([value])
            _mins.append(value)
            _list_lens.append(1)
            self._rebuild = True

    def discard(self, value):
        """Remove `value` from sorted list if it is a member."""
        _lists = self._lists
        if _lists:
            pos, idx = self._loc_right(value)
            if idx and _lists[pos][idx - 1] == value:
                self._delete(pos, idx - 1)

    def remove(self, value):
        """Remove `value` from sorted list; `value` must be a member."""
        _len = self._len
        self.discard(value)
        if _len == self._len:
            raise ValueError('{0!r} not in list'.format(value))

    def pop(self, index=-1):
        """Remove and return value at `index` in sorted list."""
        pos, idx = self._fen_findkth(self._len + index if index < 0 else index)
        value = self._lists[pos][idx]
        self._delete(pos, idx)
        return value

    def bisect_left(self, value):
        """Return the first index to insert `value` in the sorted list."""
        pos, idx = self._loc_left(value)
        return self._fen_query(pos) + idx

    def bisect_right(self, value):
        """Return the last index to insert `value` in the sorted list."""
        pos, idx = self._loc_right(value)
        return self._fen_query(pos) + idx

    def count(self, value):
        """Return number of occurrences of `value` in the sorted list."""
        return self.bisect_right(value) - self.bisect_left(value)

    def __len__(self):
        """Return the size of the sorted list."""
        return self._len

    def __getitem__(self, index):
        """Lookup value at `index` in sorted list."""
        pos, idx = self._fen_findkth(self._len + index if index < 0 else index)
        return self._lists[pos][idx]

    def __delitem__(self, index):
        """Remove value at `index` from sorted list."""
        pos, idx = self._fen_findkth(self._len + index if index < 0 else index)
        self._delete(pos, idx)

    def __contains__(self, value):
        """Return true if `value` is an element of the sorted list."""
        _lists = self._lists
        if _lists:
            pos, idx = self._loc_left(value)
            return idx < len(_lists[pos]) and _lists[pos][idx] == value
        return False

    def __iter__(self):
        """Return an iterator over the sorted list."""
        return (value for _list in self._lists for value in _list)

    def __reversed__(self):
        """Return a reverse iterator over the sorted list."""
        return (value for _list in reversed(self._lists) for value in reversed(_list))

    def __repr__(self):
        """Return string representation of sorted list."""
        return 'SortedList({0})'.format(list(self))

class VariousSort:

    @staticmethod
    def range_merge_to_disjoint_sort_inverse_pair(nums):
        ans = 0
        n = len(nums)
        arr = [0] * n
        stack = [(0, n - 1)]
        while stack:
            left, right = stack.pop()
            if left >= 0:
                if left >= right:
                    continue
                mid = (left + right) // 2
                stack.append((~left, right))
                stack.append((left, mid))
                stack.append((mid + 1, right))
            else:
                left = ~left
                mid = (left + right) // 2
                i, j = (left, mid + 1)
                k = left
                while i <= mid and j <= right:
                    if nums[i] <= nums[j]:
                        arr[k] = nums[i]
                        i += 1
                    else:
                        arr[k] = nums[j]
                        j += 1
                        ans += mid - i + 1
                    k += 1
                while i <= mid:
                    arr[k] = nums[i]
                    i += 1
                    k += 1
                while j <= right:
                    arr[k] = nums[j]
                    j += 1
                    k += 1
                for i in range(left, right + 1):
                    nums[i] = arr[i]
        return ans

def abc_380g():
    ac = FastIO()
    mod = 998244353
    n, k = ac.read_list_ints()
    nums = ac.read_list_ints_minus_one()
    pre = []
    lst = SortedList()
    for i in range(n):
        if i >= k:
            lst.discard(nums[i - k])
        cnt = len(lst) - lst.bisect_left(nums[i])
        lst.add(nums[i])
        pre.append(cnt)
    post = []
    lst = SortedList()
    for i in range(n - 1, -1, -1):
        _lcb_count[0] += 1
        if _lcb_count[0] == 502:
            _lcb_sys.stdout.write(_lcb_json.dumps({'cnt': cnt, 'i': i, 'k': k, 'lst._lists': lst._lists, 'n': n, 'post': post, 'pre': pre}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if i + k < n:
            lst.discard(nums[i + k])
        cnt = lst.bisect_left(nums[i])
        lst.add(nums[i])
        post.append(cnt)
    post.reverse()
    reverse_pair = VariousSort().range_merge_to_disjoint_sort_inverse_pair(nums[:])
    cur = VariousSort().range_merge_to_disjoint_sort_inverse_pair(nums[:k])
    mid = k * (k - 1) * pow(4, -1, mod)
    ans = 0
    for i in range(n - k + 1):
        ans += reverse_pair - cur + mid
        ans %= mod
        cur -= post[i]
        if i + k < n:
            cur += pre[i + k]
    ans *= pow(n - k + 1, -1, mod)
    ans %= mod
    ac.st(ans)
    return
abc_380g()
