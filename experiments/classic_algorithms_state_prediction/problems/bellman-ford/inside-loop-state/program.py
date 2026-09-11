import json


def main():
    __target_count = 0
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
            __target_count += 1
            if __target_count == 884:
                print(json.dumps({'dist': dist, 'edges': edges, 'parent': parent}, separators=(",", ":"), sort_keys=True))
                return
            if dist[left] != infinity and dist[left] + weight < dist[right]:
                dist[right] = dist[left] + weight
                parent[right] = left
                changed = True
        if not changed:
            break
    print(json.dumps({"distances": dist}, separators=(",", ":")))


if __name__ == "__main__":
    main()
