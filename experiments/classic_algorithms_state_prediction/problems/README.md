# Problem source and construction

All model-visible programs are repository-authored Python implementations. No
third-party source code is copied. The deterministic implementations and input
builders are in [`analysis/specs.py`](../analysis/specs.py). The literature
links identify algorithm definitions or textbook treatments, not copied source
bytes. Exact source, input, and oracle hashes are stored in
[`cases.json`](../cases.json).

The table enumerates all 30 cases. Each row is one program; Category describes
the algorithmic technique, Origin describes where this repository's code came
from, and Reference identifies the algorithm's published or textbook source.
There are no measurements, denominators, unavailable values, or model outcomes
in this table.

| Case | Category | Origin | Reference |
| --- | --- | --- | --- |
| Floyd-Warshall | Graph DP | Local implementation | [Floyd 1962](https://doi.org/10.1145/367766.368168) |
| Naive matrix multiplication | Numerical | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Discrete N-body simulation | Simulation | Local implementation | [Aarseth 2003](https://doi.org/10.1017/CBO9780511535246) |
| KMP | String | Local implementation | [Knuth, Morris, and Pratt 1977](https://doi.org/10.1137/0206024) |
| Longest common subsequence | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Matrix-chain multiplication | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Levenshtein edit distance | DP | Local implementation | [Wagner and Fischer 1974](https://doi.org/10.1145/321796.321811) |
| 0/1 knapsack | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Held-Karp TSP | Subset DP | Local implementation | [Held and Karp 1962](https://doi.org/10.1137/0110015) |
| Edmonds-Karp maximum flow | Graph | Local implementation | [Edmonds and Karp 1972](https://doi.org/10.1145/321694.321699) |
| Minimum coin change | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Rod cutting | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Longest increasing subsequence | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Weighted interval scheduling | DP | Local implementation | [Kleinberg and Tardos](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003259) |
| Longest palindromic subsequence | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Minimum palindrome partitioning | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Subset sum | DP | Local implementation | [Bellman 1957](https://press.princeton.edu/books/paperback/9780691146683/dynamic-programming) |
| Minimum-cost grid path | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Optimal binary search tree | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Egg dropping | DP | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Dijkstra shortest paths | Graph | Local implementation | [Dijkstra 1959](https://doi.org/10.1007/BF01386390) |
| Bellman-Ford shortest paths | Graph | Local implementation | [Bellman 1958](https://doi.org/10.1090/S0002-9939-1958-0102435-2) |
| Prim minimum spanning tree | Graph | Local implementation | [Prim 1957](https://doi.org/10.1002/j.1538-7305.1957.tb01515.x) |
| Kruskal minimum spanning tree | Graph | Local implementation | [Kruskal 1956](https://doi.org/10.1090/S0002-9939-1956-0078686-7) |
| Kahn topological sort | Graph | Local implementation | [Kahn 1962](https://doi.org/10.1145/368996.369025) |
| Bottom-up merge sort | Sorting | Local implementation | [CLRS](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) |
| Heap sort | Sorting | Local implementation | [Williams 1964](https://doi.org/10.1145/512274.512284) |
| Rabin-Karp | String | Local implementation | [Karp and Rabin 1987](https://doi.org/10.1147/rd.312.0249) |
| Z Algorithm | String | Local implementation | [Gusfield 1997](https://doi.org/10.1017/CBO9780511574931) |
| Andrew monotone chain | Computational geometry | Local implementation | [Andrew 1979](https://doi.org/10.1016/0020-0190(79)90072-3) |

## Input and checkpoint selection

Short- and long-trace inputs are deterministic fixtures produced from fixed seeds.
They change only problem size or workload, not the algorithm. The builder
counts executions of one declared core statement under both inputs and rejects
a case unless the hard count is larger. In the committed suite, hard counts
range from 220 to 5,317 executions and every hard/simple ratio exceeds 3.6.

The inside checkpoint is a deterministic execution of the selected core loop.
The post checkpoint is immediately after that same loop finishes normally.
Both checkpoints serialize the same ordered fields and types, chosen from the
algorithm's arrays, matrices, queues, graphs, and accumulators; at least one
core field must change between them.

## Four-arm construction

The table explains the source, input, and identity of every arm. It applies to
all 30 rows above.

| Arm | Source | Input | Target identity |
| --- | --- | --- | --- |
| `short-trace-final` | Clean | Short-trace | Final output |
| `long-trace-final` | Same clean bytes | Long-trace | Final output |
| `inside-loop-state` | State-output transformation | Long-trace | Selected-loop core state |
| `post-loop-state` | State-output transformation | Long-trace | Same projection after the loop |

Materialization runs each final and transformed program three times. It checks
deterministic output, checkpoint reachability, strict native-trace ordering,
same state schema, and a changed core state. It performs no model calls.
