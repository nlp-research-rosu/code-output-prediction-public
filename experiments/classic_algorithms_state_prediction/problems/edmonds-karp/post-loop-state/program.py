import json

def main():
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
    print(json.dumps({'adjacency': adjacency, 'edges': edges, 'flow': flow, 'sink': sink, 'source': source}, separators=(",", ":"), sort_keys=True))


if __name__ == "__main__":
    main()
