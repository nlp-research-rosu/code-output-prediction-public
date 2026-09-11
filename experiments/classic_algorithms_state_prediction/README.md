# Classic algorithms state prediction

## Objective

This experiment tests whether exact-output prediction becomes less reliable as
the execution state of canonical algorithms grows. It contains 30 deterministic
Python programs and four controlled arms: **30 cases x 4 arms = 120 predictions
per model**.

## Selection

The purposive suite was fixed before model evaluation. Repository-authored
implementations cover dynamic programming, graph, string, sorting, simulation,
numerical, and geometry workloads. Every case is deterministic, uses only the
Python standard library, exposes a serializable core state, and has measured
short/long inputs with a strictly longer native trace under the long input.
The selection is not exhaustive.

See [Problem source and construction](problems/README.md) and
[`cases.json`](cases.json) for sources, hashes, checkpoints, and validation.

## Arms

| Arm | Source and input | Oracle |
| --- | --- | --- |
| `short-trace-final` | Clean source; measured shorter-trace input | Normal final output |
| `long-trace-final` | Same clean source; measured longer-trace input | Normal final output |
| `inside-loop-state` | Long input; stop inside the selected loop | Canonical JSON core state |
| `post-loop-state` | Long input; stop immediately after that loop | Same JSON fields and types, with changed state |

## Models and collection

Each row is one model setting. Coverage is selected cells/planned cells,
including ungradable no-response outcomes; timeout is seconds per attempt.

| Run | Provider | Model | Reasoning | Timeout (s) | Coverage |
| --- | --- | --- | --- | ---: | ---: |
| `gpt-5.6-sol-high` | OpenAI Codex | `gpt-5.6-sol` | high | 3600 | 120/120 |
| `gpt-5.6-sol-off` | OpenAI Codex | `gpt-5.6-sol` | off (Pi `minimal`) | 1800 | 120/120 |
| `glm-5.3-high` | ZAI Coding Plan | `glm-5.3` | high | 3600 | 120/120 |
| `deepseek-v4-pro-0813-off` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | off | 1800 | 120/120 |
| `deepseek-v4-pro-0813-high` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | high | 3600 | 120/120 |
| `qwen3.8-27b-off` | OpenRouter | `qwen/qwen3.8-27b` | off | 1800 | 120/120 |
| `qwen3.8-27b-high` | OpenRouter | `qwen/qwen3.8-27b` | high | 3600 | 120/120 |

The design selects **30 cases x 4 arms x 7 settings = 840 prediction cells**,
one prediction per cell. The release preserves 1,082 native attempts, including
retries. Collection used isolated Pi sessions through the listed providers,
with tools, extensions, context files, retrieval, and execution feedback
disabled. Models received the exact source and input; oracles were withheld.

GPT off uses Pi `minimal`, mapped to provider `none`; selected completed
responses are checked for thinking blocks and reported reasoning usage.
The default selection is the first completed response; the
[selected-attempt manifest](analysis/selected-attempts.json) pins exceptions
for transport/no-response retries and verified condition or task corrections.
A completed wrong answer or invalid envelope is not a retry reason. Native
attempts and selected hashes preserve the evidence for every retry.

The grader compares JSON values when the oracle is JSON, and whitespace-separated
tokens otherwise; it does not require identical output formatting.
Response-envelope validity and correctness are scored separately under the
[four-way grading contract](../../shared/grading/README.md).

## Results and figures

- [Analysis report](reports/README.md)
- [Problem source and construction](problems/README.md)
- [Complexity measurements](measurements/program-complexity/README.md)
- [Analysis artifacts and method](reports/prediction-factor-analysis/README.md)

## Reproduce

```bash
uv run --python 3.12.11 python -m experiments.classic_algorithms_state_prediction.analysis.materialize
uv run --python 3.12.11 python workbench.py validate experiments/classic_algorithms_state_prediction
uv run --python 3.12.11 python -m experiments.classic_algorithms_state_prediction.analysis.measure_complexity --workers 4 --execution-timeout 120 --state-cell-visit-limit 50000000
uv run --python 3.12.11 --with-requirements experiments/classic_algorithms_state_prediction/analysis/requirements.txt python experiments/classic_algorithms_state_prediction/analysis/generate_report.py
```

These commands do not call a model.
