# NetworkX network-simplex reasoning and state prediction

## Objective

This experiment tests where exact-output and intermediate-state prediction
degrades as one production algorithm performs more runtime work. It contains
30 graph cases for one algorithm, four arms, and seven collected model settings: **30 x 4 x 7 = 840
prediction cells**.

## Selection

Programs use NetworkX `network_simplex` 3.4.2 at commit
`2acf1590f82757c01a57b81b8c5dfb79e60aa416` (BSD-3-Clause). Before model
evaluation, the deterministic builder searched 90,000 generated graphs and
selected 10 distinct topologies for each predeclared lower, medium, and higher
runtime cohort. Within a problem, topology stays fixed while capacities and
weights produce strictly ordered measured short and long native traces.

See [Problem source and construction](problems/README.md) and
[`cases.json`](cases.json) for the funnel, hashes, inputs, and checkpoints.

## Arms

| Arm | Source and input | Oracle |
| --- | --- | --- |
| `short-trace-final` | Clean source; measured shorter-trace graph | Final minimum cost |
| `long-trace-final` | Same clean source; measured longer-trace graph | Final minimum cost |
| `inside-loop-state` | Long input; stop inside the pivot loop | Canonical JSON `node_potentials` |
| `post-loop-state` | Long input; stop immediately after that loop | Same field and type, with changed values |

## Models and collection

Each row is one model setting. Coverage is selected cells/planned cells,
including ungradable no-response outcomes; timeout is seconds per attempt.

| Run | Provider | Model | Reasoning | Timeout (s) | Coverage |
| --- | --- | --- | --- | ---: | ---: |
| `gpt-5.6-sol-high` | OpenAI Codex | `gpt-5.6-sol` | high | 1800 | 120/120 |
| `gpt-5.6-sol-off` | OpenAI Codex | `gpt-5.6-sol` | off (Pi `minimal`) | 1800 | 120/120 |
| `glm-5.3-high` | ZAI Coding Plan | `glm-5.3` | high | 3600 | 120/120 |
| `deepseek-v4-pro-0813-off` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | off | 1800 | 120/120 |
| `deepseek-v4-pro-0813-high` | OpenRouter | `deepseek/deepseek-v4-pro-0813` | high | 3600 | 120/120 |
| `qwen3.8-27b-off` | OpenRouter | `qwen/qwen3.8-27b` | off | 1800 | 120/120 |
| `qwen3.8-27b-high` | OpenRouter | `qwen/qwen3.8-27b` | high | 3600 | 120/120 |

The design selects **30 cases x 4 arms x 7 settings = 840 prediction cells**,
one prediction per cell. The release preserves 906 native attempts, including
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

The grader compares the decoded predicted output with the oracle byte-for-byte,
including JSON serialization and the final newline.
Response-envelope validity and correctness are scored separately under the
[four-way grading contract](../../shared/grading/README.md).

## Results and figures

- [Analysis report](reports/README.md)
- [Problem source and construction](problems/README.md)
- [Complexity measurements](measurements/program-complexity/README.md)
- [Analysis artifacts and method](reports/prediction-factor-analysis/README.md)

## Reproduce

```bash
uv run --python 3.12.11 --with-requirements experiments/networkx_network_simplex_state_prediction/analysis/requirements.txt python experiments/networkx_network_simplex_state_prediction/analysis/materialize.py --verify-selection
uv run --python 3.12.11 python workbench.py validate experiments/networkx_network_simplex_state_prediction
uv run --python 3.12.11 --with-requirements experiments/networkx_network_simplex_state_prediction/analysis/requirements.txt python experiments/networkx_network_simplex_state_prediction/analysis/generate_report.py
```

These commands do not call a model.
