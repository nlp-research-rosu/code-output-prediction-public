# LiveCodeBench Hard v1 — Python

## Objective

This experiment tests whether exact-output prediction degrades under longer
executions or loop-state prediction for the Python portion of LiveCodeBench
Hard v1. It contains 283 cases and four arms: **283 x 4 = 1,132 prediction
cells per complete model setting**.

## Selection

Benchmark items were selected from `livecodebench/code_generation_lite` revision
`25d8cb8f0db2efe1b589941eb8c26a219850d4d2`. The selection reviewed
350 Hard items; construction and determinism checks retained 318 cases: the 283 cases
here and 35 C++20 cases analyzed separately in
[`lcb_hard_v1_cpp`](../lcb_hard_v1_cpp/README.md). `atcoder/abc329_e` has
hash-order-dependent state outputs, and
`atcoder/abc375_g` uses an unseeded random modulus that can change its answer.
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
| `gpt-5.6-sol-high` | OpenAI Codex | `gpt-5.6-sol` | high | 3600 | 1,132/1,132 |
| `gpt-5.6-sol-off` | OpenAI Codex | `gpt-5.6-sol` | off (Pi `minimal`) | 1800 | 1,132/1,132 |
| `glm-5.3-high` | ZAI Coding Plan | `glm-5.3` | high | 3600 | 1,132/1,132 |
| `deepseek-v4-pro-0813-off` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | off | 1800 | 1,132/1,132 |
| `deepseek-v4-pro-0813-high` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | high | 3600 | 1,132/1,132 |
| `qwen3.8-27b-off` | OpenRouter | `qwen/qwen3.8-27b` | off | 1800 | 1,132/1,132 |
| `qwen3.8-27b-high` | OpenRouter | `qwen/qwen3.8-27b` | high | 3600 | 1,132/1,132 |

The design selects **283 cases x 4 arms x 7 settings = 7,924 prediction cells**,
one prediction per cell. The release preserves 8,263 native attempts, including
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

Two GPT-off state predictions retain positive reasoning usage; the
[analysis limits](reports/README.md#limits) identify these condition deviations.

## Results and figures

- [Analysis report](reports/README.md)
- [Problem source and construction](problems/README.md)
- [Complexity measurements](measurements/program-complexity/README.md)
- [Analysis artifacts and method](reports/prediction-factor-analysis/README.md)

## Reproduce

```bash
uv run --python 3.12.11 python workbench.py validate experiments/lcb_hard_v1_python
uv run --python 3.12.11 python -m experiments.lcb_hard_v1_python.analysis.normalize_complexity_profiles --benchmark experiments/lcb_hard_v1_python
uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_python/analysis/requirements.txt python experiments/lcb_hard_v1_python/analysis/generate_report.py
```

These commands do not call a model.
