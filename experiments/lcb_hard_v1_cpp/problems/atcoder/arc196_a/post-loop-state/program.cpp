#include<iostream>


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

#include<algorithm>
#include<set>
using namespace std;

int n, a[300005], b[300005];
multiset<int> ms[4];
long long ans;

int main() {
	scanf("%d", &n);
	for (int i = 0; i < n; i++) {
		scanf("%d", &a[i]);
		b[i] = a[i];
	}
	
	if (n % 2 == 0) {
		sort(b, b + n);
		for (int i = 0; i < n / 2; i++) {
			ans -= b[i];
		}
		for (int i = n / 2; i < n; i++) {
			ans += b[i];
		}
	} else {
		long long pl = 0;
		long long mi = 0;
		sort(b + 1, b + n);
		for (int i = 1; i < (n + 1) / 2; i++) {
			mi += b[i];
			ms[2].insert(b[i]);
		}
		for (int i = (n + 1) / 2; i < n; i++) {
			pl += b[i];
			ms[3].insert(b[i]);
		}
		ans = pl - mi;

		for (int i = 0; i + 2 < n; i += 2) {
++_lcb_count;

			ms[0].insert(a[i]);
			ms[0].insert(a[i + 1]);
			mi += a[i] + a[i + 1];
			
			{
				auto x = ms[0].end();
				x--;
				int y = *x;
				mi -= y;
				pl += y;
				ms[1].insert(y);
				ms[0].erase(x);
			}
			
			{
				auto u = ms[0].end();
				u--;
				auto v = ms[1].begin();
				int x = *u;
				int y = *v;
				if (x > y) {
					ms[0].erase(u);
					ms[1].erase(v);
					ms[0].insert(y);
					ms[1].insert(x);
					mi += y - x;
					pl += x - y;
				}
			}
			
			if (ms[2].find(a[i + 1]) != ms[2].end()) {
				ms[2].erase(ms[2].lower_bound(a[i + 1]));
				mi -= a[i + 1];
			} else {
				ms[3].erase(ms[3].lower_bound(a[i + 1]));
				pl -= a[i + 1];
			}
			
			if (ms[2].find(a[i + 2]) != ms[2].end()) {
				ms[2].erase(ms[2].find(a[i + 2]));
				mi -= a[i + 2];
			} else {
				ms[3].erase(ms[3].find(a[i + 2]));
				pl -= a[i + 2];
			}
			
			if (ms[2].size() < ms[3].size()) {
				auto x = ms[3].begin();
				mi += *x;
				pl -= *x;
				ms[2].insert(*x);
				ms[3].erase(x);
			} else if (ms[2].size() > ms[3].size()) {
				auto x = ms[2].end();
				x--;
				mi -= *x;
				pl += *x;
				ms[3].insert(*x);
				ms[2].erase(x);
			}

			ans = max(ans, pl - mi);
		}
if (_lcb_count > 1000) {
std::cout << "{\"ans\":";
_lcb_json(std::cout, ans);
std::cout << ",\"mi\":";
_lcb_json(std::cout, mi);
std::cout << ",\"ms[0].size()\":";
_lcb_json(std::cout, ms[0].size());
std::cout << ",\"ms[1].size()\":";
_lcb_json(std::cout, ms[1].size());
std::cout << ",\"ms[2].size()\":";
_lcb_json(std::cout, ms[2].size());
std::cout << ",\"ms[3].size()\":";
_lcb_json(std::cout, ms[3].size());
std::cout << ",\"pl\":";
_lcb_json(std::cout, pl);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

	}
	
	printf("%lld\n", ans);
	
	return 0;
}
