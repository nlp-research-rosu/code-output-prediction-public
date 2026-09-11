# CodeContests reasoning and state prediction

## Objective

This experiment tests how reasoning effort and requested execution state affect
exact-output prediction for 22 C++ programs: **22 cases x 4 arms = 88
predictions per model**.

## Selection

Programs come from the validation and test splits of
[`deepmind/code_contests`](https://huggingface.co/datasets/deepmind/code_contests)
at revision `802411c3010cb00d1b05bad57ca77365a3c699d6` (CC-BY-4.0).
The fixed funnel started with 79 rated C++ candidates and retained 22 programs
with deterministic measured short/long inputs and a shared, meaningful state
projection available inside and immediately after one selected loop. One final
candidate lacked a valid post-loop checkpoint. Two programs exposed random
state that was nondeterministic or runtime-dependent. Selection did not inspect
model outcomes and was not exhaustive over the dataset.

See [Problem source and construction](problems/README.md) and
[`cases.json`](cases.json) for source identity, inputs, checkpoints, and hashes.

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
| `gpt-5.6-sol-high` | OpenAI Codex | `gpt-5.6-sol` | high | 3600 | 88/88 |
| `gpt-5.6-sol-off` | OpenAI Codex | `gpt-5.6-sol` | off (Pi `minimal`) | 3600 | 88/88 |
| `glm-5.3-high` | OpenRouter / ZAI Coding Plan | `glm-5.3` | high | 3600 | 88/88 |
| `deepseek-v4-pro-0813-off` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | off | 1800 | 88/88 |
| `deepseek-v4-pro-0813-high` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | high | 3600 | 88/88 |
| `qwen3.8-27b-off` | OpenRouter | `qwen/qwen3.8-27b` | off | 1800 | 88/88 |
| `qwen3.8-27b-high` | OpenRouter | `qwen/qwen3.8-27b` | high | 3600 | 88/88 |

The design selects **22 cases x 4 arms x 7 settings = 616 prediction cells**,
one prediction per cell. The release preserves 666 native attempts, including
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

The headline score compares ordered signed-integer and alphabetic tokens,
ignoring punctuation and whitespace. A separate byte-exact score is retained
in the graded data; the tables here use the token-based score.
Response-envelope validity and correctness are scored separately under the
[four-way grading contract](../../shared/grading/README.md).

## Results and figures

- [Analysis report](reports/README.md)
- [Problem source and construction](problems/README.md)
- [Complexity measurements](measurements/program-complexity/README.md)
- [Analysis artifacts and method](reports/prediction-factor-analysis/README.md)

## Reproduce

```bash
uv run --python 3.12.11 python workbench.py validate experiments/codecontests_reasoning_state_prediction
uv run --python 3.12.11 --with-requirements experiments/codecontests_reasoning_state_prediction/analysis/requirements.txt python experiments/codecontests_reasoning_state_prediction/analysis/generate_report.py
```

These commands do not call a model.
