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

- `deepseek-v4-pro-0813-high`: 35 programs across 4 arms.
- `deepseek-v4-pro-0813-off`: 35 programs across 4 arms.
- `glm-5.3-high`: 35 programs across 4 arms.
- `gpt-5.6-sol-high`: 35 programs across 4 arms.
- `gpt-5.6-sol-off`: 33 programs across 4 arms.
- `qwen3.8-27b-high`: 35 programs across 4 arms.
- `qwen3.8-27b-off`: 35 programs across 4 arms.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 23/35 (65.7%) | 1/35 (2.9%) | 15/35 (42.9%) | 25/35 (71.4%) | 5/33 (15.2%) | 10/35 (28.6%) | 0/35 (0.0%) |
| long-trace-final | 22/35 (62.9%) | 4/35 (11.4%) | 21/35 (60.0%) | 26/35 (74.3%) | 8/33 (24.2%) | 13/35 (37.1%) | 3/35 (8.6%) |
| post-loop-state | 22/35 (62.9%) | 1/35 (2.9%) | 14/35 (40.0%) | 21/35 (60.0%) | 7/33 (21.2%) | 9/35 (25.7%) | 0/35 (0.0%) |
| short-trace-final | 35/35 (100.0%) | 1/35 (2.9%) | 34/35 (97.1%) | 34/35 (97.1%) | 10/33 (30.3%) | 30/35 (85.7%) | 3/35 (8.6%) |

## What these denominators leave out

A prediction counts only when the model returned an answer that could
be graded. Records below are excluded from every cell above: they are
**not** counted as wrong, so each denominator is smaller than the arm's
problem count.

| Model | `no_response` | total excluded |
| --- | ---: | ---: |
| `gpt-5.6-sol-off` | 2 | 2 |

Meaning of each cause:

- `no_response`: sent, but the model returned no gradable answer.

Excluding a `no_response` record is optimistic for a model that used
its whole token budget without answering: that failure is removed
rather than counted against it. Excluding a provider or transport
failure is correct, because it measures the provider, not the model.
The per-arm split is in `cohort-manifest.json`.
