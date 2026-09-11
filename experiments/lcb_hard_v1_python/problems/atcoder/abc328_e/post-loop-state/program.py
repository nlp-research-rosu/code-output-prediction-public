import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
import itertools

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    M = int(data[1])
    K = int(data[2])
    edges = []
    index = 3
    for _ in range(M):
        u = int(data[index])
        v = int(data[index + 1])
        w = int(data[index + 2])
        edges.append((u, v, w))
        index += 3
    min_cost = K
    for edge_comb in itertools.combinations(edges, N - 1):
        parent = list(range(N + 1))

        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u

        def union(u, v):
            root_u = find(u)
            root_v = find(v)
            if root_u == root_v:
                return False
            parent[root_v] = root_u
            return True
        connected = True
        for u, v, _ in edge_comb:
            _lcb_count[0] += 1
            if not union(u, v):
                connected = False
                break
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'cost': cost, 'edge_comb': edge_comb, 'parent': parent, 'total_weight': total_weight, 'u': u, 'v': v}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
        if connected:
            total_weight = sum((w for _, _, w in edge_comb))
            cost = total_weight % K
            if cost < min_cost:
                min_cost = cost
    print(min_cost)
if __name__ == '__main__':
    main()
