# Problem source and arm construction

The executable algorithm comes from NetworkX `network_simplex` 3.4.2 at
commit `2acf1590f82757c01a57b81b8c5dfb79e60aa416`. The upstream
`networkx/algorithms/flow/networksimplex.py` file has SHA-256
`df6b9eb686568feffb28f3b6389a6eb4fd05a53aec43fa89c67b42f17c4856bd`.
NetworkX uses the BSD-3-Clause license; the notice is in
[`LICENSE-NETWORKX.txt`](LICENSE-NETWORKX.txt).

`analysis/materialize.py` removes documentation, examples, and the dispatch
decorator, renames the copied entry point, and adds a JSON input/final-cost
wrapper. The two final arms keep that algorithm clean. The state arms add only
the requested checkpoint output and stop.

## Selection

Selection was fixed before model evaluation. The builder exhaustively checked
1,000 capacity/weight assignments for each of 30 topology seeds in each
cohort: **90,000 candidate graphs**. For every selected topology, the short arm
uses the minimum-pivot candidate and the other three arms use the maximum-pivot
candidate.

| Cohort | Problems | Graph size | Short rule | Long rule | Inside checkpoint |
| --- | ---: | --- | --- | --- | ---: |
| lower | 10 | 14 nodes, 88 edges | at most 55 pivots | at least 110 pivots and 2.0x simple | 100 |
| medium | 10 | 22 nodes, 171 edges | at most 130 pivots | at least 210 pivots and 1.6x simple | 190 |
| higher | 10 | 32 nodes, 311 edges | at most 270 pivots | at least 400 pivots and 1.45x simple | 360 |

The cohorts use disjoint topology-seed ranges: 1-30, 101-130, and 201-230.
The builder retained the first 10 qualifying topologies in each range. Within
one problem, topology and graph size stay fixed while capacities and weights
change between the short- and long-trace inputs.

## Four arms

Every problem has `short-trace-final`, `long-trace-final`,
`inside-loop-state`, and `post-loop-state`. Both state arms serialize the full
`node_potentials` vector as canonical JSON: the inside arm stops at its cohort
pivot checkpoint, while the post arm stops immediately after the same pivot
loop finishes. At least one vector value changes.

[`cases.json`](../cases.json) records all selected seeds, hashes, pivot counts,
targets, inputs, checkpoints, and validation evidence for the 120 tasks.
