# Dynamic factor association tables

Cells show `(theta_obs, p)` for one metric, arm, and model.

- `theta_obs`: how often a failed prediction has a larger metric value
  than a successful one, ties counting half. `0.5` means no ordering
  tendency; above `0.5` means failures had larger values.
- `p`: the share of 10,000 shuffled correct/wrong labelings that
  separated the two groups at least as much as the observed data.
  `< 0.0001` is the smallest value this many shuffles can produce and
  means no shuffle reached the observed separation.
- `— (k/n correct)`: every prediction in the series had the same
  outcome, so there is no failure-success pair to order and
  `theta_obs` does not exist. The score itself is a real result.
- `no data`: this model and arm produced no gradable prediction,
  either because it was never run or because every answer was
  ungradable. It is not a score of zero.

## `Omega_hat_NativeTrace`

Target-source native adapter events executed in one exact run. This measures execution length under that adapter, not time or source lines.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-arms | (0.77, p 0.0007) | (0.62, p 0.1807) | (0.68, p 0.0017) | (0.80, p < 0.0001) | (0.65, p 0.0501) | (0.63, p 0.0151) | (0.58, p 0.2436) |

## `Omega_hat_StateLoad`

Reachable runtime value cells summed over every state observation in the run.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-arms | (0.67, p 0.0163) | (0.66, p 0.1008) | (0.58, p 0.1248) | (0.70, p 0.0060) | (0.58, p 0.1864) | (0.58, p 0.1003) | (0.61, p 0.1825) |

## `Omega_hat_StateSize`

Greatest number of runtime value cells reachable from live program variables at one observation point.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-arms | (0.53, p 0.3701) | (0.63, p 0.1577) | (0.45, p 0.7740) | (0.54, p 0.3334) | (0.54, p 0.3306) | (0.51, p 0.4208) | (0.64, p 0.1178) |
