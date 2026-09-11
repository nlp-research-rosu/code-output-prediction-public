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
| `Omega_hat_NativeTrace` | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | **theta=0.84<br>p 0.0016<br>n=120/120** | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | 1/7 |
| `Omega_hat_StateLoad` | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | **theta=0.84<br>p 0.0013<br>n=120/120** | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | 1/7 |
| `Omega_hat_StateSize` | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | **theta=0.87<br>p 0.0009<br>n=120/120** | — (0/120 correct) | — (0/120 correct) | — (0/120 correct) | 1/7 |

- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.
- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.

## static: inside-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: long-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | theta=0.50<br>p 1.0000<br>n=30/30 | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: post-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: short-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | theta=0.50<br>p 1.0000<br>n=30/30 | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.
