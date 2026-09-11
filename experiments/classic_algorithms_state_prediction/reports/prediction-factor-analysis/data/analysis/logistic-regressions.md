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
| `deepseek-v4-pro-0813-high` | 120 | 20 | 1.31 (1.07–1.59) | 0.0080 |
| `deepseek-v4-pro-0813-off` | 120 | 110 | 1.35 (1.07–1.70) | 0.0116 |
| `glm-5.3-high` | 120 | 52 | 1.28 (1.11–1.48) | 0.0007 |
| `gpt-5.6-sol-high` | 120 | 21 | 1.39 (1.13–1.72) | 0.0019 |
| `gpt-5.6-sol-off` | 120 | 96 | 1.40 (1.18–1.66) | 0.0001 |
| `qwen3.8-27b-high` | 120 | 84 | 2.06 (1.60–2.66) | < 0.0001 |
| `qwen3.8-27b-off` | 120 | 116 | 1.04 (0.75–1.44) | 0.8186 |
