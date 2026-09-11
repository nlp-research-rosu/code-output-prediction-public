#include <bits/stdc++.h>
using namespace std;
const int M = 1000000007;
const int MM = 998244353;
template <typename T, typename U>
static inline void amin(T &x, U y) {
  if (y < x) x = y;
}
template <typename T, typename U>
static inline void amax(T &x, U y) {
  if (x < y) x = y;
}
map<int, map<int, pair<int, int>>> mask;
int _runtimeTerror_() {
  int n;
  cin >> n;
  vector<long long> b(n);
  vector<int> even, odd;
  set<int> s;
  for (int i = 0; i < n; ++i) {
    cin >> b[i];
    if (!s.count(b[i])) {
      if (b[i] & 1) {
        odd.push_back(b[i]);
      } else {
        even.push_back(b[i]);
      }
    }
    s.insert(b[i]);
  }
  if ((long long)s.size() < n) {
    vector<int> ans(n, 1e8);
    ans[0] = 0;
    s.clear();
    int cur = 1;
    for (int i = 0; i < n; ++i) {
      if (s.count(b[i])) {
        continue;
      }
      ans[cur] = b[i];
      ++cur;
      s.insert(b[i]);
    }
    cout << "YES\n";
    for (int i = 0; i < n; ++i) {
      cout << ans[i] << " ";
    }
    cout << "\n";
    return 0;
  }
  if (n == 2) {
    cout << "NO\n";
    return 0;
  }
  if (n == 3) {
    int sum = b[0] + b[1] + b[2];
    if (sum % 2) {
      cout << "NO\n";
      return 0;
    }
    sum /= 2;
    cout << "YES\n";
    cout << sum - b[0] << " " << sum - b[1] << " " << sum - b[2] << "\n";
    return 0;
  }
  assert(n >= 4);
  if (even.empty()) {
    int nn = min(n, 24);
    vector<int> left, right;
    for (int i = 0; i < (nn + 1) / 2; ++i) {
      left.push_back(b[i]);
    }
    for (int i = 0; i < nn / 2; ++i) {
      right.push_back(b[nn - 1 - i]);
    }
    reverse(right.begin(), right.end());
    int tmp = (long long)right.size();
    assert((long long)left.size() + (long long)right.size() == nn);
    mask[0][0] = {0, 0};
    for (int i = 0; i < (1 << tmp); ++i) {
      for (int j = i; j; j = (j - 1) & i) {
        int val = 0, f = 0;
        for (int k = 0; k < tmp; ++k) {
          if ((i & (1 << k)) && ((j & (1 << k)) == 0)) {
            val += right[k];
            ++f;
          } else if (i & (1 << k)) {
            val -= right[k];
            --f;
          }
        }
        mask[f][val] = {i, j};
      }
    }
    tmp = (long long)left.size();
    pair<int, int> ans = {-1, -1};
    if (mask[0][0].first != 0) {
      ans = mask[0][0];
      ans.first <<= tmp;
      ans.second <<= tmp;
    }
    for (int i = 0; i < (1 << tmp); ++i) {
      if (ans.first != -1) {
        break;
      }
      for (int j = i; j; j = (j - 1) & i) {
        int val = 0, f = 0;
        for (int k = 0; k < tmp; ++k) {
          if ((i & (1 << k)) && ((j & (1 << k)) == 0)) {
            val += left[k];
            ++f;
          } else if (i & (1 << k)) {
            val -= left[k];
            --f;
          }
        }
        if (mask.count(-f) && mask[-f].count(-val)) {
          ans = mask[-f][-val];
          ans.first <<= tmp;
          ans.second <<= tmp;
          ans.first |= i;
          ans.second |= j;
          break;
        }
      }
      if (ans.first != -1) {
        break;
      }
    }
    if (ans.first == -1) {
      cout << "NO\n";
      return 0;
    }
    assert(__builtin_popcountll(ans.first) ==
           2 * __builtin_popcountll(ans.second));
    vector<int> lx, rx, tt;
    for (int i = 0; i < nn; ++i) {
      if ((ans.first & (1 << i)) && (ans.second & (1 << i))) {
        rx.push_back(b[i]);
      } else if (ans.first & (1 << i)) {
        lx.push_back(b[i]);
      } else {
        tt.push_back(b[i]);
      }
    }
    assert((long long)lx.size() == (long long)rx.size());
    cout << "YES\n";
    int cur = 0;
    for (int i = 0; i < (long long)lx.size(); ++i) {
      cout << lx[i] - cur << " ";
      cur = lx[i] - cur;
      cout << rx[i] - cur << " ";
      cur = rx[i] - cur;
    }
    for (auto &j : tt) {
      cout << j - cur << " ";
    }
    for (int i = nn; i < n; ++i) {
      cout << b[i] - cur << " ";
    }
    cout << "\n";
    return 0;
  }
  vector<int> t;
  int cnt = min(3ll, (long long)even.size());
  for (int i = 0; i < cnt; ++i) {
    t.push_back(even.back());
    even.pop_back();
  }
  if ((long long)t.size() % 2 == 0) {
    even.push_back(t.back());
    t.pop_back();
  }
  while ((long long)t.size() < 3) {
    t.push_back(odd.back());
    odd.pop_back();
  }
  int sum = accumulate(t.begin(), t.end(), 0);
  assert(sum % 2 == 0);
  cout << "YES\n";
  sum /= 2;
  cout << sum - t[0] << " " << sum - t[1] << " " << sum - t[2] << " ";
  for (int i : even) {
    cout << i - (sum - t[0]) << " ";
  }
  for (int i : odd) {
    cout << i - (sum - t[0]) << " ";
  }
  return 0;
}
int main() {
  ios_base::sync_with_stdio(0);
  cin.tie(0);
  cout.tie(0);
  int TESTS = 1;
  while (TESTS--) _runtimeTerror_();
  return 0;
}
