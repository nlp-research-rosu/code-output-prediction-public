#include <algorithm>
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
                int next = countr_zero(static_cast<unsigned>(remaining));
                remaining &= remaining - 1;
                if (distance[last][next] == infinity) {
                    continue;
                }
                long long candidate = value + distance[last][next];
                size_t index = static_cast<size_t>(mask | 1 << next) * vertexCount + next;
                best[index] = min(best[index], candidate);
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
