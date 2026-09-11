# Complexity measurements

These profiles cover the exact committed source and input for 30 problems and
all four arms: **120 profiles and 120 unique executions**. The current dataset
uses the repository's shared Python adapter, so its dynamic values can be
pooled with other Python benchmarks measured under the same convention.

Metric names, formulas, units, and interpretation are defined in the
[shared metric definitions](../../../../shared/metrics/README.md).
There is no combined complexity score.

## Coverage

| Metric | Measured | Unavailable |
| --- | ---: | ---: |
| `Omega_CC` | 120/120 | 0 |
| `Omega_hat_NativeTrace` | 120/120 | 0 |
| `Omega_hat_StateSize` | 40/120 | 80 |
| `Omega_hat_StateLoad` | 40/120 | 80 |

All 40 lower-cohort executions have exact StateSize and StateLoad values. The
80 medium- and higher-cohort executions reached the declared 50,000,000
semantic-cell traversal limit, so both state metrics remain `NOT_MEASURED`.
The limit controls measurement work; it is not a StateSize or StateLoad value
or lower bound. Partial observation rows are retained only as failure evidence.

## Method and files

[`measure_shared.py`](measure_shared.py) runs CPython 3.12.11 with NetworkX
3.4.2. NativeTrace counts target-frame CPython instruction events. StateSize
and StateLoad use the same complete, unsampled series at initialization,
post-mutation boundaries, and return or unwind. Each execution is measured
three times, the values must agree, and every natural and instrumented output
must match its committed oracle.

- [`measurements.csv`](measurements.csv) contains one row per execution;
- [`measurement-manifest.json`](measurement-manifest.json) records versions,
  methods, hashes, limits, repetitions, coverage, and unavailable causes;
- [`normalized-profiles.csv`](normalized-profiles.csv) is the shared long-form
  view for cross-benchmark analysis;
- [`raw-state-observations/`](raw-state-observations/) contains the compressed
  state-observation evidence for every repetition.

`measure.py` and `state_cells.c` are retained only to audit the older
benchmark-specific convention. They do not generate the current comparable
dataset.

```bash
COMPLEXITY_WORKERS=4 \
COMPLEXITY_TRACE_TIMEOUT_SECONDS=600 \
COMPLEXITY_STATE_CELL_VISIT_LIMIT=50000000 \
uv run --python 3.12.11 --with networkx==3.4.2 \
  python experiments/networkx_network_simplex_state_prediction/measurements/program-complexity/measure_shared.py
python3 shared/metrics/scripts/normalize_profiles.py --config experiments/networkx_network_simplex_state_prediction/measurements/program-complexity/normalized-profiles-config.json
```
