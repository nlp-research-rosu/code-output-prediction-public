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
| inside-loop-state | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) |
| long-trace-final | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | (0.50, p 1.0000) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) |
| post-loop-state | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) |
| short-trace-final | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) | (0.50, p 1.0000) | — (0/30 correct) | — (0/30 correct) | — (0/30 correct) |
