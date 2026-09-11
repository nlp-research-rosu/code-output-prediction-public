# Overall accuracy

Predictions are deduplicated by `prediction_id` before counting.
Each cell shows `correct/eligible (accuracy)` for one arm and model.

Eligible counts differ between arms because ungradable answers are
excluded, so a difference between two cells in the same column mixes
an arm effect with a coverage difference. Compare arms within a model
using `matched-accuracy.md`, which holds the program set fixed.

| Arm | deepseek-v4-pro-0813-high | deepseek-v4-pro-0813-off | glm-5.3-high | gpt-5.6-sol-high | gpt-5.6-sol-off | qwen3.8-27b-high | qwen3.8-27b-off |
| --- | --- | --- | --- | --- | --- | --- | --- |
| inside-loop-state | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) |
| long-trace-final | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 2/30 (6.7%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) |
| post-loop-state | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) |
| short-trace-final | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) | 4/30 (13.3%) | 0/30 (0.0%) | 0/30 (0.0%) | 0/30 (0.0%) |
