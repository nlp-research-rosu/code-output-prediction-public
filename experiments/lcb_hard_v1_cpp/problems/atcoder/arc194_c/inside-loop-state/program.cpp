#ifndef U
#pragma GCC optimize("Ofast,unroll-loops")
#endif
#include <bits/stdc++.h>


#include <algorithm>
#include <array>
#include <cstdlib>
#include <deque>
#include <iomanip>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <type_traits>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
static long long _lcb_count = 0;
static void _lcb_json_string(std::ostream& out, const std::string& value) {
    out << '"';
    for (unsigned char character : value) {
        switch (character) {
        case '"': out << "\\\""; break;
        case '\\': out << "\\\\"; break;
        case '\b': out << "\\b"; break;
        case '\f': out << "\\f"; break;
        case '\n': out << "\\n"; break;
        case '\r': out << "\\r"; break;
        case '\t': out << "\\t"; break;
        default:
            if (character < 0x20) {
                out << "\\u00" << std::hex << std::setw(2)
                    << std::setfill('0') << static_cast<int>(character)
                    << std::dec << std::setfill(' ');
            } else {
                out << static_cast<char>(character);
            }
        }
    }
    out << '"';
}
static void _lcb_json(std::ostream& out, const std::string& value) {
    _lcb_json_string(out, value);
}
static void _lcb_json(std::ostream& out, const char* value) {
    _lcb_json_string(out, value);
}
static void _lcb_json(std::ostream& out, char value) {
    _lcb_json_string(out, std::string(1, value));
}
static void _lcb_json(std::ostream& out, bool value) {
    out << (value ? "true" : "false");
}
template <class T>
static std::enable_if_t<std::is_integral_v<T> && !std::is_same_v<T, bool>>
_lcb_json(std::ostream& out, T value) {
    out << value;
}
template <class T>
static std::enable_if_t<std::is_floating_point_v<T>>
_lcb_json(std::ostream& out, T value) {
    out << std::setprecision(17) << value;
}
template <class First, class Second>
static void _lcb_json(std::ostream& out, const std::pair<First, Second>& value) {
    out << '[';
    _lcb_json(out, value.first);
    out << ',';
    _lcb_json(out, value.second);
    out << ']';
}
template <class Range>
static void _lcb_json_range(std::ostream& out, const Range& values) {
    out << '[';
    bool first = true;
    for (const auto& value : values) {
        if (!first) out << ',';
        first = false;
        _lcb_json(out, value);
    }
    out << ']';
}
template <class T, class Allocator>
static void _lcb_json(std::ostream& out, const std::vector<T, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class T, std::size_t Size>
static void _lcb_json(std::ostream& out, const std::array<T, Size>& value) {
    _lcb_json_range(out, value);
}
template <class T, class Allocator>
static void _lcb_json(std::ostream& out, const std::deque<T, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Compare, class Allocator>
static void _lcb_json(std::ostream& out, const std::set<Key, Compare, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Hash, class Equal, class Allocator>
static void _lcb_json(std::ostream& out, const std::unordered_set<Key, Hash, Equal, Allocator>& value) {
    std::vector<Key> ordered(value.begin(), value.end());
    std::sort(ordered.begin(), ordered.end());
    _lcb_json_range(out, ordered);
}
template <class Key, class Value, class Compare, class Allocator>
static void _lcb_json(std::ostream& out, const std::map<Key, Value, Compare, Allocator>& value) {
    _lcb_json_range(out, value);
}
template <class Key, class Value, class Hash, class Equal, class Allocator>
static void _lcb_json(std::ostream& out, const std::unordered_map<Key, Value, Hash, Equal, Allocator>& value) {
    std::vector<std::pair<Key, Value>> ordered(value.begin(), value.end());
    std::sort(ordered.begin(), ordered.end());
    _lcb_json_range(out, ordered);
}

using namespace std;

#define int long long
#define rep(i, a, b) for (int i = a; i < (b); ++i)
#define all(x) begin(x), end(x)
#define sz(x) (int) (x).size()
#define eb emplace_back
#define pb push_back
#define vc vector
#define fs first
#define sd second
typedef pair<int, int> pii;
typedef vc<int> vi;

int chmin(auto &u, auto v) { return u > v ? u = v, 1 : 0; }
int chmax(auto &u, auto v) { return u < v ? u = v, 1 : 0; }

signed main() {
  cin.tie(0)->sync_with_stdio(0);
  cin.exceptions(cin.failbit);

  // two sets (0->1, 1->0), also 1->0->1
  //
  // brute force quantity to do 1->0->1
  //
  // subtract from remaining, add cost of operation

  int N;
  cin >> N;

  vi A(N);
  for (auto &e : A) cin >> e;

  vi B(N);
  for (auto &e : B) cin >> e;

  vi C(N);
  for (auto &e : C) {

++_lcb_count;
if (_lcb_count == 502) {
std::cout << "{\"A\":";
_lcb_json(std::cout, A);
std::cout << ",\"B\":";
_lcb_json(std::cout, B);
std::cout << ",\"C\":";
_lcb_json(std::cout, C);
std::cout << ",\"N\":";
_lcb_json(std::cout, N);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}
cin >> e;
}

  vi order(N);
  iota(all(order), 0);
  sort(all(order), [&](int a, int b) -> bool { return C[a] > C[b]; });

  int sum1 = 0, sum2 = 0;
  rep(i, 0, N) {
    sum1 += A[i] * C[i];
    sum2 += B[i] * C[i];
  }
  vi ps1(N + 1), ps2(N + 1);
  ps1[0] = ps2[0] = 0;
  rep(i, 0, N) {
    ps1[i + 1] = ps1[i] + A[order[i]] * (1 - B[order[i]]);
    ps2[i + 1] = ps2[i] + B[order[i]] * (1 - A[order[i]]);
  }
  int cost = 0;
  rep(i, 0, N) {
    if (A[order[i]] == 1 and B[order[i]] == 0) {
      cost += sum1;
      cost -= C[order[i]] * (ps1[N] - ps1[i]);
    }
    if (B[order[i]] == 1 and A[order[i]] == 0) {
      cost += sum2;
      cost -= C[order[i]] * (ps2[N] - ps2[i + 1]);
    }
  }
  int ans = cost;
  rep(i, 0, N) {
    if (A[order[i]] == 1) {
      sum1 -= C[order[i]];
    }
    if (A[order[i]] == 1 and B[order[i]] == 1) {
      cost += sum1;
      cost -= C[order[i]] * (ps1[N] - ps1[i + 1]);
      cost += sum2;
      cost -= C[order[i]] * (ps2[N] - ps2[i + 1]);
      chmin(ans, cost);
    }
    if (B[order[i]] == 1) {
      sum2 -= C[order[i]];
    }
  }
  cout << ans << '\n';
}
