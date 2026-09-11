import sys
MOD = 998244353

def solve() -> None:
    data = sys.stdin.read().strip().split()
    if not data:
        return
    N = int(data[0])
    S = data[1]
    parent = [-1]
    children = [[]]
    stack = []
    for ch in S:
        if ch == '(':
            node = len(parent)
            parent.append(-1)
            children.append([])
            if stack:
                p = stack[-1]
                children[p].append(node)
                parent[node] = p
            else:
                children[0].append(node)
                parent[node] = 0
            stack.append(node)
        else:
            stack.pop()
    max_n = N
    fact = [1] * (max_n + 1)
    for i in range(2, max_n + 1):
        fact[i] = fact[i - 1] * i % MOD
    inv_fact = [1] * (max_n + 1)
    inv_fact[max_n] = pow(fact[max_n], MOD - 2, MOD)
    for i in range(max_n, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD
    hash_id = {}
    next_id = 1
    hash_of = [0] * len(parent)
    sys.setrecursionlimit(10000)
    answer = 1

    def dfs(v: int) -> None:
        nonlocal next_id, answer
        child_hashes = []
        for c in children[v]:
            dfs(c)
            child_hashes.append(hash_of[c])
        child_hashes.sort()
        i = 0
        while i < len(child_hashes):
            j = i
            while j < len(child_hashes) and child_hashes[j] == child_hashes[i]:
                j += 1
            cnt = j - i
            answer = answer * inv_fact[cnt] % MOD
            i = j
        answer = answer * fact[len(child_hashes)] % MOD
        tup = tuple(child_hashes)
        if tup not in hash_id:
            hash_id[tup] = next_id
            next_id += 1
        hash_of[v] = hash_id[tup]
    dfs(0)
    print(answer % MOD)
if __name__ == '__main__':
    solve()
