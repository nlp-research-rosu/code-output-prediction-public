import json as _lcb_json
import sys as _lcb_sys
_lcb_count = [0]
import sys
sys.setrecursionlimit(1 << 25)

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    N = int(data[0])
    edges = [[] for _ in range(N + 1)]
    index = 1
    for _ in range(N - 1):
        a = int(data[index])
        b = int(data[index + 1])
        edges[a].append(b)
        edges[b].append(a)
        index += 2
    C = list(map(int, data[index:index + N]))
    parent = [0] * (N + 1)
    children = [[] for _ in range(N + 1)]
    visited = [False] * (N + 1)

    def build_tree(u):
        visited[u] = True
        for v in edges[u]:
            if not visited[v]:
                parent[v] = u
                children[u].append(v)
                build_tree(v)
    build_tree(1)
    total_C = [0] * (N + 1)
    total_f = [0] * (N + 1)

    def post_order(u):
        total_C[u] = C[u - 1]
        total_f[u] = 0
        for v in children[u]:
            post_order(v)
            total_C[u] += total_C[v]
            total_f[u] += total_f[v] + total_C[v] * 1
    post_order(1)
    result = [0] * (N + 1)
    result[1] = total_f[1]

    def pre_order(u):
        for v in children[u]:
            _lcb_count[0] += 1
            result[v] = result[u] - total_C[v] + (total_C[1] - total_C[v])
            pre_order(v)
        if _lcb_count[0] > 1000:
            _lcb_sys.stdout.write(_lcb_json.dumps({'result': result, 'u': u}, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n')
            raise SystemExit
    pre_order(1)
    print(min(result[1:N + 1]))
if __name__ == '__main__':
    main()
