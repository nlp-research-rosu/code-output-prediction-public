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
| `Omega_hat_StateLoad` | **theta=0.69<br>p < 0.0001<br>n=1132/1132** | **theta=0.65<br>p < 0.0001<br>n=1132/1132** | **theta=0.68<br>p < 0.0001<br>n=1132/1132** | **theta=0.67<br>p < 0.0001<br>n=1132/1132** | **theta=0.60<br>p < 0.0001<br>n=1089/1089** | **theta=0.69<br>p < 0.0001<br>n=1132/1132** | **theta=0.57<br>p 0.0201<br>n=1132/1132** | 7/7 |
| `Omega_hat_StateSize` | **theta=0.69<br>p < 0.0001<br>n=1132/1132** | **theta=0.67<br>p < 0.0001<br>n=1132/1132** | **theta=0.69<br>p < 0.0001<br>n=1132/1132** | **theta=0.65<br>p < 0.0001<br>n=1132/1132** | **theta=0.60<br>p < 0.0001<br>n=1089/1089** | **theta=0.70<br>p < 0.0001<br>n=1132/1132** | **theta=0.59<br>p 0.0020<br>n=1132/1132** | 7/7 |
| `Omega_hat_NativeTrace` | **theta=0.68<br>p < 0.0001<br>n=1132/1132** | **theta=0.64<br>p < 0.0001<br>n=1132/1132** | **theta=0.67<br>p < 0.0001<br>n=1132/1132** | **theta=0.66<br>p < 0.0001<br>n=1132/1132** | **theta=0.62<br>p < 0.0001<br>n=1089/1089** | **theta=0.69<br>p < 0.0001<br>n=1132/1132** | theta=0.55<br>p 0.0553<br>n=1132/1132 | 6/7 |

- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.
- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.

## static: inside-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.55<br>p 0.0810<br>n=283/283 | — (0/283 correct) | **theta=0.56<br>p 0.0486<br>n=283/283** | theta=0.52<br>p 0.3310<br>n=283/283 | **theta=0.65<br>p 0.0056<br>n=268/268** | **theta=0.59<br>p 0.0222<br>n=283/283** | — (0/283 correct) | 3/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: long-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.51<br>p 0.3852<br>n=283/283 | theta=0.46<br>p 0.8094<br>n=283/283 | theta=0.48<br>p 0.7089<br>n=283/283 | theta=0.52<br>p 0.3331<br>n=283/283 | theta=0.46<br>p 0.8659<br>n=279/279 | theta=0.51<br>p 0.3623<br>n=283/283 | theta=0.48<br>p 0.6399<br>n=283/283 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: post-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | **theta=0.57<br>p 0.0316<br>n=283/283** | — (0/283 correct) | **theta=0.58<br>p 0.0139<br>n=283/283** | **theta=0.59<br>p 0.0086<br>n=283/283** | **theta=0.63<br>p 0.0052<br>n=259/259** | **theta=0.60<br>p 0.0238<br>n=283/283** | — (0/283 correct) | 5/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: short-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.49<br>p 0.5414<br>n=283/283 | theta=0.43<br>p 0.9504<br>n=283/283 | theta=0.55<br>p 0.2605<br>n=283/283 | theta=0.23<br>p 0.8021<br>n=283/283 | theta=0.41<br>p 0.9962<br>n=283/283 | **theta=0.60<br>p 0.0413<br>n=283/283** | theta=0.53<br>p 0.2735<br>n=283/283 | 1/7 |

- `Omega_CC`: independent control-flow paths in the source.
