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
| `deepseek-v4-pro-0813-high` | 88 | 16 | 1.06 (1.00–1.13) | 0.0624 |
| `deepseek-v4-pro-0813-off` | 88 | 82 | 1.07 (0.98–1.17) | 0.1521 |
| `glm-5.3-high` | 88 | 34 | 1.03 (0.98–1.07) | 0.2755 |
| `gpt-5.6-sol-high` | 88 | 16 | 1.09 (1.02–1.16) | 0.0149 |
| `gpt-5.6-sol-off` | 86 | 73 | 1.04 (0.97–1.10) | 0.2764 |
| `qwen3.8-27b-high` | 86 | 46 | 1.03 (0.99–1.08) | 0.1455 |
| `qwen3.8-27b-off` | 88 | 81 | 1.06 (0.97–1.15) | 0.1929 |
