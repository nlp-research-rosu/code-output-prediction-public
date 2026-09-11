# Logistic regressions

Each section asks how the odds of `wrong=1` change when the named
metric doubles. `OR` is that multiplier: above 1 means greater error
odds at larger values. The 95% interval and two-sided p-value come
from the standard maximum-likelihood logistic model. These are
associations, not causal effects, and p-values are not adjusted for
multiple testing.

## `Omega_hat_StateLoad` — all-arms

Included arms: `short-trace-final`, `long-trace-final`, `inside-loop-state`, `post-loop-state`.

`n` counts the pooled `(metric value, wrong-or-correct)` points
included in this regression. Arms are not separate statistical
groups; `arm_id` remains only for auditing the selected points.

| Model | n | Wrong | OR per doubling (95% CI) | p |
| --- | ---: | ---: | ---: | ---: |
| `deepseek-v4-pro-0813-high` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
| `deepseek-v4-pro-0813-off` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
| `glm-5.3-high` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
| `gpt-5.6-sol-high` | 120 | 114 | 3.28 (1.28–8.40) | 0.0133 |
| `gpt-5.6-sol-off` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
| `qwen3.8-27b-high` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
| `qwen3.8-27b-off` | 120 | 120 | NOT_ESTIMATED | NOT_ESTIMATED |
