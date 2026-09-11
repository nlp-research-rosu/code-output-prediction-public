# Dynamic metric measurement coverage

This table answers which program profiles actually carry each dynamic
metric before model outcomes are joined. Rows are experiment arms and
columns are metrics. Every cell is `measured / selected (coverage)` in
program profiles; it is not an accuracy, model-prediction, or execution
count.
Missing values are never treated as zero. The reason table below
separates an adapter that did not run from a measurement that failed.

| Arm | Omega_hat_NativeTrace | Omega_hat_StateSize | Omega_hat_StateLoad |
| --- | ---: | ---: | ---: |
| `short-trace-final` | 283 / 283 (100.0%) | 283 / 283 (100.0%) | 283 / 283 (100.0%) |
| `long-trace-final` | 283 / 283 (100.0%) | 283 / 283 (100.0%) | 283 / 283 (100.0%) |
| `inside-loop-state` | 283 / 283 (100.0%) | 283 / 283 (100.0%) | 283 / 283 (100.0%) |
| `post-loop-state` | 283 / 283 (100.0%) | 283 / 283 (100.0%) | 283 / 283 (100.0%) |

## Why measurements are unavailable

Rows below count unavailable program profiles, not model predictions.
`Affected arms` gives the profile count per arm. Prompt/instrumented
arms that reuse one execution are still separate profile rows here.

| Metric | Status or reason | Profiles | Affected arms | Meaning |
| --- | --- | ---: | --- | --- |

Metric meanings:

- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.
- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
