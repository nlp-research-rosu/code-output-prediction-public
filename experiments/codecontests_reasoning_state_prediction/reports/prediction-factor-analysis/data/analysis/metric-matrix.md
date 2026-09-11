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
| `Omega_hat_NativeTrace` | **theta=0.77<br>p 0.0007<br>n=88/88** | theta=0.62<br>p 0.1807<br>n=88/88 | **theta=0.68<br>p 0.0017<br>n=88/88** | **theta=0.80<br>p < 0.0001<br>n=88/88** | theta=0.65<br>p 0.0501<br>n=86/86 | **theta=0.63<br>p 0.0151<br>n=86/86** | theta=0.58<br>p 0.2436<br>n=88/88 | 4/7 |
| `Omega_hat_StateLoad` | **theta=0.67<br>p 0.0163<br>n=88/88** | theta=0.66<br>p 0.1008<br>n=88/88 | theta=0.58<br>p 0.1248<br>n=88/88 | **theta=0.70<br>p 0.0060<br>n=88/88** | theta=0.58<br>p 0.1864<br>n=86/86 | theta=0.58<br>p 0.1003<br>n=86/86 | theta=0.61<br>p 0.1825<br>n=88/88 | 2/7 |
| `Omega_hat_StateSize` | theta=0.53<br>p 0.3701<br>n=88/88 | theta=0.63<br>p 0.1577<br>n=88/88 | theta=0.45<br>p 0.7740<br>n=88/88 | theta=0.54<br>p 0.3334<br>n=88/88 | theta=0.54<br>p 0.3306<br>n=86/86 | theta=0.51<br>p 0.4208<br>n=86/86 | theta=0.64<br>p 0.1178<br>n=88/88 | 0/7 |

- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.
- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.

## static: inside-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.71<br>p 0.0897<br>n=22/22 | — (0/22 correct) | theta=0.54<br>p 0.3834<br>n=22/22 | theta=0.71<br>p 0.0939<br>n=22/22 | — (0/21 correct) | theta=0.63<br>p 0.1734<br>n=21/21 | — (0/22 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: long-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.28<br>p 0.9303<br>n=22/22 | theta=0.51<br>p 0.4859<br>n=22/22 | theta=0.38<br>p 0.8284<br>n=22/22 | theta=0.40<br>p 0.7706<br>n=22/22 | theta=0.56<br>p 0.3757<br>n=22/22 | theta=0.57<br>p 0.3160<br>n=22/22 | theta=0.55<br>p 0.3991<br>n=22/22 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: post-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | **theta=0.76<br>p 0.0321<br>n=22/22** | — (0/22 correct) | theta=0.71<br>p 0.0596<br>n=22/22 | theta=0.61<br>p 0.2401<br>n=22/22 | theta=0.68<br>p 0.1446<br>n=21/21 | **theta=0.72<br>p 0.0444<br>n=21/21** | — (0/22 correct) | 2/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: short-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (22/22 correct) | theta=0.40<br>p 0.7019<br>n=22/22 | theta=0.22<br>p 0.9357<br>n=22/22 | — (22/22 correct) | **theta=0.78<br>p 0.0362<br>n=22/22** | theta=0.38<br>p 0.8101<br>n=22/22 | theta=0.37<br>p 0.7838<br>n=22/22 | 1/7 |

- `Omega_CC`: independent control-flow paths in the source.
