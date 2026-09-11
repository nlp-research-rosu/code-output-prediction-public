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
| `deepseek-v4-pro-0813-high` | 140 | 38 | 1.04 (0.99–1.09) | 0.1066 |
| `deepseek-v4-pro-0813-off` | 140 | 133 | 1.00 (0.91–1.10) | 0.9556 |
| `glm-5.3-high` | 140 | 56 | 1.05 (1.00–1.10) | 0.0305 |
| `gpt-5.6-sol-high` | 140 | 34 | 1.02 (0.97–1.07) | 0.4035 |
| `gpt-5.6-sol-off` | 138 | 107 | 1.03 (0.98–1.08) | 0.2718 |
| `qwen3.8-27b-high` | 140 | 78 | 1.07 (1.02–1.12) | 0.0033 |
| `qwen3.8-27b-off` | 140 | 134 | 1.00 (0.90–1.10) | 0.9770 |
