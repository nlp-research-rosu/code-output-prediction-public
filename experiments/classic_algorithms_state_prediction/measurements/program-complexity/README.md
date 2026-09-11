# Program complexity measurements

This package measures the exact Python source and source-input executions used
by the experiment. Static and dynamic profiles cover all four canonical arms.

The retained dimensions are `Omega_CC`, `Omega_hat_NativeTrace`,
`Omega_hat_StateSize`, and `Omega_hat_StateLoad`. A missing dynamic value is
written as `NOT_MEASURED`, never as zero. Raw compressed state-observation rows
and three-repetition provenance live under `raw-state-observations/`.

Metric names, formulas, units, calculation, and interpretation are defined in
the [shared metric definitions](../../../../shared/metrics/README.md).
This experiment uses the Python extended-decision convention, target-frame
CPython instruction events, and the shared Python reachable-value adapter.

`Omega_hat_NativeTrace` is available for 120/120 unique
executions. `Omega_hat_StateSize` and `Omega_hat_StateLoad` are available for
120/120. The unavailable executions are
; each exceeded the pinned 50,000,000 semantic-cell traversal
limit. One semantic-cell visit is one recursive inspection of a reachable
value. The counter accumulates over every state observation in one isolated
measurement repetition, so repeatedly observing a large container can exhaust
the budget even when no single state has 50,000,000 cells. The limit controls
measurement work; it is not a program metric, byte count, variable count, or
instruction count. No partial peak, sampled state series, or proxy value is
reported.

<!-- dataset-complexity-summary:start -->
<!-- dataset-complexity-summary:end -->

## Reproduce

```bash
uv run --python 3.12.11 python -m experiments.classic_algorithms_state_prediction.analysis.measure_complexity --workers 4 --execution-timeout 120 --state-cell-visit-limit 50000000
python3 shared/metrics/scripts/summarize_dataset.py --config experiments/classic_algorithms_state_prediction/measurements/program-complexity/dataset-summary-config.json --output experiments/classic_algorithms_state_prediction/measurements/program-complexity --readme experiments/classic_algorithms_state_prediction/measurements/program-complexity/README.md
```
