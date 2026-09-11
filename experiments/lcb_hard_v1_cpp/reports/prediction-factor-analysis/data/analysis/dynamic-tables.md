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
| all-arms | (0.70, p 0.0003) | (0.44, p 0.7033) | (0.67, p 0.0004) | (0.68, p 0.0011) | (0.62, p 0.0237) | (0.70, p < 0.0001) | (0.67, p 0.0836) |

## `Omega_hat_StateLoad`

Reachable runtime value cells summed over every state observation in the run.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-arms | (0.59, p 0.0517) | (0.52, p 0.4160) | (0.61, p 0.0156) | (0.54, p 0.2490) | (0.56, p 0.1647) | (0.64, p 0.0022) | (0.53, p 0.4034) |

## `Omega_hat_StateSize`

Greatest number of runtime value cells reachable from live program variables at one observation point.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| all-arms | (0.45, p 0.8248) | (0.52, p 0.4143) | (0.47, p 0.6976) | (0.44, p 0.8632) | (0.51, p 0.3989) | (0.49, p 0.5711) | (0.32, p 0.9338) |
