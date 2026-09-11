# Supported associations

Every statistical series meeting the predeclared rule `theta_obs > 0.5`
and unadjusted permutation `p_value < 0.05`, strongest ordering first.
This is the audit list behind the analysis report; read the report for
what it means and the metric support matrix for cross-model consistency.

A row here is one model, one arm group, and one metric. Support for
only one model is weak cross-model evidence even with a small p-value,
because these p-values are not corrected for multiple testing.

| Metric | Model | Arm group | theta_obs | p | Correct | Wrong | n |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `Omega_hat_NativeTrace` | `qwen3.8-27b-high` | all-arms | 0.89 | < 0.0001 | 36 | 84 | 120 |
| `Omega_hat_StateLoad` | `qwen3.8-27b-high` | all-arms | 0.88 | < 0.0001 | 36 | 84 | 120 |
| `Omega_hat_StateSize` | `qwen3.8-27b-high` | all-arms | 0.80 | < 0.0001 | 36 | 84 | 120 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-off` | all-arms | 0.78 | < 0.0001 | 24 | 96 | 120 |
| `Omega_hat_StateLoad` | `gpt-5.6-sol-off` | all-arms | 0.74 | 0.0003 | 24 | 96 | 120 |
| `Omega_hat_StateSize` | `deepseek-v4-pro-0813-high` | all-arms | 0.73 | 0.0006 | 100 | 20 | 120 |
| `Omega_hat_StateSize` | `gpt-5.6-sol-high` | all-arms | 0.72 | 0.0003 | 99 | 21 | 120 |
| `Omega_hat_NativeTrace` | `deepseek-v4-pro-0813-off` | all-arms | 0.72 | 0.0086 | 10 | 110 | 120 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-high` | all-arms | 0.71 | 0.0014 | 99 | 21 | 120 |
| `Omega_hat_NativeTrace` | `glm-5.3-high` | all-arms | 0.71 | < 0.0001 | 68 | 52 | 120 |
| `Omega_hat_StateLoad` | `gpt-5.6-sol-high` | all-arms | 0.71 | 0.0013 | 99 | 21 | 120 |
| `Omega_hat_StateLoad` | `deepseek-v4-pro-0813-off` | all-arms | 0.70 | 0.0148 | 10 | 110 | 120 |
| `Omega_hat_StateLoad` | `deepseek-v4-pro-0813-high` | all-arms | 0.70 | 0.0035 | 100 | 20 | 120 |
| `Omega_hat_StateSize` | `deepseek-v4-pro-0813-off` | all-arms | 0.69 | 0.0274 | 10 | 110 | 120 |
| `Omega_hat_StateLoad` | `glm-5.3-high` | all-arms | 0.67 | 0.0011 | 68 | 52 | 120 |
| `Omega_hat_StateSize` | `gpt-5.6-sol-off` | all-arms | 0.67 | 0.0062 | 24 | 96 | 120 |
| `Omega_hat_StateSize` | `glm-5.3-high` | all-arms | 0.65 | 0.0025 | 68 | 52 | 120 |

Column meanings:

- `theta_obs`: how often a failed prediction had the larger metric
  value than a successful one, ties counting half.
- `p`: share of 10,000 shuffled labelings at least as separated as
  the observed data. `< 0.0001` is the floor this many shuffles can
  reach and means no shuffle matched the observed separation.
- `Correct` / `Wrong`: predictions in the series carrying a numeric
  value for this metric. Predictions without a value are not counted.
- `n`: `Correct + Wrong`, the series denominator.

Full precision for every series, supported or not, is in
`series-results.csv`.
