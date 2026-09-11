from __future__ import annotations

from dataclasses import dataclass
import json
import random


@dataclass(frozen=True)
class AlgorithmSpec:
    case_id: str
    title: str
    category: str
    reference: str
    reference_url: str
    source_origin: str
    source: str
    short_input: str
    long_input: str
    anchor: str
    in_state: str
    out_anchor: str
    out_state: str


def packed(value: object) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n"


def matrix(size: int, seed: int, low: int, high: int, diagonal: int | None = None) -> list[list[int]]:
    rng = random.Random(seed)
    result = [[rng.randint(low, high) for _ in range(size)] for _ in range(size)]
    if diagonal is not None:
        for index in range(size):
            result[index][index] = diagonal
    return result


def connected_graph(nodes: int, extra_edges: int, seed: int, directed: bool) -> list[list[int]]:
    rng = random.Random(seed)
    edges: list[list[int]] = []
    seen: set[tuple[int, int]] = set()
    for node in range(nodes - 1):
        weight = rng.randint(1, 30)
        edge = (node, node + 1)
        edges.append([node, node + 1, weight])
        seen.add(edge)
        if not directed:
            seen.add((node + 1, node))
    while len(edges) < nodes - 1 + extra_edges:
        left = rng.randrange(nodes)
        right = rng.randrange(nodes)
        if left == right or (left, right) in seen:
            continue
        edges.append([left, right, rng.randint(1, 30)])
        seen.add((left, right))
        if not directed:
            seen.add((right, left))
    return edges


