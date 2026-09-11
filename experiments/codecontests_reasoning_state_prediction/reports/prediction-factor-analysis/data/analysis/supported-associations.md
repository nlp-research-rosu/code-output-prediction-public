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
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-high` | all-arms | 0.80 | < 0.0001 | 72 | 16 | 88 |
| `Omega_CC` | `gpt-5.6-sol-off` | short-trace-final | 0.78 | 0.0362 | 5 | 17 | 22 |
| `Omega_hat_NativeTrace` | `deepseek-v4-pro-0813-high` | all-arms | 0.77 | 0.0007 | 72 | 16 | 88 |
| `Omega_CC` | `deepseek-v4-pro-0813-high` | post-loop-state | 0.76 | 0.0321 | 16 | 6 | 22 |
| `Omega_CC` | `qwen3.8-27b-high` | post-loop-state | 0.72 | 0.0444 | 10 | 11 | 21 |
| `Omega_hat_StateLoad` | `gpt-5.6-sol-high` | all-arms | 0.70 | 0.0060 | 72 | 16 | 88 |
| `Omega_hat_NativeTrace` | `glm-5.3-high` | all-arms | 0.68 | 0.0017 | 54 | 34 | 88 |
| `Omega_hat_StateLoad` | `deepseek-v4-pro-0813-high` | all-arms | 0.67 | 0.0163 | 72 | 16 | 88 |
| `Omega_hat_NativeTrace` | `qwen3.8-27b-high` | all-arms | 0.63 | 0.0151 | 40 | 46 | 86 |

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
