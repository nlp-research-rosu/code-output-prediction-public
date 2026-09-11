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
| `deepseek-v4-pro-0813-high` | 1132 | 386 | 1.13 (1.10–1.15) | < 0.0001 |
| `deepseek-v4-pro-0813-off` | 1132 | 1017 | 1.10 (1.07–1.13) | < 0.0001 |
| `glm-5.3-high` | 1132 | 453 | 1.12 (1.10–1.15) | < 0.0001 |
| `gpt-5.6-sol-high` | 1132 | 219 | 1.11 (1.08–1.13) | < 0.0001 |
| `gpt-5.6-sol-off` | 1089 | 765 | 1.07 (1.05–1.10) | < 0.0001 |
| `qwen3.8-27b-high` | 1132 | 641 | 1.14 (1.12–1.17) | < 0.0001 |
| `qwen3.8-27b-off` | 1132 | 1048 | 1.05 (1.02–1.09) | 0.0029 |
