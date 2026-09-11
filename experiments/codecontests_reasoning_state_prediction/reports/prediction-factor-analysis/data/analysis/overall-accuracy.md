# Overall accuracy

Predictions are deduplicated by `prediction_id` before counting.
Each cell shows `correct/eligible (accuracy)` for one arm and model.

Eligible counts differ between arms because ungradable answers are
excluded, so a difference between two cells in the same column mixes
an arm effect with a coverage difference. Compare arms within a model
using `matched-accuracy.md`, which holds the program set fixed.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 17/22 (77.3%) | 0/22 (0.0%) | 12/22 (54.5%) | 17/22 (77.3%) | 0/21 (0.0%) | 8/21 (38.1%) | 0/22 (0.0%) |
| long-trace-final | 17/22 (77.3%) | 3/22 (13.6%) | 14/22 (63.6%) | 16/22 (72.7%) | 4/22 (18.2%) | 7/22 (31.8%) | 3/22 (13.6%) |
| post-loop-state | 16/22 (72.7%) | 0/22 (0.0%) | 9/22 (40.9%) | 17/22 (77.3%) | 4/21 (19.0%) | 10/21 (47.6%) | 0/22 (0.0%) |
| short-trace-final | 22/22 (100.0%) | 3/22 (13.6%) | 19/22 (86.4%) | 22/22 (100.0%) | 5/22 (22.7%) | 15/22 (68.2%) | 4/22 (18.2%) |

## What these denominators leave out

A prediction counts only when the model returned an answer that could
be graded. Records below are excluded from every cell above: they are
**not** counted as wrong, so each denominator is smaller than the arm's
problem count.

| Model | `no_response` | total excluded |
| --- | ---: | ---: |
| `gpt-5.6-sol-off` | 2 | 2 |
| `qwen3.8-27b-high` | 2 | 2 |

Meaning of each cause:

- `no_response`: sent, but the model returned no gradable answer.

Excluding a `no_response` record is optimistic for a model that used
its whole token budget without answering: that failure is removed
rather than counted against it. Excluding a provider or transport
failure is correct, because it measures the provider, not the model.
The per-arm split is in `cohort-manifest.json`.
