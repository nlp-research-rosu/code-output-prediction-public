#include <algorithm>


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

#include <bit>
#include <iostream>
#include <limits>
#include <vector>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int vertexCount, edgeCount;
    cin >> vertexCount >> edgeCount;
    const long long infinity = numeric_limits<long long>::max() / 4;
    vector<vector<long long>> distance(
        vertexCount, vector<long long>(vertexCount, infinity)
    );
    for (int vertex = 0; vertex < vertexCount; ++vertex) {
        distance[vertex][vertex] = 0;
    }
    for (int edge = 0; edge < edgeCount; ++edge) {
        int from, to;
        long long weight;
        cin >> from >> to >> weight;
        --from;
        --to;
        distance[from][to] = min(distance[from][to], weight);
    }
    for (int middle = 0; middle < vertexCount; ++middle) {
        for (int from = 0; from < vertexCount; ++from) {
            for (int to = 0; to < vertexCount; ++to) {
                if (distance[from][middle] == infinity ||
                    distance[middle][to] == infinity) {
                    continue;
                }
                distance[from][to] = min(
                    distance[from][to],
                    distance[from][middle] + distance[middle][to]
                );
            }
        }
    }

    int stateCount = 1 << vertexCount;
    int fullMask = stateCount - 1;
    vector<long long> best(static_cast<size_t>(stateCount) * vertexCount, infinity);
    for (int vertex = 0; vertex < vertexCount; ++vertex) {
        best[(1 << vertex) * vertexCount + vertex] = 0;
    }
    for (int mask = 1; mask < stateCount; ++mask) {
        for (int last = 0; last < vertexCount; ++last) {
            long long value = best[static_cast<size_t>(mask) * vertexCount + last];
            if (value == infinity) {
                continue;
            }
            int remaining = fullMask ^ mask;
            while (remaining) {
++_lcb_count;

                int next = countr_zero(static_cast<unsigned>(remaining));
                remaining &= remaining - 1;
                if (distance[last][next] == infinity) {
                    continue;
                }
                long long candidate = value + distance[last][next];
                size_t index = static_cast<size_t>(mask | 1 << next) * vertexCount + next;
                best[index] = min(best[index], candidate);
            }
if (_lcb_count > 1000) {
std::cout << "{\"fullMask\":";
_lcb_json(std::cout, fullMask);
std::cout << ",\"last\":";
_lcb_json(std::cout, last);
std::cout << ",\"mask\":";
_lcb_json(std::cout, mask);
std::cout << ",\"remaining\":";
_lcb_json(std::cout, remaining);
std::cout << ",\"value\":";
_lcb_json(std::cout, value);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

        }
    }

    long long answer = infinity;
    for (int last = 0; last < vertexCount; ++last) {
        answer = min(answer, best[static_cast<size_t>(fullMask) * vertexCount + last]);
    }
    if (answer == infinity) {
        cout << "No\n";
    } else {
        cout << answer << '\n';
    }
}
