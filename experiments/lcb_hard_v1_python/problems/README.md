# Program source and arm construction

Benchmark items were selected from the Hard subset of
`livecodebench/code_generation_lite` at
revision `25d8cb8f0db2efe1b589941eb8c26a219850d4d2`. Selection was fixed before
model outcomes were inspected. Construction and determinism checks retained
318 of 350 candidate items. This experiment
keeps the remaining 283 Python cases; the 35 selected C++20 cases live in
[`lcb_hard_v1_cpp`](../../lcb_hard_v1_cpp/README.md).

Construction checks excluded `atcoder/abc329_e` because its checkpoint
state changes with Python's hash seed and `atcoder/abc375_g` because an unseeded
random modulus can change its answer or cause division by zero. These are task
construction failures, not exclusions based on model accuracy.

For every included program, the clean sources are byte-identical across the
two final-output arms, the exact short and long inputs have three stable
NativeTrace measurements with strict short < long ordering, and both state
arms use the long input. The inside checkpoint is within the selected loop;
the post checkpoint is immediately after that loop terminates normally. Both
emit canonical compact JSON with matching ordered fields and types, and at
least one core field changes.

[`cases.json`](../cases.json) records source and input hashes, selected-loop
anchors, checkpoints, field schemas, oracle hashes, exclusions, and validation
evidence. It also records the five case-specific serialization or control-flow
adjustments needed to keep checkpoint fields type-stable and reachable.
Instrumentation adds only deterministic observation and termination logic
before the checkpoint.

The exact evaluated implementations are supplied with this release. The pinned
dataset supplies problem metadata and tests; its card does not identify the
authorship of these solution implementations. See the repository
[third-party notices](../../../THIRD_PARTY_NOTICES.md) for the recorded source
and license scope.
