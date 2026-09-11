import json


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
