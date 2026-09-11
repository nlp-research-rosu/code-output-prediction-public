# Metric support matrix

One row is one measured factor and one column is one model. Every
computed cell explicitly reports `theta`, `p`, and `n`:

- `theta`: how often a failed prediction had the larger value, ties
  counting half. `0.5` means no ordering tendency; values below `0.5`
  mean failures had smaller values.
- `p`: the one-sided permutation p-value. `< 0.0001` is the floor for
  10,000 shuffles and means no shuffle reached the observed separation.
- `n=measured/eligible`: predictions carrying this metric divided by all
  gradable predictions for that model and group. When no cohort manifest
  supplies the denominator, the cell shows measured `n` only. Here, a
  measured point carries one numeric value for the metric.

`n` counts prediction rows, not distinct programs or executions. Several
predictions may share one execution measurement. Different `n` values
mean the cells analyze different measured subsets; missing measurements
and ungradable predictions are never converted to zero.

**Bold** marks the predeclared rule `theta_obs > 0.5` and unadjusted
`p_value < 0.05`. The `supported` column counts how many models met it,
which is the cross-model consistency of that factor. Rows are ordered by
that count, so the factors carrying the most evidence appear first.

A factor supported for one model out of 7 is weak evidence even when
its single p-value is small, because these p-values are unadjusted.
Read `theta_obs` for effect size and the `supported` count for
consistency; neither alone ranks a factor.

## dynamic: all-arms

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_hat_StateLoad` | **theta=0.70<br>p 0.0035<br>n=120/120** | **theta=0.70<br>p 0.0148<br>n=120/120** | **theta=0.67<br>p 0.0011<br>n=120/120** | **theta=0.71<br>p 0.0013<br>n=120/120** | **theta=0.74<br>p 0.0003<br>n=120/120** | **theta=0.88<br>p < 0.0001<br>n=120/120** | theta=0.48<br>p 0.5522<br>n=120/120 | 6/7 |
| `Omega_hat_StateSize` | **theta=0.73<br>p 0.0006<br>n=120/120** | **theta=0.69<br>p 0.0274<br>n=120/120** | **theta=0.65<br>p 0.0025<br>n=120/120** | **theta=0.72<br>p 0.0003<br>n=120/120** | **theta=0.67<br>p 0.0062<br>n=120/120** | **theta=0.80<br>p < 0.0001<br>n=120/120** | theta=0.51<br>p 0.4782<br>n=120/120 | 6/7 |
| `Omega_hat_NativeTrace` | theta=0.58<br>p 0.1317<br>n=120/120 | **theta=0.72<br>p 0.0086<br>n=120/120** | **theta=0.71<br>p < 0.0001<br>n=120/120** | **theta=0.71<br>p 0.0014<br>n=120/120** | **theta=0.78<br>p < 0.0001<br>n=120/120** | **theta=0.89<br>p < 0.0001<br>n=120/120** | theta=0.51<br>p 0.4674<br>n=120/120 | 5/7 |

- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.
- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.

## static: inside-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.67<br>p 0.0553<br>n=30/30 | — (0/30 correct) | theta=0.36<br>p 0.8880<br>n=30/30 | theta=0.40<br>p 0.8297<br>n=30/30 | — (0/30 correct) | theta=0.24<br>p 0.8323<br>n=30/30 | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: long-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.31<br>p 0.8592<br>n=30/30 | theta=0.46<br>p 0.6386<br>n=30/30 | theta=0.53<br>p 0.4029<br>n=30/30 | theta=0.17<br>p 0.9752<br>n=30/30 | theta=0.40<br>p 0.7950<br>n=30/30 | theta=0.42<br>p 0.7355<br>n=30/30 | theta=0.46<br>p 0.6357<br>n=30/30 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: post-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.41<br>p 0.7517<br>n=30/30 | theta=0.24<br>p 0.8312<br>n=30/30 | theta=0.40<br>p 0.8335<br>n=30/30 | theta=0.42<br>p 0.7451<br>n=30/30 | theta=0.23<br>p 0.8975<br>n=30/30 | theta=0.09<br>p 0.9315<br>n=30/30 | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: short-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (30/30 correct) | theta=0.39<br>p 0.8061<br>n=30/30 | theta=0.75<br>p 0.0525<br>n=30/30 | — (30/30 correct) | theta=0.41<br>p 0.8049<br>n=30/30 | theta=0.61<br>p 0.2601<br>n=30/30 | theta=0.83<br>p 0.0843<br>n=30/30 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.
