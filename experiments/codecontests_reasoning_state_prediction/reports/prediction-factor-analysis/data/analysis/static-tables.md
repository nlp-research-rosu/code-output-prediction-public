# Static factor association tables

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

## `Omega_CC`

Independent control-flow paths in the source.

| Arm group | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | (0.71, p 0.0897) | — (0/22 correct) | (0.54, p 0.3834) | (0.71, p 0.0939) | — (0/21 correct) | (0.63, p 0.1734) | — (0/22 correct) |
| long-trace-final | (0.28, p 0.9303) | (0.51, p 0.4859) | (0.38, p 0.8284) | (0.40, p 0.7706) | (0.56, p 0.3757) | (0.57, p 0.3160) | (0.55, p 0.3991) |
| post-loop-state | (0.76, p 0.0321) | — (0/22 correct) | (0.71, p 0.0596) | (0.61, p 0.2401) | (0.68, p 0.1446) | (0.72, p 0.0444) | — (0/22 correct) |
| short-trace-final | — (22/22 correct) | (0.40, p 0.7019) | (0.22, p 0.9357) | — (22/22 correct) | (0.78, p 0.0362) | (0.38, p 0.8101) | (0.37, p 0.7838) |
