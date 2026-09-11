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

- `deepseek-v4-pro-0813-high`: 30 programs across 4 arms.
- `deepseek-v4-pro-0813-off`: 30 programs across 4 arms.
- `glm-5.3-high`: 30 programs across 4 arms.
- `gpt-5.6-sol-high`: 30 programs across 4 arms.
- `gpt-5.6-sol-off`: 30 programs across 4 arms.
- `qwen3.8-27b-high`: 30 programs across 4 arms.
- `qwen3.8-27b-off`: 30 programs across 4 arms.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 19/30 (63.3%) | 0/30 (0.0%) | 10/30 (33.3%) | 20/30 (66.7%) | 0/30 (0.0%) | 1/30 (3.3%) | 0/30 (0.0%) |
| long-trace-final | 27/30 (90.0%) | 2/30 (6.7%) | 20/30 (66.7%) | 28/30 (93.3%) | 6/30 (20.0%) | 8/30 (26.7%) | 2/30 (6.7%) |
| post-loop-state | 24/30 (80.0%) | 1/30 (3.3%) | 12/30 (40.0%) | 21/30 (70.0%) | 2/30 (6.7%) | 1/30 (3.3%) | 0/30 (0.0%) |
| short-trace-final | 30/30 (100.0%) | 7/30 (23.3%) | 26/30 (86.7%) | 30/30 (100.0%) | 16/30 (53.3%) | 26/30 (86.7%) | 2/30 (6.7%) |
