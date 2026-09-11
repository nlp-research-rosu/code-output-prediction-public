# Program complexity measurements

This package contains language-native profiles for the 35 C++20 cases across
all four canonical arms (140 source profiles and 140 execution identities).
Metric definitions, formulas, units, calculation, and interpretation live in
the [shared metric definitions](../../../../shared/metrics/README.md).

## Adapters and coverage

| Metric | Method | Measured execution profiles |
| --- | --- | ---: |
| `Omega_CC` | g++ macro expansion with external include bodies excluded, then Tree-sitter C++ control flow | 140/140 |
| `Omega_hat_NativeTrace` | Clang 18 coverage-region execution counts, three identical repetitions | 140/140 |
| `Omega_hat_StateSize` | Clang binding/container state observation, peak reachable value cells | 140/140 |
| `Omega_hat_StateLoad` | The same observation stream, summed across the execution | 140/140 |

The dynamic adapter uses the pinned `silkeh/clang` image, `gnu++20`, a
read-only repository mount, disabled network access, exact committed inputs,
and exact oracle comparison. The isolated build reads the pinned compilation
headers documented in [`support/README.md`](support/README.md); their bodies are
excluded from the measured target-source scope. The adapter also keeps standard
overloads visible in its private AST namespace, inserts its runtime header after
the first real include, and avoids non-constant guards inside `constexpr`
functions. All 140 execution profiles now have exact values for all three
runtime metrics.

<!-- dataset-complexity-summary:start -->
## Dataset median summary

All metric cells are medians. Dynamic metrics are marked with a hat.

| Dataset | #Programs | Omega_CC | Omega_hat_NativeTrace | Omega_hat_StateSize | Omega_hat_StateLoad |
| --- | --- | --- | --- | --- | --- |
| lcb_hard_v1_cpp (C++20) | 35 | 20 | 34.9K | 73.3K | 657M |

### Cohort

- **lcb_hard_v1_cpp (C++20)**: 35 unique programs; 140 unique dynamic executions. Static medians use one clean source per case. Dynamic medians use the four canonical execution identities per case when supported by the Clang adapter.

Metric names, units, and calculation follow the shared definitions linked
by this measurement package. `NOT_MEASURED` means unavailable, not zero.

Raw, unrounded medians are in `dataset-summary.csv`. Input hashes,
deduplication counts, and per-metric availability are in
`dataset-summary-manifest.json`.
<!-- dataset-complexity-summary:end -->

## Schema and identity

Authoritative records live in `<arm>/cpp/profiles.jsonl`; adjacent CSV files
are flat views. Each record pins exact source and input hashes, an execution
identity, metric methods, three per-repetition summaries, adapter/container
versions, and explicit limitations. Each arm manifest records selection,
coverage provenance, runtime versions, and all profile identities.
`normalized-profiles.csv` is the shared long-form view used to combine this
package with other benchmarks; it does not replace the authoritative JSONL.

C++ measurements are analyzed separately from Python because their static and
runtime events use language-specific conventions.

## Reproduce

```bash
for arm in short-trace-final long-trace-final inside-loop-state post-loop-state; do
  uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_cpp/analysis/requirements.txt python -m experiments.lcb_hard_v1_cpp.analysis.program_complexity run --benchmark experiments/lcb_hard_v1_cpp --arm "$arm" --language cpp --workers 2 --execution-timeout 180
done
python3 shared/metrics/scripts/summarize_dataset.py --config experiments/lcb_hard_v1_cpp/measurements/program-complexity/dataset-summary-config.json --output experiments/lcb_hard_v1_cpp/measurements/program-complexity --readme experiments/lcb_hard_v1_cpp/measurements/program-complexity/README.md
python3 shared/metrics/scripts/normalize_profiles.py --config experiments/lcb_hard_v1_cpp/measurements/program-complexity/normalized-profiles-config.json
```
