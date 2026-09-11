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
| inside-loop-state | (0.67, p 0.0553) | — (0/30 correct) | (0.36, p 0.8880) | (0.40, p 0.8297) | — (0/30 correct) | (0.24, p 0.8323) | — (0/30 correct) |
| long-trace-final | (0.31, p 0.8592) | (0.46, p 0.6386) | (0.53, p 0.4029) | (0.17, p 0.9752) | (0.40, p 0.7950) | (0.42, p 0.7355) | (0.46, p 0.6357) |
| post-loop-state | (0.41, p 0.7517) | (0.24, p 0.8312) | (0.40, p 0.8335) | (0.42, p 0.7451) | (0.23, p 0.8975) | (0.09, p 0.9315) | — (0/30 correct) |
| short-trace-final | — (30/30 correct) | (0.39, p 0.8061) | (0.75, p 0.0525) | — (30/30 correct) | (0.41, p 0.8049) | (0.61, p 0.2601) | (0.83, p 0.0843) |
