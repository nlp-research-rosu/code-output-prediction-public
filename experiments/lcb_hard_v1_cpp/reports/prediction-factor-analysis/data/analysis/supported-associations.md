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
| `Omega_hat_NativeTrace` | `qwen3.8-27b-high` | all-arms | 0.70 | < 0.0001 | 62 | 78 | 140 |
| `Omega_hat_NativeTrace` | `deepseek-v4-pro-0813-high` | all-arms | 0.70 | 0.0003 | 102 | 38 | 140 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-high` | all-arms | 0.68 | 0.0011 | 106 | 34 | 140 |
| `Omega_hat_NativeTrace` | `glm-5.3-high` | all-arms | 0.67 | 0.0004 | 84 | 56 | 140 |
| `Omega_hat_StateLoad` | `qwen3.8-27b-high` | all-arms | 0.64 | 0.0022 | 62 | 78 | 140 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-off` | all-arms | 0.62 | 0.0237 | 31 | 107 | 138 |
| `Omega_hat_StateLoad` | `glm-5.3-high` | all-arms | 0.61 | 0.0156 | 84 | 56 | 140 |

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
