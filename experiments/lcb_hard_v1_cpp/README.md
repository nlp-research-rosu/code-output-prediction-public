# LiveCodeBench Hard v1 — C++20

## Objective

This experiment tests whether exact-output prediction degrades under longer
executions or loop-state prediction for the C++20 portion of LiveCodeBench
Hard v1. It contains 35 cases and four arms: **35 x 4 = 140 prediction cells
per complete model setting**.

## Selection

Benchmark items were selected from `livecodebench/code_generation_lite` revision
`25d8cb8f0db2efe1b589941eb8c26a219850d4d2`. The selection reviewed
350 Hard items; construction and determinism checks retained 318 cases: the 35 C++20
cases here and 283 Python cases analyzed separately in
[`lcb_hard_v1_python`](../lcb_hard_v1_python/README.md).
The full funnel, exclusions, and included-case evidence are in
[`cases.json`](cases.json).

See [Problem source and construction](problems/README.md) for provenance and
the construction summary.

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
| `gpt-5.6-sol-high` | OpenAI Codex | `gpt-5.6-sol` | high | 3600 | 140/140 |
| `gpt-5.6-sol-off` | OpenAI Codex | `gpt-5.6-sol` | off (Pi `minimal`) | 1800 | 140/140 |
| `glm-5.3-high` | ZAI Coding Plan | `glm-5.3` | high | 3600 | 140/140 |
| `deepseek-v4-pro-0813-off` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | off | 1800 | 140/140 |
| `deepseek-v4-pro-0813-high` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | high | 3600 | 140/140 |
| `qwen3.8-27b-off` | OpenRouter | `qwen/qwen3.8-27b` | off | 1800 | 140/140 |
| `qwen3.8-27b-high` | OpenRouter | `qwen/qwen3.8-27b` | high | 3600 | 140/140 |

The design selects **35 cases x 4 arms x 7 settings = 980 prediction cells**,
one prediction per cell. The release preserves 1,002 native attempts, including
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
uv run --python 3.12.11 python workbench.py validate experiments/lcb_hard_v1_cpp
for arm in short-trace-final long-trace-final inside-loop-state post-loop-state; do
  uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_cpp/analysis/requirements.txt python -m experiments.lcb_hard_v1_cpp.analysis.program_complexity run --benchmark experiments/lcb_hard_v1_cpp --arm "$arm" --language cpp --workers 2 --execution-timeout 180
done
uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_cpp/analysis/requirements.txt python experiments/lcb_hard_v1_cpp/analysis/generate_report.py
```

These commands do not call a model.
