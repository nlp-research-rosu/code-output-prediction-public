#include <atcoder/all>


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

#include <iostream>
#include <memory>

using namespace atcoder;
using namespace std;

using mint = modint998244353;
using vm = vector<mint>;
using v2m = vector<vm>;
using v3m = vector<v2m>;

#define vm(n, i) vm(n, i)
#define v2m(n, m, i) v2m(n, vm(m, i))
#define v3m(n, m, k, i) v3m(n, v2m(m, k, i))

struct state {
  shared_ptr<v3m> _xxx;
  shared_ptr<v3m> _xxy;
  shared_ptr<v3m> _xyx;
  shared_ptr<v3m> _yxx;

  state(int n) {
    this->_xxx = make_shared<v3m>(v3m(n, n, n, 0));
    this->_xxy = make_shared<v3m>(v3m(n, n, n, 0));
    this->_xyx = make_shared<v3m>(v3m(n, n, n, 0));
    this->_yxx = make_shared<v3m>(v3m(n, n, n, 0));
  }

  mint& xxx(int a, int b, int c) { return (*_xxx)[a][b][c]; }
  mint& xxy(int a, int b, int c) { return (*_xxy)[a][b][c]; }
  mint& xyx(int a, int b, int c) { return (*_xyx)[a][b][c]; }
  mint& yxx(int a, int b, int c) { return (*_yxx)[a][b][c]; }
};

int main() {
  int n, k;
  cin >> n >> k;

  string s;
  cin >> s;

  state dp(1);
  dp.xxx(0, 0, 0) = 1;
  for (int i = 1; i <= n; i++) {
    char ch = s[i - 1];
    state dp0(i + 1);

    for (int a = 0; a < i; a++) {
      for (int b = 0; b < i; b++) {
        for (int c = 0; c < i; c++) {
          if (ch == 'A' || ch == '?') {
            dp0.xxy(a + 1, b, c) += dp.xxx(a, b, c);
            dp0.xxx(a, b, c) += dp.xxy(a, b, c);
            dp0.yxx(a, b, c + 1) += dp.xyx(a, b, c);
            dp0.xyx(a, b + 1, c) += dp.yxx(a, b, c);
          }

          if (ch == 'B' || ch == '?') {
            dp0.xyx(a, b + 1, c) += dp.xxx(a, b, c);
            dp0.yxx(a, b, c + 1) += dp.xxy(a, b, c);
            dp0.xxx(a, b, c) += dp.xyx(a, b, c);
            dp0.xxy(a + 1, b, c) += dp.yxx(a, b, c);
          }

          if (ch == 'C' || ch == '?') {
            dp0.yxx(a, b, c + 1) += dp.xxx(a, b, c);
            dp0.xyx(a, b + 1, c) += dp.xxy(a, b, c);
            dp0.xxy(a + 1, b, c) += dp.xyx(a, b, c);
            dp0.xxx(a, b, c) += dp.yxx(a, b, c);
          }
        }
      }
    }
    dp = dp0;
  }

  mint ans = 0;
  for (int a = 0; a <= n; a++) {
    for (int b = 0; b <= n; b++) {
      for (int c = 0; c <= n; c++) {
++_lcb_count;

        int d = n + 1 - (a + b + c);
        int aa = a * (a - 1) / 2;
        int bb = b * (b - 1) / 2;
        int cc = c * (c - 1) / 2;
        int dd = d * (d - 1) / 2;
        if (aa + bb + cc + dd >= k) {
          ans += dp.xxx(a, b, c);
          ans += dp.xxy(a, b, c);
          ans += dp.xyx(a, b, c);
          ans += dp.yxx(a, b, c);
        }
      }
if (_lcb_count > 1000) {
std::cout << "{\"a\":";
_lcb_json(std::cout, a);
std::cout << ",\"ans.val()\":";
_lcb_json(std::cout, ans.val());
std::cout << ",\"b\":";
_lcb_json(std::cout, b);
std::cout << ",\"k\":";
_lcb_json(std::cout, k);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    }
  }
  cout << ans.val() << endl;

  return 0;
}
