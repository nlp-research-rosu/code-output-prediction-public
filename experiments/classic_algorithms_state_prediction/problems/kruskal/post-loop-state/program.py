import json


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
    print(json.dumps({'parent': parent, 'rank': rank, 'selected': selected, 'total': total}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
