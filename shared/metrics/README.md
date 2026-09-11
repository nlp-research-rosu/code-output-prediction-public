# Program-complexity metric definitions

This is the repository's single human-facing definition of the four retained
program-complexity metrics. Experiment reports link here instead of repeating
the definitions. Experiment measurement packages document only their selected
sources and inputs, language adapter, coverage, limits, and unavailable values.

## Notation

- `E` and `N` are the edges and nodes in one connected control-flow graph.
- `count(e)` is the number of times native event site `e` fires in one run.
- `S(t)` is the number of runtime value cells reachable from live,
  program-owned variables at state observation `t`.

Plain `Omega` describes exact source bytes. Hatted `Omega_hat` describes one
exact execution, identified by source, input, runtime or toolchain, flags, and
instrumentation convention. None of the four values is a universal difficulty
score, and they must not be added or collapsed into one score.

## Four-arm eligibility and coverage

For a canonical experiment, dynamic measurement starts from every exact
source-input execution referenced by all four canonical arms:
`short-trace-final`, `long-trace-final`, `inside-loop-state`, and
`post-loop-state`. Identical dynamic identities are measured once and joined
back to their arms. This deduplication does not remove an arm from the eligible
cohort.

Report `measured/eligible` separately for each metric. `eligible` is the number
of distinct four-arm execution identities in the declared measurement cohort;
`measured` is the subset with an exact numeric result from that metric's
adapter. Do not calculate coverage only over successful measurements or only
over the long-input arms.

## The four retained metrics

| Identifier | Full name | Calculation | Unit and interpretation |
| --- | --- | --- | --- |
| `Omega_CC` | Cyclomatic Complexity | `E - N + 2`, or the equivalent language-aware independent-decision count | Independent control-flow routes in the exact source. |
| `Omega_hat_NativeTrace` | Language-Native Execution Trace Length | `sum_e count(e)` | Adapter-defined target-source execution events in one exact run. It is execution length, not elapsed time. |
| `Omega_hat_StateSize` | Peak Reachable Program-State Size | `max_t S(t)` | Greatest reachable runtime value-cell count at one state observation. |
| `Omega_hat_StateLoad` | Cumulative Program-State Load | `sum_t S(t)` | Reachable runtime value-cell observations accumulated over the complete run. |

## How they are calculated

### `Omega_CC`

Parse the complete source shown to the model with a language-aware adapter,
build its control-flow graph, and calculate `E - N + 2`. The repository's
extended convention also counts independently evaluated Boolean terms as
decisions. The natural-language prompt is excluded. Reuse a value only for
byte-identical source measured with the same language and convention.

### `Omega_hat_NativeTrace`

Run the exact source and input with a reviewed language-native adapter and sum
the event counts inside the declared target-source scope. The Python adapter
counts target-frame CPython opcode events. The C/C++ adapter sums included
Clang coverage-region execution counts. Runtime libraries, dependencies,
wrappers, and instrumentation are excluded. Values from different languages,
runtime or compiler versions, flags, scopes, or adapter conventions are not
directly comparable.

The repository's normalized profile schema gives every benchmark the same
columns and status vocabulary. It does not convert values to a common numeric
scale. Pool raw values only when language, runtime or toolchain, included scope,
and adapter convention match.

### `Omega_hat_StateSize` and `Omega_hat_StateLoad`

Observe the exact run at every boundary declared by the language adapter. At
each observation, recursively count values reachable from live program-owned
variables:

- a scalar contributes one cell;
- a string, sequence, set, array, map, tuple, record, or object contributes one
  container or aggregate cell plus its included contents recursively;
- compound aliases are counted once per observation, and cycles stop at an
  already visited object;
- runtime internals, instrumentation, functions, classes, modules, allocator
  metadata, and unsupported opaque storage are excluded.

Use the same complete, unsampled `S(t)` series for both metrics. StateSize keeps
the maximum; StateLoad adds every observation. StateLoad is therefore not
`StateSize * NativeTrace`: a run may be long and narrow, short and wide, or vary
its state size over time.

The current Python adapter receives every target-frame opcode event for
NativeTrace, but it does **not** traverse the whole state after every opcode.
It records state at frame initialization, at the next opcode after an operation
that may mutate a binding or reachable value, at return, and at exceptional
unwind. This captures the completed mutation while avoiding repeated full-state
traversals after opcodes that cannot change the state. Its convention identifier
is `initial-next-opcode-mutation-boundary-return-v1`.

Each successful Python observation is stored in a compressed CSV row:

```text
event_index,event_kind,source_location,state_count,state_size
```

`event_index` is the zero-based observation number, not the opcode count.
`event_kind` is normally `initial`, `mutation_boundary`, `return`, or `unwind`.
`source_location` identifies the target source and current line. `state_count`
is the number of selected live roots and is diagnostic only. `state_size` is
`S(t)`. The profile records the raw artifact path and SHA-256, row count, and
the `event_index` where the maximum occurred. If traversal fails, the failure
metadata records its index, kind, location, type, and reason; no fabricated
`state_size` is written for that failed observation.

## Measurement procedure and unavailable values

For every dynamic metric, first run the uninstrumented program, then run the
instrumented measurement in isolation with the same source, input, runtime,
limits, and oracle. The measured run must terminate as expected and preserve
the observable result. Repeated deterministic runs must agree under the
declared repetition policy.

Return `NOT_MEASURED`, never zero or a proxy, for the exact metric when the adapter is unsupported,
instrumentation changes the result, an exact traversal cannot inspect a value,
the run is nondeterministic, or a declared time or work limit is exceeded.
Do not place a partial peak or sum in the exact metric field. For a timed run,
an experiment may separately retain the completed execution prefix as a
censored lower bound: `NativeTrace >= completed instructions`,
`StateSize >= observed peak`, and `StateLoad >= observed sum`. A failure in one
metric does not erase an independently valid metric from the same execution.

Normalized profiles use `MEASURED`, `LOWER_BOUND`, `NOT_MEASURED`, and
`NOT_REQUESTED`.
`MEASURED` carries an exact non-negative integer and no unavailable reason.
`LOWER_BOUND` carries a non-negative integer with an explicit `>=` relation.
`NOT_MEASURED` carries no numeric value and records the exact cause.
`NOT_REQUESTED` is distinct from a failed attempt. Experiment measurement
READMEs report per-metric coverage, limits, and unavailable causes for their
full four-arm cohort.
