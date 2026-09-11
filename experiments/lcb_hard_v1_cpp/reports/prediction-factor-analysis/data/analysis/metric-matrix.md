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
| `Omega_hat_NativeTrace` | **theta=0.70<br>p 0.0003<br>n=140/140** | theta=0.44<br>p 0.7033<br>n=140/140 | **theta=0.67<br>p 0.0004<br>n=140/140** | **theta=0.68<br>p 0.0011<br>n=140/140** | **theta=0.62<br>p 0.0237<br>n=138/138** | **theta=0.70<br>p < 0.0001<br>n=140/140** | theta=0.67<br>p 0.0836<br>n=140/140 | 5/7 |
| `Omega_hat_StateLoad` | theta=0.59<br>p 0.0517<br>n=140/140 | theta=0.52<br>p 0.4160<br>n=140/140 | **theta=0.61<br>p 0.0156<br>n=140/140** | theta=0.54<br>p 0.2490<br>n=140/140 | theta=0.56<br>p 0.1647<br>n=138/138 | **theta=0.64<br>p 0.0022<br>n=140/140** | theta=0.53<br>p 0.4034<br>n=140/140 | 2/7 |
| `Omega_hat_StateSize` | theta=0.45<br>p 0.8248<br>n=140/140 | theta=0.52<br>p 0.4143<br>n=140/140 | theta=0.47<br>p 0.6976<br>n=140/140 | theta=0.44<br>p 0.8632<br>n=140/140 | theta=0.51<br>p 0.3989<br>n=138/138 | theta=0.49<br>p 0.5711<br>n=140/140 | theta=0.32<br>p 0.9338<br>n=140/140 | 0/7 |

- `Omega_hat_NativeTrace`: target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.
- `Omega_hat_StateLoad`: reachable runtime value cells summed over every state observation in the run.
- `Omega_hat_StateSize`: greatest number of runtime value cells reachable from live program variables at one observation point.

## static: inside-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.41<br>p 0.7954<br>n=35/35 | theta=0.12<br>p 0.8876<br>n=35/35 | theta=0.43<br>p 0.7456<br>n=35/35 | theta=0.50<br>p 0.5061<br>n=35/35 | theta=0.17<br>p 0.9923<br>n=35/35 | theta=0.43<br>p 0.7577<br>n=35/35 | — (0/35 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: long-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.66<br>p 0.0602<br>n=35/35 | theta=0.75<br>p 0.0602<br>n=35/35 | theta=0.63<br>p 0.1108<br>n=35/35 | theta=0.55<br>p 0.3344<br>n=35/35 | theta=0.52<br>p 0.4265<br>n=34/34 | theta=0.61<br>p 0.1358<br>n=35/35 | theta=0.79<br>p 0.0601<br>n=35/35 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: post-loop-state

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | theta=0.45<br>p 0.6906<br>n=35/35 | theta=0.65<br>p 0.4097<br>n=35/35 | theta=0.35<br>p 0.9270<br>n=35/35 | theta=0.43<br>p 0.7609<br>n=35/35 | theta=0.34<br>p 0.8898<br>n=34/34 | theta=0.54<br>p 0.3600<br>n=35/35 | — (0/35 correct) | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.

## static: short-trace-final

| Metric | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off | supported |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| `Omega_CC` | — (35/35 correct) | theta=0.06<br>p 0.9400<br>n=35/35 | theta=0.91<br>p 0.1180<br>n=35/35 | theta=0.94<br>p 0.0859<br>n=35/35 | theta=0.63<br>p 0.1185<br>n=35/35 | theta=0.31<br>p 0.9110<br>n=35/35 | theta=0.47<br>p 0.5755<br>n=35/35 | 0/7 |

- `Omega_CC`: independent control-flow paths in the source.
