# Overall accuracy

Predictions are deduplicated by `prediction_id` before counting.
Each cell shows `correct/eligible (accuracy)` for one arm and model.

Eligible counts differ between arms because ungradable answers are
excluded, so a difference between two cells in the same column mixes
an arm effect with a coverage difference. Compare arms within a model
using `matched-accuracy.md`, which holds the program set fixed.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 152/283 (53.7%) | 0/283 (0.0%) | 108/283 (38.2%) | 200/283 (70.7%) | 25/268 (9.3%) | 47/283 (16.6%) | 0/283 (0.0%) |
| long-trace-final | 218/283 (77.0%) | 49/283 (17.3%) | 203/283 (71.7%) | 236/283 (83.4%) | 112/279 (40.1%) | 149/283 (52.7%) | 44/283 (15.5%) |
| post-loop-state | 97/283 (34.3%) | 0/283 (0.0%) | 98/283 (34.6%) | 195/283 (68.9%) | 34/259 (13.1%) | 38/283 (13.4%) | 0/283 (0.0%) |
| short-trace-final | 279/283 (98.6%) | 66/283 (23.3%) | 270/283 (95.4%) | 282/283 (99.6%) | 153/283 (54.1%) | 257/283 (90.8%) | 40/283 (14.1%) |

## What these denominators leave out

A prediction counts only when the model returned an answer that could
be graded. Records below are excluded from every cell above: they are
**not** counted as wrong, so each denominator is smaller than the arm's
problem count.

| Model | `no_response` | total excluded |
| --- | ---: | ---: |
| `gpt-5.6-sol-off` | 43 | 43 |

Meaning of each cause:

- `no_response`: sent, but the model returned no gradable answer.

Excluding a `no_response` record is optimistic for a model that used
its whole token budget without answering: that failure is removed
rather than counted against it. Excluding a provider or transport
failure is correct, because it measures the provider, not the model.
The per-arm split is in `cohort-manifest.json`.