def dag(nodes: int, edge_count: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    candidates = [(left, right) for left in range(nodes) for right in range(left + 1, nodes)]
    rng.shuffle(candidates)
    return [[left, right] for left, right in candidates[:edge_count]]


FLOYD_WARSHALL = '''import json


def main():
    n = int(input())
    dist = [list(map(int, input().split())) for _ in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                candidate = dist[i][k] + dist[k][j]
                if candidate < dist[i][j]:
                    dist[i][j] = candidate
    print(json.dumps(dist, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


MATRIX_MULTIPLICATION = '''import json


def main():
    n = int(input())
    left = [list(map(int, input().split())) for _ in range(n)]
    right = [list(map(int, input().split())) for _ in range(n)]
    result = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            total = 0
            for k in range(n):
                total += left[i][k] * right[k][j]
            result[i][j] = total
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


N_BODY = '''import json


def sign(value):
    return (value > 0) - (value < 0)


def main():
    n, steps = map(int, input().split())
    rows = [list(map(int, input().split())) for _ in range(n)]
    positions = [[row[0], row[1]] for row in rows]
    velocities = [[row[2], row[3]] for row in rows]
    for step in range(steps):
        acceleration = [[0, 0] for _ in range(n)]
        for i in range(n):
            for j in range(i + 1, n):
                dx = positions[j][0] - positions[i][0]
                dy = positions[j][1] - positions[i][1]
                sx, sy = sign(dx), sign(dy)
                acceleration[i][0] += sx
                acceleration[i][1] += sy
                acceleration[j][0] -= sx
                acceleration[j][1] -= sy
        for i in range(n):
            velocities[i][0] += acceleration[i][0]
            velocities[i][1] += acceleration[i][1]
            positions[i][0] += velocities[i][0]
            positions[i][1] += velocities[i][1]
    print(json.dumps({"positions": positions, "velocities": velocities}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
'''


KMP = '''import json


def prefix_function(pattern):
    lps = [0] * len(pattern)
    matched = 0
    for i in range(1, len(pattern)):
        while matched > 0 and pattern[i] != pattern[matched]:
            matched = lps[matched - 1]
        if pattern[i] == pattern[matched]:
            matched += 1
        lps[i] = matched
    return lps


def main():
    text = input().strip()
    pattern = input().strip()
    lps = prefix_function(pattern)
    matched = 0
    matches = []
    for index in range(len(text)):
        ch = text[index]
        while matched > 0 and ch != pattern[matched]:
            matched = lps[matched - 1]
        if ch == pattern[matched]:
            matched += 1
        if matched == len(pattern):
            matches.append(index - len(pattern) + 1)
            matched = lps[matched - 1]
    print(json.dumps(matches, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


LCS = '''def main():
    left = input().strip()
    right = input().strip()
    previous = [0] * (len(right) + 1)
    for i in range(1, len(left) + 1):
        current = [0] * (len(right) + 1)
        for j in range(1, len(right) + 1):
            if left[i - 1] == right[j - 1]:
                current[j] = previous[j - 1] + 1
            else:
                current[j] = max(previous[j], current[j - 1])
        previous = current
    print(previous[-1])


if __name__ == "__main__":
    main()
'''


MATRIX_CHAIN = '''import json


def main():
    n = int(input())
    dimensions = list(map(int, input().split()))
    infinity = 10**30
    dp = [[0] * n for _ in range(n)]
    for chain_length in range(2, n + 1):
        for left in range(n - chain_length + 1):
            right = left + chain_length - 1
            dp[left][right] = infinity
            for split in range(left, right):
                cost = dp[left][split] + dp[split + 1][right] + dimensions[left] * dimensions[split + 1] * dimensions[right + 1]
                if cost < dp[left][right]:
                    dp[left][right] = cost
    print(json.dumps({"minimum_cost": dp[0][n - 1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


EDIT_DISTANCE = '''def main():
    source = input().strip()
    target = input().strip()
    previous = list(range(len(target) + 1))
    for i in range(1, len(source) + 1):
        current = [i] + [0] * len(target)
        for j in range(1, len(target) + 1):
            if source[i - 1] == target[j - 1]:
                current[j] = previous[j - 1]
            else:
                current[j] = 1 + min(previous[j], current[j - 1], previous[j - 1])
        previous = current
    print(previous[-1])


if __name__ == "__main__":
    main()
'''


KNAPSACK = '''def main():
    n, capacity = map(int, input().split())
    items = [tuple(map(int, input().split())) for _ in range(n)]
    dp = [0] * (capacity + 1)
    for index, (weight, value) in enumerate(items):
        for current_capacity in range(capacity, 0, -1):
            if weight <= current_capacity:
                dp[current_capacity] = max(dp[current_capacity], dp[current_capacity - weight] + value)
    print(dp[capacity])


if __name__ == "__main__":
    main()
'''


HELD_KARP = '''import itertools


def main():
    n = int(input())
    distances = [list(map(int, input().split())) for _ in range(n)]
    dp = {(1, 0): 0}
    for subset_size in range(1, n):
        for subset in itertools.combinations(range(1, n), subset_size):
            mask = 1
            for city in subset:
                mask |= 1 << city
            for last in subset:
                previous_mask = mask ^ (1 << last)
                best = 10**30
                for previous in range(n):
                    if previous == last:
                        continue
                    state = (previous_mask, previous)
                    if state in dp:
                        candidate = dp[state] + distances[previous][last]
                        if candidate < best:
                            best = candidate
                dp[(mask, last)] = best
    full_mask = (1 << n) - 1
    answer = min(dp[(full_mask, last)] + distances[last][0] for last in range(1, n))
    print(answer)


if __name__ == "__main__":
    main()
'''


EDMONDS_KARP = '''def main():
    n, m, source, sink = map(int, input().split())
    adjacency = [[] for _ in range(n)]
    edges = []

    def add_edge(u, v, capacity):
        adjacency[u].append(len(edges))
        edges.append([v, capacity])
        adjacency[v].append(len(edges))
        edges.append([u, 0])

    for _ in range(m):
        u, v, capacity = map(int, input().split())
        add_edge(u, v, capacity)

    flow = 0
    while True:
        parent = [-1] * n
        parent_edge = [-1] * n
        parent[source] = source
        queue = [source]
        head = 0
        while head < len(queue) and parent[sink] == -1:
            node = queue[head]
            head += 1
            for edge_index in adjacency[node]:
                neighbor = edges[edge_index][0]
                residual = edges[edge_index][1]
                if residual > 0 and parent[neighbor] == -1:
                    parent[neighbor] = node
                    parent_edge[neighbor] = edge_index
                    queue.append(neighbor)
        if parent[sink] == -1:
            break
        bottleneck = 10**30
        node = sink
        while node != source:
            edge_index = parent_edge[node]
            bottleneck = min(bottleneck, edges[edge_index][1])
            node = parent[node]
        node = sink
        while node != source:
            edge_index = parent_edge[node]
            edges[edge_index][1] -= bottleneck
            edges[edge_index ^ 1][1] += bottleneck
            node = parent[node]
        flow += bottleneck
    print(flow)


if __name__ == "__main__":
    main()
'''


COIN_CHANGE = '''import json


def main():
    data = json.load(__import__("sys").stdin)
    coins = data["coins"]
    amount = data["amount"]
    infinity = amount + 1
    dp = [0] + [infinity] * amount
    choice = [-1] * (amount + 1)
    for current in range(1, amount + 1):
        for coin in coins:
            if coin <= current and dp[current - coin] + 1 < dp[current]:
                dp[current] = dp[current - coin] + 1
                choice[current] = coin
    print(json.dumps({"minimum_coins": -1 if dp[amount] == infinity else dp[amount]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


ROD_CUTTING = '''import json


def main():
    data = json.load(__import__("sys").stdin)
    prices = data["prices"]
    length = data["length"]
    best = [0] * (length + 1)
    first_cut = [0] * (length + 1)
    for current in range(1, length + 1):
        for cut in range(1, min(current, len(prices)) + 1):
            candidate = prices[cut - 1] + best[current - cut]
            if candidate > best[current]:
                best[current] = candidate
                first_cut[current] = cut
    print(json.dumps({"maximum_revenue": best[length]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


LONGEST_INCREASING_SUBSEQUENCE = '''import json


def main():
    values = json.load(__import__("sys").stdin)
    n = len(values)
    length = [1] * n
    parent = [-1] * n
    for right in range(n):
        for left in range(right):
            if values[left] < values[right] and length[left] + 1 > length[right]:
                length[right] = length[left] + 1
                parent[right] = left
    end = max(range(n), key=length.__getitem__)
    sequence = []
    while end != -1:
        sequence.append(values[end])
        end = parent[end]
    print(json.dumps(sequence[::-1], separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


WEIGHTED_INTERVAL_SCHEDULING = '''import bisect
import json


def main():
    intervals = json.load(__import__("sys").stdin)
    intervals.sort(key=lambda item: (item[1], item[0], item[2]))
    finishes = [item[1] for item in intervals]
    predecessor = [bisect.bisect_right(finishes, item[0]) - 1 for item in intervals]
    dp = [0] * (len(intervals) + 1)
    take = [False] * len(intervals)
    for index, (_, _, weight) in enumerate(intervals, start=1):
        include = weight + dp[predecessor[index - 1] + 1]
        exclude = dp[index - 1]
        if include > exclude:
            dp[index] = include
            take[index - 1] = True
        else:
            dp[index] = exclude
    print(json.dumps({"maximum_weight": dp[-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


LONGEST_PALINDROMIC_SUBSEQUENCE = '''import json


def main():
    text = input().strip()
    n = len(text)
    dp = [[0] * n for _ in range(n)]
    for left in range(n - 1, -1, -1):
        dp[left][left] = 1
        for right in range(left + 1, n):
            if text[left] == text[right]:
                dp[left][right] = 2 + (dp[left + 1][right - 1] if right - left > 1 else 0)
            else:
                dp[left][right] = max(dp[left + 1][right], dp[left][right - 1])
    print(json.dumps({"length": dp[0][n - 1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


PALINDROME_PARTITIONING = '''import json


def main():
    text = input().strip()
    n = len(text)
    palindrome = [[False] * n for _ in range(n)]
    cuts = list(range(n))
    for right in range(n):
        for left in range(right + 1):
            if text[left] == text[right] and (right - left <= 2 or palindrome[left + 1][right - 1]):
                palindrome[left][right] = True
                cuts[right] = 0 if left == 0 else min(cuts[right], cuts[left - 1] + 1)
    print(json.dumps({"minimum_cuts": cuts[-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


SUBSET_SUM = '''import json


def main():
    data = json.load(__import__("sys").stdin)
    values = data["values"]
    target = data["target"]
    dp = [[False] * (target + 1) for _ in range(len(values) + 1)]
    dp[0][0] = True
    for index, value in enumerate(values, start=1):
        for total in range(target + 1):
            dp[index][total] = dp[index - 1][total] or (total >= value and dp[index - 1][total - value])
    print(json.dumps({"reachable": dp[-1][target]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


MINIMUM_COST_GRID_PATH = '''import json


def main():
    grid = json.load(__import__("sys").stdin)
    rows = len(grid)
    columns = len(grid[0])
    dp = [[0] * columns for _ in range(rows)]
    for row in range(rows):
        for column in range(columns):
            if row == 0 and column == 0:
                dp[row][column] = grid[row][column]
            elif row == 0:
                dp[row][column] = dp[row][column - 1] + grid[row][column]
            elif column == 0:
                dp[row][column] = dp[row - 1][column] + grid[row][column]
            else:
                dp[row][column] = min(dp[row - 1][column], dp[row][column - 1]) + grid[row][column]
    print(json.dumps({"minimum_cost": dp[-1][-1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


OPTIMAL_BINARY_SEARCH_TREE = '''import json


def main():
    frequencies = json.load(__import__("sys").stdin)
    n = len(frequencies)
    prefix = [0]
    for value in frequencies:
        prefix.append(prefix[-1] + value)
    cost = [[0] * n for _ in range(n)]
    root = [[-1] * n for _ in range(n)]
    for length in range(1, n + 1):
        for left in range(n - length + 1):
            right = left + length - 1
            total = prefix[right + 1] - prefix[left]
            cost[left][right] = 10**30
            for candidate_root in range(left, right + 1):
                candidate = total
                if candidate_root > left:
                    candidate += cost[left][candidate_root - 1]
                if candidate_root < right:
                    candidate += cost[candidate_root + 1][right]
                if candidate < cost[left][right]:
                    cost[left][right] = candidate
                    root[left][right] = candidate_root
    print(json.dumps({"minimum_cost": cost[0][n - 1]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


EGG_DROPPING = '''import json


def main():
    eggs, floors = map(int, input().split())
    dp = [[0] * (floors + 1) for _ in range(eggs + 1)]
    choice = [[0] * (floors + 1) for _ in range(eggs + 1)]
    for floor in range(floors + 1):
        dp[1][floor] = floor
    for egg in range(2, eggs + 1):
        for floor in range(1, floors + 1):
            dp[egg][floor] = 10**30
            for drop in range(1, floor + 1):
                candidate = 1 + max(dp[egg - 1][drop - 1], dp[egg][floor - drop])
                if candidate < dp[egg][floor]:
                    dp[egg][floor] = candidate
                    choice[egg][floor] = drop
    print(json.dumps({"minimum_trials": dp[eggs][floors]}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


DIJKSTRA = '''import heapq
import json


def main():
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    source = data["source"]
    adjacency = [[] for _ in range(n)]
    for left, right, weight in data["edges"]:
        adjacency[left].append((right, weight))
        adjacency[right].append((left, weight))
    infinity = 10**30
    dist = [infinity] * n
    parent = [-1] * n
    dist[source] = 0
    queue = [(0, source)]
    visited = [False] * n
    while queue:
        distance, node = heapq.heappop(queue)
        if visited[node]:
            continue
        visited[node] = True
        for neighbor, weight in adjacency[node]:
            candidate = distance + weight
            if candidate < dist[neighbor]:
                dist[neighbor] = candidate
                parent[neighbor] = node
                heapq.heappush(queue, (candidate, neighbor))
    print(json.dumps({"distances": dist}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


BELLMAN_FORD = '''import json


def main():
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    source = data["source"]
    edges = data["edges"]
    infinity = 10**30
    dist = [infinity] * n
    parent = [-1] * n
    dist[source] = 0
    for pass_index in range(n - 1):
        changed = False
        for left, right, weight in edges:
            if dist[left] != infinity and dist[left] + weight < dist[right]:
                dist[right] = dist[left] + weight
                parent[right] = left
                changed = True
        if not changed:
            break
    print(json.dumps({"distances": dist}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


PRIM = '''import json


def main():
    matrix = json.load(__import__("sys").stdin)
    n = len(matrix)
    infinity = 10**30
    key = [infinity] * n
    parent = [-1] * n
    in_tree = [False] * n
    key[0] = 0
    for step in range(n):
        node = min((index for index in range(n) if not in_tree[index]), key=key.__getitem__)
        in_tree[node] = True
        for neighbor in range(n):
            weight = matrix[node][neighbor]
            if 0 < weight < key[neighbor] and not in_tree[neighbor]:
                key[neighbor] = weight
                parent[neighbor] = node
    print(json.dumps({"weight": sum(key)}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


KRUSKAL = '''import json


def main():
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    edges = sorted(data["edges"], key=lambda edge: (edge[2], edge[0], edge[1]))
    parent = list(range(n))
    rank = [0] * n

    def find(node):
        while parent[node] != node:
            parent[node] = parent[parent[node]]
            node = parent[node]
        return node

    total = 0
    selected = []
    for left, right, weight in edges:
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            continue
        if rank[left_root] < rank[right_root]:
            left_root, right_root = right_root, left_root
        parent[right_root] = left_root
        if rank[left_root] == rank[right_root]:
            rank[left_root] += 1
        selected.append([left, right, weight])
        total += weight
    print(json.dumps({"weight": total}, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


KAHN_TOPOLOGICAL_SORT = '''import heapq
import json


def main():
    data = json.load(__import__("sys").stdin)
    n = data["nodes"]
    adjacency = [[] for _ in range(n)]
    indegree = [0] * n
    for left, right in data["edges"]:
        adjacency[left].append(right)
        indegree[right] += 1
    queue = [node for node in range(n) if indegree[node] == 0]
    heapq.heapify(queue)
    order = []
    while queue:
        node = heapq.heappop(queue)
        order.append(node)
        for neighbor in adjacency[node]:
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                heapq.heappush(queue, neighbor)
    print(json.dumps(order, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


MERGE_SORT = '''import json


def main():
    values = json.load(__import__("sys").stdin)
    n = len(values)
    buffer = [0] * n
    width = 1
    while width < n:
        for start in range(0, n, 2 * width):
            middle = min(start + width, n)
            end = min(start + 2 * width, n)
            left = start
            right = middle
            for target in range(start, end):
                if left < middle and (right >= end or values[left] <= values[right]):
                    buffer[target] = values[left]
                    left += 1
                else:
                    buffer[target] = values[right]
                    right += 1
        values, buffer = buffer, values
        width *= 2
    print(json.dumps(values, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


HEAP_SORT = '''import json


def main():
    values = json.load(__import__("sys").stdin)
    n = len(values)

    def sift_down(root, end):
        while 2 * root + 1 < end:
            child = 2 * root + 1
            if child + 1 < end and values[child] < values[child + 1]:
                child += 1
            if values[root] >= values[child]:
                return
            values[root], values[child] = values[child], values[root]
            root = child

    for root in range(n // 2 - 1, -1, -1):
        sift_down(root, n)
    for end in range(n - 1, 0, -1):
        values[0], values[end] = values[end], values[0]
        sift_down(0, end)
    print(json.dumps(values, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


RABIN_KARP = '''import json


def main():
    text = input().strip()
    pattern = input().strip()
    base = 257
    modulus = 1000000007
    length = len(pattern)
    power = pow(base, length - 1, modulus)
    pattern_hash = 0
    window_hash = 0
    for index in range(length):
        pattern_hash = (pattern_hash * base + ord(pattern[index])) % modulus
        window_hash = (window_hash * base + ord(text[index])) % modulus
    matches = []
    for start in range(len(text) - length + 1):
        if window_hash == pattern_hash and text[start:start + length] == pattern:
            matches.append(start)
        if start + length < len(text):
            window_hash = (window_hash - ord(text[start]) * power) % modulus
            window_hash = (window_hash * base + ord(text[start + length])) % modulus
    print(json.dumps(matches, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


Z_ALGORITHM = '''import json


def main():
    text = input().strip()
    z = [0] * len(text)
    left = 0
    right = 0
    for index in range(1, len(text)):
        if index <= right:
            z[index] = min(right - index + 1, z[index - left])
        while index + z[index] < len(text) and text[z[index]] == text[index + z[index]]:
            z[index] += 1
        if index + z[index] - 1 > right:
            left = index
            right = index + z[index] - 1
    print(json.dumps(z, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


MONOTONE_CHAIN = '''import json


def cross(origin, left, right):
    return (left[0] - origin[0]) * (right[1] - origin[1]) - (left[1] - origin[1]) * (right[0] - origin[0])


def main():
    points = sorted(set(map(tuple, json.load(__import__("sys").stdin))))
    if len(points) <= 1:
        print(json.dumps(points, separators=(",", ":")))
        return
    lower = []
    for point in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:
            lower.pop()
        lower.append(point)
    upper = []
    for point in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], point) <= 0:
            upper.pop()
        upper.append(point)
    hull = lower[:-1] + upper[:-1]
    print(json.dumps(hull, separators=(",", ":")))


if __name__ == "__main__":
    main()
'''


TEXTBOOK_URL = "https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/"


def lines(rows: list[list[int]]) -> str:
    return "\n".join(" ".join(map(str, row)) for row in rows) + "\n"


def sized_matrix_input(size: int, seed: int, low: int, high: int, diagonal: int | None = None) -> str:
    return f"{size}\n" + lines(matrix(size, seed, low, high, diagonal))


def multiplication_input(size: int, seed: int) -> str:
    return f"{size}\n" + lines(matrix(size, seed, -9, 9)) + lines(matrix(size, seed + 1, -9, 9))


def n_body_input(size: int, steps: int, seed: int) -> str:
    rng = random.Random(seed)
    rows = [[rng.randint(-60, 60), rng.randint(-60, 60), rng.randint(-3, 3), rng.randint(-3, 3)] for _ in range(size)]
    return f"{size} {steps}\n" + lines(rows)


def random_text(length: int, seed: int, alphabet: str = "abcdef") -> str:
    rng = random.Random(seed)
    return "".join(rng.choice(alphabet) for _ in range(length))


def text_with_pattern(length: int, pattern: str, positions: tuple[int, ...], seed: int) -> str:
    characters = list(random_text(length, seed))
    for position in positions:
        characters[position : position + len(pattern)] = pattern
    return "".join(characters)


def dimensions_input(size: int, seed: int) -> str:
    rng = random.Random(seed)
    return f"{size}\n" + " ".join(str(rng.randint(3, 40)) for _ in range(size + 1)) + "\n"


def knapsack_input(count: int, capacity: int, seed: int) -> str:
    rng = random.Random(seed)
    items = [[rng.randint(2, max(3, capacity // 5)), rng.randint(5, 60)] for _ in range(count)]
    return f"{count} {capacity}\n" + lines(items)


def edmonds_karp_input(width: int, layers: int, seed: int) -> str:
    rng = random.Random(seed)
    source = 0
    sink = 1 + width * layers
    edges: list[list[int]] = []
    for node in range(width):
        edges.append([source, 1 + node, rng.randint(3, 12)])
    for layer in range(layers - 1):
        left_start = 1 + layer * width
        right_start = left_start + width
        for left in range(width):
            for right in range(width):
                edges.append([left_start + left, right_start + right, rng.randint(1, 9)])
    final_start = 1 + (layers - 1) * width
    for node in range(width):
        edges.append([final_start + node, sink, rng.randint(3, 12)])
    return f"{sink + 1} {len(edges)} {source} {sink}\n" + lines(edges)


def intervals(count: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    result = []
    for _ in range(count):
        start = rng.randint(0, count * 3)
        result.append([start, start + rng.randint(1, 12), rng.randint(5, 80)])
    return result


def points(count: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    result: set[tuple[int, int]] = set()
    while len(result) < count:
        result.add((rng.randint(-500, 500), rng.randint(-500, 500)))
    return [list(point) for point in sorted(result)]


def mst_matrix(size: int, seed: int) -> list[list[int]]:
    rng = random.Random(seed)
    result = [[0] * size for _ in range(size)]
    for left in range(size):
        for right in range(left + 1, size):
            value = rng.randint(1, 50)
            result[left][right] = value
            result[right][left] = value
    return result


def spec(
    case_id: str,
    title: str,
    category: str,
    reference: str,
    reference_url: str,
    source_origin: str,
    source: str,
    short_input: str,
    long_input: str,
    anchor: str,
    in_state: str,
    out_anchor: str,
    out_state: str,
) -> AlgorithmSpec:
    return AlgorithmSpec(case_id, title, category, reference, reference_url, source_origin, source, short_input, long_input, anchor, in_state, out_anchor, out_state)


def make_specs() -> tuple[AlgorithmSpec, ...]:
    original = "adapted from PR 5 head c40257a4d45262c52084bfb7fe5f03c401bd4d56"
    added = "repository-authored textbook implementation"
    tsp_simple = matrix(6, 109, 4, 45, 0)
    tsp_hard = matrix(9, 110, 4, 45, 0)
    bellman_simple = connected_graph(10, 24, 211, True)
    bellman_hard = connected_graph(32, 190, 212, True)
    return (
        spec("floyd-warshall", "Floyd-Warshall Algorithm", "graph dynamic programming", "Floyd, Algorithm 97: Shortest Path", "https://doi.org/10.1145/367766.368168", original, FLOYD_WARSHALL, sized_matrix_input(5, 101, 2, 40, 0), sized_matrix_input(12, 102, 2, 40, 0), "                candidate = dist[i][k] + dist[k][j]\n", '{"dist": dist, "i": i, "j": j, "k": k, "n": n}', '    print(json.dumps(dist, separators=(",", ":")))\n', '{"dist": dist, "n": n}'),
        spec("matrix-multiplication", "Naive Matrix Multiplication", "numerical", "Introduction to Algorithms, matrix multiplication", TEXTBOOK_URL, original, MATRIX_MULTIPLICATION, multiplication_input(4, 103), multiplication_input(12, 104), "                total += left[i][k] * right[k][j]\n", '{"i": i, "j": j, "k": k, "left": left, "n": n, "result": result, "right": right, "total": total}', '    print(json.dumps(result, separators=(",", ":")))\n', '{"left": left, "n": n, "result": result, "right": right}'),
        spec("n-body", "Discrete N-Body Simulation", "simulation", "Aarseth, Gravitational N-Body Simulations", "https://doi.org/10.1017/CBO9780511535246", original, N_BODY, n_body_input(6, 3, 105), n_body_input(20, 6, 106), "                dx = positions[j][0] - positions[i][0]\n", '{"acceleration": acceleration, "i": i, "j": j, "n": n, "positions": positions, "step": step, "velocities": velocities}', '    print(json.dumps({"positions": positions, "velocities": velocities}, separators=(",", ":"), sort_keys=True))\n', '{"positions": positions, "steps": steps, "velocities": velocities}'),
        spec("kmp", "Knuth-Morris-Pratt Pattern Matching", "string", "Knuth, Morris, and Pratt, Fast Pattern Matching in Strings", "https://doi.org/10.1137/0206024", original, KMP, text_with_pattern(60, "ababaca", (12,), 107) + "\nababaca\n", text_with_pattern(220, "abacabadabacabae", (25, 170), 108) + "\nabacabadabacabae\n", "        ch = text[index]\n", '{"index": index, "lps": lps, "matched": matched, "matches": matches, "pattern": pattern, "text": text}', '    print(json.dumps(matches, separators=(",", ":")))\n', '{"lps": lps, "matched": matched, "matches": matches, "pattern": pattern, "text": text}'),
        spec("longest-common-subsequence", "Longest Common Subsequence", "dynamic programming", "Introduction to Algorithms, longest common subsequence", TEXTBOOK_URL, original, LCS, random_text(12, 111) + "\n" + random_text(14, 112) + "\n", random_text(36, 113) + "\n" + random_text(38, 114) + "\n", "            if left[i - 1] == right[j - 1]:\n", '{"current": current, "i": i, "j": j, "left": left, "previous": previous, "right": right}', "    print(previous[-1])\n", '{"left": left, "previous": previous, "right": right}'),
        spec("matrix-chain-multiplication", "Matrix Chain Multiplication", "dynamic programming", "Introduction to Algorithms, matrix-chain multiplication", TEXTBOOK_URL, original, MATRIX_CHAIN, dimensions_input(7, 115), dimensions_input(20, 116), "                cost = dp[left][split] + dp[split + 1][right] + dimensions[left] * dimensions[split + 1] * dimensions[right + 1]\n", '{"chain_length": chain_length, "dimensions": dimensions, "dp": dp, "left": left, "right": right, "split": split}', '    print(json.dumps({"minimum_cost": dp[0][n - 1]}, separators=(",", ":")))\n', '{"dimensions": dimensions, "dp": dp, "n": n}'),
        spec("edit-distance", "Levenshtein Edit Distance", "dynamic programming", "Wagner and Fischer, The String-to-String Correction Problem", "https://doi.org/10.1145/321796.321811", original, EDIT_DISTANCE, random_text(12, 117, "abcdefgh") + "\n" + random_text(14, 118, "abcdefgh") + "\n", random_text(38, 119, "abcdefgh") + "\n" + random_text(40, 120, "abcdefgh") + "\n", "            if source[i - 1] == target[j - 1]:\n", '{"current": current, "i": i, "j": j, "previous": previous, "source": source, "target": target}', "    print(previous[-1])\n", '{"previous": previous, "source": source, "target": target}'),
        spec("knapsack-01", "0/1 Knapsack", "dynamic programming", "Introduction to Algorithms, 0/1 knapsack", TEXTBOOK_URL, original, KNAPSACK, knapsack_input(8, 30, 121), knapsack_input(20, 100, 122), "            if weight <= current_capacity:\n", '{"current_capacity": current_capacity, "dp": dp, "index": index, "items": items, "value": value, "weight": weight}', "    print(dp[capacity])\n", '{"capacity": capacity, "dp": dp, "items": items}'),
        spec("traveling-salesperson-held-karp", "Traveling Salesperson (Held-Karp)", "subset dynamic programming", "Held and Karp, A Dynamic Programming Approach to Sequencing Problems", "https://doi.org/10.1137/0110015", original, HELD_KARP, f"6\n{lines(tsp_simple)}", f"9\n{lines(tsp_hard)}", "                        candidate = dp[state] + distances[previous][last]\n", '{"best": best, "distances": distances, "dp": [[key[0], key[1], value] for key, value in sorted(dp.items())], "last": last, "mask": mask, "previous": previous, "previous_mask": previous_mask, "subset": subset, "subset_size": subset_size}', "    print(answer)\n", '{"answer": answer, "distances": distances, "dp": [[key[0], key[1], value] for key, value in sorted(dp.items())]}'),
        spec("edmonds-karp", "Edmonds-Karp Maximum Flow", "graph", "Edmonds and Karp, Theoretical Improvements in Algorithmic Efficiency for Network Flow Problems", "https://doi.org/10.1145/321694.321699", original, EDMONDS_KARP, edmonds_karp_input(3, 2, 123), edmonds_karp_input(8, 3, 124), "                neighbor = edges[edge_index][0]\n", '{"adjacency": adjacency, "edge_index": edge_index, "edges": edges, "flow": flow, "head": head, "node": node, "parent": parent, "parent_edge": parent_edge, "queue": queue, "sink": sink, "source": source}', "    print(flow)\n", '{"adjacency": adjacency, "edges": edges, "flow": flow, "sink": sink, "source": source}'),
        spec("coin-change", "Minimum Coin Change", "dynamic programming", "Introduction to Algorithms, dynamic programming", TEXTBOOK_URL, added, COIN_CHANGE, packed({"coins": [1, 4, 7, 13], "amount": 36}), packed({"coins": [1, 7, 13, 29, 43], "amount": 173}), "            if coin <= current and dp[current - coin] + 1 < dp[current]:\n", '{"amount": amount, "choice": choice, "coin": coin, "coins": coins, "current": current, "dp": dp}', '    print(json.dumps({"minimum_coins": -1 if dp[amount] == infinity else dp[amount]}, separators=(",", ":")))\n', '{"amount": amount, "choice": choice, "coins": coins, "dp": dp}'),
        spec("rod-cutting", "Rod Cutting", "dynamic programming", "Introduction to Algorithms, rod cutting", TEXTBOOK_URL, added, ROD_CUTTING, packed({"prices": [2, 5, 7, 8, 10, 13, 17, 18, 22, 25, 27, 30], "length": 12}), packed({"prices": [2, 5, 7, 8, 10, 13, 17, 18, 22, 25, 27, 30, 33, 35, 39, 41, 44, 47, 49, 52], "length": 48}), "            candidate = prices[cut - 1] + best[current - cut]\n", '{"best": best, "candidate": best[current], "current": current, "cut": cut, "first_cut": first_cut, "length": length, "prices": prices}', '    print(json.dumps({"maximum_revenue": best[length]}, separators=(",", ":")))\n', '{"best": best, "first_cut": first_cut, "length": length, "prices": prices}'),
        spec("longest-increasing-subsequence", "Longest Increasing Subsequence", "dynamic programming", "Introduction to Algorithms, longest increasing subsequence", TEXTBOOK_URL, added, LONGEST_INCREASING_SUBSEQUENCE, packed([17, 4, 9, 2, 15, 6, 11, 3, 18, 8, 14, 20, 1, 16, 10, 22, 7, 19]), packed([random.Random(201 + index).randint(0, 500) for index in range(80)]), "            if values[left] < values[right] and length[left] + 1 > length[right]:\n", '{"left": left, "length": length, "parent": parent, "right": right, "values": values}', '    print(json.dumps(sequence[::-1], separators=(",", ":")))\n', '{"length": length, "parent": parent, "sequence": sequence, "values": values}'),
        spec("weighted-interval-scheduling", "Weighted Interval Scheduling", "dynamic programming", "Kleinberg and Tardos, Algorithm Design, weighted interval scheduling", "https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003259", added, WEIGHTED_INTERVAL_SCHEDULING, packed(intervals(40, 202)), packed(intervals(240, 203)), "        include = weight + dp[predecessor[index - 1] + 1]\n", '{"dp": dp, "index": index, "intervals": intervals, "predecessor": predecessor, "take": take, "weight": weight}', '    print(json.dumps({"maximum_weight": dp[-1]}, separators=(",", ":")))\n', '{"dp": dp, "intervals": intervals, "predecessor": predecessor, "take": take}'),
        spec("longest-palindromic-subsequence", "Longest Palindromic Subsequence", "dynamic programming", "Classical interval dynamic programming recurrence", TEXTBOOK_URL, added, LONGEST_PALINDROMIC_SUBSEQUENCE, random_text(18, 204, "abcde") + "\n", random_text(54, 205, "abcde") + "\n", "            if text[left] == text[right]:\n", '{"dp": dp, "left": left, "right": right, "text": text}', '    print(json.dumps({"length": dp[0][n - 1]}, separators=(",", ":")))\n', '{"dp": dp, "n": n, "text": text}'),
        spec("palindrome-partitioning", "Minimum Palindrome Partitioning", "dynamic programming", "Classical palindrome-table and minimum-cut dynamic programming", TEXTBOOK_URL, added, PALINDROME_PARTITIONING, random_text(14, 206, "abcd") + "\n", random_text(40, 207, "abcd") + "\n", "            if text[left] == text[right] and (right - left <= 2 or palindrome[left + 1][right - 1]):\n", '{"cuts": cuts, "left": left, "palindrome": palindrome, "right": right, "text": text}', '    print(json.dumps({"minimum_cuts": cuts[-1]}, separators=(",", ":")))\n', '{"cuts": cuts, "palindrome": palindrome, "text": text}'),
        spec("subset-sum", "Subset Sum", "dynamic programming", "Bellman, Dynamic Programming", "https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming", added, SUBSET_SUM, packed({"values": [4, 8, 12, 16, 20, 24, 28, 32], "target": 31}), packed({"values": [random.Random(208 + index).randint(2, 25) for index in range(20)], "target": 80}), "            dp[index][total] = dp[index - 1][total] or (total >= value and dp[index - 1][total - value])\n", '{"dp": dp, "index": index, "target": target, "total": total, "value": value, "values": values}', '    print(json.dumps({"reachable": dp[-1][target]}, separators=(",", ":")))\n', '{"dp": dp, "target": target, "values": values}'),
        spec("minimum-cost-grid-path", "Minimum-Cost Grid Path", "dynamic programming", "Classical grid dynamic programming recurrence", TEXTBOOK_URL, added, MINIMUM_COST_GRID_PATH, packed(matrix(6, 239, 1, 20)), packed(matrix(20, 240, 1, 20)), "            if row == 0 and column == 0:\n", '{"column": column, "columns": columns, "dp": dp, "grid": grid, "row": row, "rows": rows}', '    print(json.dumps({"minimum_cost": dp[-1][-1]}, separators=(",", ":")))\n', '{"columns": columns, "dp": dp, "grid": grid, "rows": rows}'),
        spec("optimal-binary-search-tree", "Optimal Binary Search Tree", "dynamic programming", "Introduction to Algorithms, optimal binary search trees", TEXTBOOK_URL, added, OPTIMAL_BINARY_SEARCH_TREE, packed([7, 3, 11, 5, 13, 2, 17, 9]), packed([random.Random(241 + index).randint(1, 30) for index in range(24)]), "                candidate = total\n", '{"candidate_root": candidate_root, "cost": cost, "frequencies": frequencies, "left": left, "length": length, "right": right, "root": root, "total": total}', '    print(json.dumps({"minimum_cost": cost[0][n - 1]}, separators=(",", ":")))\n', '{"cost": cost, "frequencies": frequencies, "root": root}'),
        spec("egg-dropping", "Egg Dropping", "dynamic programming", "Classical egg-dropping dynamic programming recurrence", TEXTBOOK_URL, added, EGG_DROPPING, "3 14\n", "5 45\n", "                candidate = 1 + max(dp[egg - 1][drop - 1], dp[egg][floor - drop])\n", '{"candidate": dp[egg][floor], "choice": choice, "dp": dp, "drop": drop, "egg": egg, "eggs": eggs, "floor": floor, "floors": floors}', '    print(json.dumps({"minimum_trials": dp[eggs][floors]}, separators=(",", ":")))\n', '{"choice": choice, "dp": dp, "eggs": eggs, "floors": floors}'),
        spec("dijkstra", "Dijkstra Shortest Paths", "graph", "Dijkstra, A Note on Two Problems in Connexion with Graphs", "https://doi.org/10.1007/BF01386390", added, DIJKSTRA, packed({"nodes": 10, "source": 0, "edges": connected_graph(10, 22, 213, False)}), packed({"nodes": 34, "source": 0, "edges": connected_graph(34, 180, 214, False)}), "            candidate = distance + weight\n", '{"adjacency": adjacency, "candidate": distance, "dist": dist, "distance": distance, "neighbor": neighbor, "node": node, "parent": parent, "queue": queue, "visited": visited, "weight": weight}', '    print(json.dumps({"distances": dist}, separators=(",", ":")))\n', '{"dist": dist, "parent": parent, "visited": visited}'),
        spec("bellman-ford", "Bellman-Ford Shortest Paths", "graph", "Bellman, On a Routing Problem", "https://doi.org/10.1090/S0002-9939-1958-0102435-2", added, BELLMAN_FORD, packed({"nodes": 10, "source": 0, "edges": bellman_simple}), packed({"nodes": 32, "source": 0, "edges": bellman_hard}), "            if dist[left] != infinity and dist[left] + weight < dist[right]:\n", '{"changed": changed, "dist": dist, "edges": edges, "left": left, "parent": parent, "pass_index": pass_index, "right": right, "weight": weight}', '    print(json.dumps({"distances": dist}, separators=(",", ":")))\n', '{"dist": dist, "edges": edges, "parent": parent}'),
        spec("prim", "Prim Minimum Spanning Tree", "graph", "Prim, Shortest Connection Networks and Some Generalizations", "https://doi.org/10.1002/j.1538-7305.1957.tb01515.x", added, PRIM, packed(mst_matrix(8, 215)), packed(mst_matrix(26, 216)), "            weight = matrix[node][neighbor]\n", '{"in_tree": in_tree, "key": key, "matrix": matrix, "neighbor": neighbor, "node": node, "parent": parent, "step": step}', '    print(json.dumps({"weight": sum(key)}, separators=(",", ":")))\n', '{"in_tree": in_tree, "key": key, "matrix": matrix, "parent": parent}'),
        spec("kruskal", "Kruskal Minimum Spanning Tree", "graph", "Kruskal, On the Shortest Spanning Subtree of a Graph", "https://doi.org/10.1090/S0002-9939-1956-0078686-7", added, KRUSKAL, packed({"nodes": 10, "edges": connected_graph(10, 25, 217, False)}), packed({"nodes": 36, "edges": connected_graph(36, 220, 218, False)}), "        left_root = find(left)\n", '{"edges": edges, "left": left, "parent": parent, "rank": rank, "right": right, "selected": selected, "total": total, "weight": weight}', '    print(json.dumps({"weight": total}, separators=(",", ":")))\n', '{"parent": parent, "rank": rank, "selected": selected, "total": total}'),
        spec("kahn-topological-sort", "Kahn Topological Sort", "graph", "Kahn, Topological Sorting of Large Networks", "https://doi.org/10.1145/368996.369025", added, KAHN_TOPOLOGICAL_SORT, packed({"nodes": 12, "edges": dag(12, 24, 219)}), packed({"nodes": 55, "edges": dag(55, 260, 220)}), "            indegree[neighbor] -= 1\n", '{"adjacency": adjacency, "indegree": indegree, "neighbor": neighbor, "node": node, "order": order, "queue": queue}', "    print(json.dumps(order, separators=(\",\", \":\")))\n", '{"indegree": indegree, "order": order, "queue": queue}'),
        spec("merge-sort", "Bottom-Up Merge Sort", "sorting", "Introduction to Algorithms, merge sort", TEXTBOOK_URL, added, MERGE_SORT, packed([random.Random(221 + index).randint(-500, 500) for index in range(32)]), packed([random.Random(253 + index).randint(-5000, 5000) for index in range(256)]), "                if left < middle and (right >= end or values[left] <= values[right]):\n", '{"buffer": buffer, "end": end, "left": left, "middle": middle, "right": right, "start": start, "target": target, "values": values, "width": width}', "    print(json.dumps(values, separators=(\",\", \":\")))\n", '{"buffer": buffer, "values": values, "width": width}'),
        spec("heap-sort", "Heap Sort", "sorting", "Williams, Algorithm 232: Heapsort", "https://doi.org/10.1145/512274.512284", added, HEAP_SORT, packed([random.Random(222 + index).randint(-500, 500) for index in range(32)]), packed([random.Random(254 + index).randint(-5000, 5000) for index in range(256)]), "        sift_down(0, end)\n", '{"end": end, "n": n, "values": values}', "    print(json.dumps(values, separators=(\",\", \":\")))\n", '{"n": n, "values": values}'),
        spec("rabin-karp", "Rabin-Karp String Matching", "string", "Karp and Rabin, Efficient Randomized Pattern-Matching Algorithms", "https://doi.org/10.1147/rd.312.0249", added, RABIN_KARP, text_with_pattern(70, "abcab", (15,), 223) + "\nabcab\n", text_with_pattern(320, "abacabadabacaba", (45, 250), 224) + "\nabacabadabacaba\n", "        if window_hash == pattern_hash and text[start:start + length] == pattern:\n", '{"matches": matches, "pattern": pattern, "pattern_hash": pattern_hash, "start": start, "text": text, "window_hash": window_hash}', '    print(json.dumps(matches, separators=(",", ":")))\n', '{"matches": matches, "pattern": pattern, "pattern_hash": pattern_hash, "text": text, "window_hash": window_hash}'),
        spec("z-algorithm", "Z Algorithm", "string", "Gusfield, Algorithms on Strings, Trees, and Sequences", "https://doi.org/10.1017/CBO9780511574931", added, Z_ALGORITHM, random_text(70, 225, "abc") + "\n", random_text(320, 226, "abc") + "\n", "        if index <= right:\n", '{"index": index, "left": left, "right": right, "text": text, "z": z}', '    print(json.dumps(z, separators=(",", ":")))\n', '{"left": left, "right": right, "text": text, "z": z}'),
        spec("andrew-monotone-chain", "Andrew Monotone Chain Convex Hull", "computational geometry", "Andrew, Another Efficient Algorithm for Convex Hulls in Two Dimensions", "https://doi.org/10.1016/0020-0190(79)90072-3", added, MONOTONE_CHAIN, packed(points(30, 227)), packed(points(220, 228)), "        while len(lower) >= 2 and cross(lower[-2], lower[-1], point) <= 0:\n", '{"lower": lower, "point": point, "points": points}', '    print(json.dumps(hull, separators=(",", ":")))\n', '{"hull": hull, "lower": lower, "points": points, "upper": upper}'),
    )


SPECS = make_specs()
