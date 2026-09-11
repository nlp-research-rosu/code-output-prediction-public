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

#include <iostream>
#include <limits>
#include <queue>
#include <set>
#include <utility>
#include <vector>

using namespace std;

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int vertexCount, edgeCount, start, target;
    cin >> vertexCount >> edgeCount >> start >> target;
    --start;
    --target;
    vector<vector<int>> graph(vertexCount);
    for (int edge = 0; edge < edgeCount; ++edge) {
        int left, right;
        cin >> left >> right;
        --left;
        --right;
        graph[left].push_back(right);
        graph[right].push_back(left);
    }

    vector<int> distance(vertexCount, -1), parent(vertexCount, -1), ways(vertexCount);
    queue<int> pending;
    distance[start] = 0;
    ways[start] = 1;
    pending.push(start);
    while (!pending.empty()) {
        int vertex = pending.front();
        pending.pop();
        for (int neighbor : graph[vertex]) {
            if (distance[neighbor] == -1) {
                distance[neighbor] = distance[vertex] + 1;
                parent[neighbor] = vertex;
                ways[neighbor] = ways[vertex];
                pending.push(neighbor);
            } else if (distance[neighbor] == distance[vertex] + 1) {
                ways[neighbor] = min(2, ways[neighbor] + ways[vertex]);
            }
        }
    }

    int shortest = distance[target];
    if (ways[target] >= 2) {
        cout << 2 * shortest << '\n';
        return 0;
    }

    vector<int> path;
    for (int vertex = target; vertex != -1; vertex = parent[vertex]) {
        path.push_back(vertex);
    }
    reverse(path.begin(), path.end());
    set<pair<int, int>> pathEdges;
    for (int index = 0; index < shortest; ++index) {
        pathEdges.insert(minmax(path[index], path[index + 1]));
    }

    vector<vector<int>> alternate(vertexCount, vector<int>(2, -1));
    queue<pair<int, int>> states;
    alternate[start][0] = 0;
    states.push({start, 0});
    while (!states.empty()) {
        auto [vertex, usedOutsideEdge] = states.front();
        states.pop();
        for (int neighbor : graph[vertex]) {
++_lcb_count;

            int nextUsed = usedOutsideEdge ||
                           !pathEdges.contains(minmax(vertex, neighbor));
            if (alternate[neighbor][nextUsed] != -1) {
                continue;
            }
            alternate[neighbor][nextUsed] = alternate[vertex][usedOutsideEdge] + 1;
            states.push({neighbor, nextUsed});
        }
if (_lcb_count > 1000) {
std::cout << "{\"alternate[vertex][usedOutsideEdge]\":";
_lcb_json(std::cout, alternate[vertex][usedOutsideEdge]);
std::cout << ",\"path\":";
_lcb_json(std::cout, path);
std::cout << ",\"pathEdges.size()\":";
_lcb_json(std::cout, pathEdges.size());
std::cout << ",\"states.size()\":";
_lcb_json(std::cout, states.size());
std::cout << ",\"usedOutsideEdge\":";
_lcb_json(std::cout, usedOutsideEdge);
std::cout << ",\"vertex\":";
_lcb_json(std::cout, vertex);
std::cout << "}\n";
std::cout.flush();
std::_Exit(0);
}

    }
    if (alternate[target][1] != -1 && alternate[target][1] <= shortest + 1) {
        cout << 2 * shortest + 1 << '\n';
        return 0;
    }

    for (int index = 1; index < shortest; ++index) {
        if (graph[path[index]].size() >= 3) {
            cout << 2 * shortest + 2 << '\n';
            return 0;
        }
    }

    vector<int> detachedDistance(vertexCount, -1);
    detachedDistance[start] = 0;
    pending.push(start);
    while (!pending.empty()) {
        int vertex = pending.front();
        pending.pop();
        for (int neighbor : graph[vertex]) {
            if (pathEdges.contains(minmax(vertex, neighbor)) ||
                detachedDistance[neighbor] != -1) {
                continue;
            }
            detachedDistance[neighbor] = detachedDistance[vertex] + 1;
            pending.push(neighbor);
        }
    }
    int alternatePath = detachedDistance[target];

    auto branchDistance = [&](int endpoint, int towardPath) {
        int previous = towardPath;
        int vertex = endpoint;
        int result = 0;
        while (graph[vertex].size() == 2) {
            int next = graph[vertex][0] == previous
                           ? graph[vertex][1]
                           : graph[vertex][0];
            previous = vertex;
            vertex = next;
            ++result;
        }
        return graph[vertex].size() >= 3
                   ? result
                   : numeric_limits<int>::max() / 4;
    };

    int branch = min(
        branchDistance(start, path[1]),
        branchDistance(target, path[shortest - 1])
    );
    int answer = numeric_limits<int>::max() / 2;
    if (alternatePath != -1) {
        answer = min(answer, shortest + alternatePath);
    }
    if (branch < numeric_limits<int>::max() / 4) {
        answer = min(answer, 2 * shortest + 4 * branch + 4);
    }
    cout << (answer == numeric_limits<int>::max() / 2 ? -1 : answer) << '\n';
}
