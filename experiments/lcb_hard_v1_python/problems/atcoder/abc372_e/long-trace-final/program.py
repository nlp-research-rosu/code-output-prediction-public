import sys
sys.setrecursionlimit(1 << 25)

def main():
    import sys
    input = sys.stdin.read
    data = input().split()
    idx = 0
    N = int(data[idx])
    idx += 1
    Q = int(data[idx])
    idx += 1
    parent = list(range(N + 1))
    size = [1] * (N + 1)
    top_list = [[i] for i in range(N + 1)]

    def find(u):
        while parent[u] != u:
            parent[u] = parent[parent[u]]
            u = parent[u]
        return u

    def merge_lists(a, b):
        res = []
        i = j = 0
        while i < len(a) and j < len(b) and (len(res) < 10):
            if a[i] > b[j]:
                res.append(a[i])
                i += 1
            else:
                res.append(b[j])
                j += 1
        while i < len(a) and len(res) < 10:
            res.append(a[i])
            i += 1
        while j < len(b) and len(res) < 10:
            res.append(b[j])
            j += 1
        return res
    output = []
    for _ in range(Q):
        if idx >= len(data):
            break
        query_type = int(data[idx])
        idx += 1
        if query_type == 1:
            u = int(data[idx])
            idx += 1
            v = int(data[idx])
            idx += 1
            root_u = find(u)
            root_v = find(v)
            if root_u != root_v:
                if size[root_u] > size[root_v]:
                    root_u, root_v = (root_v, root_u)
                new_top = merge_lists(top_list[root_u], top_list[root_v])
                top_list[root_v] = new_top
                size[root_v] += size[root_u]
                parent[root_u] = root_v
        else:
            v = int(data[idx])
            idx += 1
            k = int(data[idx])
            idx += 1
            root = find(v)
            if size[root] < k:
                output.append('-1')
            else:
                output.append(str(top_list[root][k - 1]))
    print('\n'.join(output))
if __name__ == '__main__':
    main()
