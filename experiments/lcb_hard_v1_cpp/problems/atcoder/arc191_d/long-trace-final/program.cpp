#include <algorithm>
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
            int nextUsed = usedOutsideEdge ||
                           !pathEdges.contains(minmax(vertex, neighbor));
            if (alternate[neighbor][nextUsed] != -1) {
                continue;
            }
            alternate[neighbor][nextUsed] = alternate[vertex][usedOutsideEdge] + 1;
            states.push({neighbor, nextUsed});
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
