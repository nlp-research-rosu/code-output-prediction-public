#include<bits/stdc++.h>


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


#define nl '\n'
#define ll long long
#define all(x) (x).begin(), (x).end()
#define rall(x) (x).rbegin(), (x).rend()
#define pb push_back
#define eb emplace_back
#define fi first
#define sc second

#define pii pair<int, int>
#define pll pair<ll, ll>
template<typename T> bool chkmin(T &a, T b){return (b < a) ? a = b, 1 : 0;}
template<typename T> bool chkmax(T &a, T b){return (b > a) ? a = b, 1 : 0;}
using namespace std;
using ld = long double;
const int N = 1e6 + 100;
const ll inf = 1e18;
const ll mod = 998244353;

void Add(ll &x, ll y) {
    x = (x + y) % mod;
}

void solve() {
    int n;
    cin >> n;
    vector<pii> vals(n);
    for (int i = 0; i < n; i++) {
        cin >> vals[i].fi >> vals[i].sc;
    }
    sort(all(vals));
    vector<ll> dp(n + 5, 0);
    vector<int> a(n + 2);
    a[0] = n + 1;
    a[n + 1] = 0;
    for (int i = 1; i <= n; i++) {
        a[i] = vals[i - 1].sc;
    }
    dp[0] = 1;
    // for (int i = 0; i <= n + 1; i++) cerr << a[i] << ' ' ; cerr << nl;
    auto valid = [&](int l, int r, int dw, int up) -> bool {
        if (l > r) return 1;
        vector<int> maybe;
        for (int i = l; i <= r; i++) {
            if (a[i] > dw && a[i] < up) {
                maybe.pb(a[i]);
            }
        }
        vector<int> ok(maybe.size(), 0);
        int mn = n + 1;
        for (int i = 0; i < maybe.size(); i++) {
            int nw = maybe[i];
            if (mn < nw) {
                ok[i] = 1;
            } else {
                mn = nw;
            }
        }
        int mx = -1;
        for (int i = maybe.size() - 1; i >= 0; i--) {
            int nw = maybe[i];
            if (mx > nw) {
                ok[i] = 1;
            } else {
                mx = nw;
            }
        }
        // if (ok.size()) cerr << "???" << l << ' ' << r << ' ' << dw << ' ' << up << ' ' << ok[0] << nl;
        return accumulate(all(ok), 0) == maybe.size();
    };
    for (int i = 1; i <= n + 1; i++) {
        for (int j = 0; j < i; j++) {
++_lcb_count;

            if (a[i] < a[j] && valid(j + 1, i - 1, a[i], a[j])) {
                Add(dp[i], dp[j]);
                // cerr << "!!" << j << "->" << i << nl;
            }
        }
if (_lcb_count > 1000) {
std::cout << "{\"a\":";
_lcb_json(std::cout, a);
std::cout << ",\"dp\":";
_lcb_json(std::cout, dp);
std::cout << ",\"i\":";
_lcb_json(std::cout, i);
std::cout << ",\"n\":";
_lcb_json(std::cout, n);
std::cout << ",\"vals\":";
_lcb_json(std::cout, vals);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

        // cerr << "dp" << i << '=' << dp[i] << nl;
    }
    cout << dp[n + 1] << nl;
}

signed main() {
    ios::sync_with_stdio(0);
    cin.tie(0);
    // int tt = 1;
    // cin >> tt;
    // while(tt--)
        solve();
    return 0;
}
