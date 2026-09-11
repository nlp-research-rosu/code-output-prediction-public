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
| inside-loop-state | (0.41, p 0.7954) | (0.12, p 0.8876) | (0.43, p 0.7456) | (0.50, p 0.5061) | (0.17, p 0.9923) | (0.43, p 0.7577) | — (0/35 correct) |
| long-trace-final | (0.66, p 0.0602) | (0.75, p 0.0602) | (0.63, p 0.1108) | (0.55, p 0.3344) | (0.52, p 0.4265) | (0.61, p 0.1358) | (0.79, p 0.0601) |
| post-loop-state | (0.45, p 0.6906) | (0.65, p 0.4097) | (0.35, p 0.9270) | (0.43, p 0.7609) | (0.34, p 0.8898) | (0.54, p 0.3600) | — (0/35 correct) |
| short-trace-final | — (35/35 correct) | (0.06, p 0.9400) | (0.91, p 0.1180) | (0.94, p 0.0859) | (0.63, p 0.1185) | (0.31, p 0.9110) | (0.47, p 0.5755) |
