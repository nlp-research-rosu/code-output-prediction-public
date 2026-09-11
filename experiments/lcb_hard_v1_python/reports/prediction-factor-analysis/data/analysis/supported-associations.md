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
| `Omega_hat_StateSize` | `qwen3.8-27b-high` | all-arms | 0.70 | < 0.0001 | 491 | 641 | 1132 |
| `Omega_hat_StateLoad` | `deepseek-v4-pro-0813-high` | all-arms | 0.69 | < 0.0001 | 746 | 386 | 1132 |
| `Omega_hat_StateLoad` | `qwen3.8-27b-high` | all-arms | 0.69 | < 0.0001 | 491 | 641 | 1132 |
| `Omega_hat_StateSize` | `deepseek-v4-pro-0813-high` | all-arms | 0.69 | < 0.0001 | 746 | 386 | 1132 |
| `Omega_hat_NativeTrace` | `qwen3.8-27b-high` | all-arms | 0.69 | < 0.0001 | 491 | 641 | 1132 |
| `Omega_hat_StateSize` | `glm-5.3-high` | all-arms | 0.69 | < 0.0001 | 679 | 453 | 1132 |
| `Omega_hat_StateLoad` | `glm-5.3-high` | all-arms | 0.68 | < 0.0001 | 679 | 453 | 1132 |
| `Omega_hat_NativeTrace` | `deepseek-v4-pro-0813-high` | all-arms | 0.68 | < 0.0001 | 746 | 386 | 1132 |
| `Omega_hat_StateSize` | `deepseek-v4-pro-0813-off` | all-arms | 0.67 | < 0.0001 | 115 | 1017 | 1132 |
| `Omega_hat_StateLoad` | `gpt-5.6-sol-high` | all-arms | 0.67 | < 0.0001 | 913 | 219 | 1132 |
| `Omega_hat_NativeTrace` | `glm-5.3-high` | all-arms | 0.67 | < 0.0001 | 679 | 453 | 1132 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-high` | all-arms | 0.66 | < 0.0001 | 913 | 219 | 1132 |
| `Omega_CC` | `gpt-5.6-sol-off` | inside-loop-state | 0.65 | 0.0056 | 25 | 243 | 268 |
| `Omega_hat_StateSize` | `gpt-5.6-sol-high` | all-arms | 0.65 | < 0.0001 | 913 | 219 | 1132 |
| `Omega_hat_StateLoad` | `deepseek-v4-pro-0813-off` | all-arms | 0.65 | < 0.0001 | 115 | 1017 | 1132 |
| `Omega_hat_NativeTrace` | `deepseek-v4-pro-0813-off` | all-arms | 0.64 | < 0.0001 | 115 | 1017 | 1132 |
| `Omega_CC` | `gpt-5.6-sol-off` | post-loop-state | 0.63 | 0.0052 | 34 | 225 | 259 |
| `Omega_hat_NativeTrace` | `gpt-5.6-sol-off` | all-arms | 0.62 | < 0.0001 | 324 | 765 | 1089 |
| `Omega_CC` | `qwen3.8-27b-high` | short-trace-final | 0.60 | 0.0413 | 257 | 26 | 283 |
| `Omega_hat_StateSize` | `gpt-5.6-sol-off` | all-arms | 0.60 | < 0.0001 | 324 | 765 | 1089 |
| `Omega_CC` | `qwen3.8-27b-high` | post-loop-state | 0.60 | 0.0238 | 38 | 245 | 283 |
| `Omega_hat_StateLoad` | `gpt-5.6-sol-off` | all-arms | 0.60 | < 0.0001 | 324 | 765 | 1089 |
| `Omega_CC` | `qwen3.8-27b-high` | inside-loop-state | 0.59 | 0.0222 | 47 | 236 | 283 |
| `Omega_hat_StateSize` | `qwen3.8-27b-off` | all-arms | 0.59 | 0.0020 | 84 | 1048 | 1132 |
| `Omega_CC` | `gpt-5.6-sol-high` | post-loop-state | 0.59 | 0.0086 | 195 | 88 | 283 |
| `Omega_CC` | `glm-5.3-high` | post-loop-state | 0.58 | 0.0139 | 98 | 185 | 283 |
| `Omega_CC` | `deepseek-v4-pro-0813-high` | post-loop-state | 0.57 | 0.0316 | 97 | 186 | 283 |
| `Omega_hat_StateLoad` | `qwen3.8-27b-off` | all-arms | 0.57 | 0.0201 | 84 | 1048 | 1132 |
| `Omega_CC` | `glm-5.3-high` | inside-loop-state | 0.56 | 0.0486 | 108 | 175 | 283 |

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
