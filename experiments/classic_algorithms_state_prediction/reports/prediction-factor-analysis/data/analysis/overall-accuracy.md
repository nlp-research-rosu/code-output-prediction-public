# Overall accuracy

Predictions are deduplicated by `prediction_id` before counting.
Each cell shows `correct/eligible (accuracy)` for one arm and model.

Eligible counts differ between arms because ungradable answers are
excluded, so a difference between two cells in the same column mixes
an arm effect with a coverage difference. Compare arms within a model
using `matched-accuracy.md`, which holds the program set fixed.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 19/30 (63.3%) | 0/30 (0.0%) | 10/30 (33.3%) | 20/30 (66.7%) | 0/30 (0.0%) | 1/30 (3.3%) | 0/30 (0.0%) |
| long-trace-final | 27/30 (90.0%) | 2/30 (6.7%) | 20/30 (66.7%) | 28/30 (93.3%) | 6/30 (20.0%) | 8/30 (26.7%) | 2/30 (6.7%) |
| post-loop-state | 24/30 (80.0%) | 1/30 (3.3%) | 12/30 (40.0%) | 21/30 (70.0%) | 2/30 (6.7%) | 1/30 (3.3%) | 0/30 (0.0%) |
| short-trace-final | 30/30 (100.0%) | 7/30 (23.3%) | 26/30 (86.7%) | 30/30 (100.0%) | 16/30 (53.3%) | 26/30 (86.7%) | 2/30 (6.7%) |
