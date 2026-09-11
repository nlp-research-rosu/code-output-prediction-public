# Matched-cohort accuracy

Each model is restricted to the programs that produced an eligible
prediction in every arm that model ran, so all its arms share one
denominator. Use this table to compare arms within a model. Use
`overall-accuracy.md` to see how many predictions each arm actually
produced.
Every cell is `correct/matched programs (accuracy)`; `no data` means
no program produced a gradable prediction in every arm for that model.

This cohort excludes programs whose answer was ungradable in any arm.
Those tend to be the hardest programs, so matched accuracy usually
sits above the raw accuracy for the same arm. Neither table alone is
the whole result.

Matched cohort size per model:

- `deepseek-v4-pro-0813-high`: 283 programs across 4 arms.
- `deepseek-v4-pro-0813-off`: 283 programs across 4 arms.
- `glm-5.3-high`: 283 programs across 4 arms.
- `gpt-5.6-sol-high`: 283 programs across 4 arms.
- `gpt-5.6-sol-off`: 251 programs across 4 arms.
- `qwen3.8-27b-high`: 283 programs across 4 arms.
- `qwen3.8-27b-off`: 283 programs across 4 arms.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 152/283 (53.7%) | 0/283 (0.0%) | 108/283 (38.2%) | 200/283 (70.7%) | 25/251 (10.0%) | 47/283 (16.6%) | 0/283 (0.0%) |
| long-trace-final | 218/283 (77.0%) | 49/283 (17.3%) | 203/283 (71.7%) | 236/283 (83.4%) | 99/251 (39.4%) | 149/283 (52.7%) | 44/283 (15.5%) |
| post-loop-state | 97/283 (34.3%) | 0/283 (0.0%) | 98/283 (34.6%) | 195/283 (68.9%) | 33/251 (13.1%) | 38/283 (13.4%) | 0/283 (0.0%) |
| short-trace-final | 279/283 (98.6%) | 66/283 (23.3%) | 270/283 (95.4%) | 282/283 (99.6%) | 140/251 (55.8%) | 257/283 (90.8%) | 40/283 (14.1%) |

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
