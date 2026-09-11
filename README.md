# Code Output Prediction

Can a coding model predict what a program does without running it?
This benchmark tests final outputs and intermediate loop states from exact
Python and C++ source and input. Each prediction uses an isolated model call
with no interpreter, tools, execution feedback, or retrieval.

Inspired by [CRUXEval](https://crux-eval.github.io/), the release contains
**400 cases across five studies**: 343 Python cases and 57 C++ cases.
Each case has four arms, evaluated under seven model settings.
That is **11,200 planned predictions**, with 11,151 gradable responses and
49 selected prediction cells with no response. Cases can reuse an algorithm; they are not all
distinct source programs.

## Experiments and results

The central question is whether prediction failure is associated with source
complexity, execution length, or runtime state. The table links each study's
setup and complete results. Case counts describe selected benchmark items;
findings use the study's eligible predictions and measurement coverage.

| Study | Cases | Setup | Results |
| --- | ---: | --- | --- |
| LiveCodeBench Hard, Python | 283 | [Design and reproduction](experiments/lcb_hard_v1_python/README.md) | [State size and state load are associated with failure in all seven settings; trace length in six. Cyclomatic complexity is associated in five settings on the post-loop arm.](experiments/lcb_hard_v1_python/reports/README.md) |
| LiveCodeBench Hard, C++ | 35 | [Design and reproduction](experiments/lcb_hard_v1_cpp/README.md) | [Trace length is associated with failure in five settings; state load in two. State size and cyclomatic complexity meet the rule in none.](experiments/lcb_hard_v1_cpp/reports/README.md) |
| Classic Algorithms, Python | 30 | [Design and reproduction](experiments/classic_algorithms_state_prediction/README.md) | [State size and state load are associated with failure in six settings; trace length in five. Cyclomatic complexity meets the rule in none.](experiments/classic_algorithms_state_prediction/reports/README.md) |
| CodeContests, C++ | 22 | [Design and reproduction](experiments/codecontests_reasoning_state_prediction/README.md) | [Trace length is associated with failure in the four high-reasoning settings; state load in two. State size meets the rule in none.](experiments/codecontests_reasoning_state_prediction/reports/README.md) |
| NetworkX network simplex, Python | 30 | [Design and reproduction](experiments/networkx_network_simplex_state_prediction/README.md) | [GPT high answers 6 of 120 predictions correctly; the other settings answer none. Only GPT high has estimable dynamic associations.](experiments/networkx_network_simplex_state_prediction/reports/README.md) |

Dynamic measures show more consistent associations across these studies.
Cyclomatic complexity has mixed results, including significant associations in
LiveCodeBench Python and CodeContests. The evidence does not support a blanket
claim that static complexity has no association with errors.

The reported rank tests use the normalized Mann–Whitney U statistic and
one-sided label permutations. P-values are unadjusted across tests; pooled
runtime analyses do not model dependence among predictions from the same case.
These studies do not test an intelligence-per-token scaling law or an invariant
intervention. Those are motivations and hypotheses for further work.

## The four arms

Each row describes one condition applied to every case. The state arms expose
the same ordered JSON fields and types, and at least one core field changes.

| Arm | Source and input | Prediction target |
| --- | --- | --- |
| `short-trace-final` | Clean source; empirically shorter execution | Final output |
| `long-trace-final` | Same clean source; empirically longer execution | Final output |
| `inside-loop-state` | Long input; deterministic checkpoint inside a selected loop | Declared state projection |
| `post-loop-state` | Long input; checkpoint immediately after that loop exits | Same state projection |

Prompts request `{"output":"<exact text>"}`. Accuracy follows the committed
[grading policies](shared/grading/README.md), including study-specific output
normalization. Response-envelope validity is recorded separately from answer
correctness. [Metric definitions](shared/metrics/README.md) explain the four
complexity dimensions and which measurements can be compared.

## Reproduce the results

Install Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/),
then run from the repository root:

```bash
git clone https://github.com/nlp-research-rosu/code-output-prediction-public.git
cd code-output-prediction-public
python3 reproduce.py --check
python3 reproduce.py --regenerate
```

`--check` verifies the release files, experiment layouts, saved predictions,
and analysis consistency. `--regenerate` rebuilds the statistical tables and
PNG/PDF figures from the saved predictions and measurements, then checks them.
It uses CPython 3.12.11 and each study's pinned analysis dependencies through uv;
the first run downloads those packages. Neither command calls a model.
Exact file-hash reproduction was checked on Linux x86_64.

To work with one study, append its directory name, for example:

```bash
python3 reproduce.py --regenerate classic_algorithms_state_prediction
```

Each study's README gives individual validation and regeneration commands.
Its measurement package describes remeasurement, toolchains, and coverage
limits; remeasurement is separate from regenerating the reported results.
The [shared implementation](shared/README.md) explains the command-line tools
and how to collect new predictions.

## Included evidence

Each experiment contains the exact tasks and oracles, model configuration,
native attempts and parsed responses, selected-attempt metadata, complexity
measurements, normalized analysis data, and generated reports and figures.
`RELEASE.json` records the source snapshot; `MANIFEST.sha256` fixes the release
contents. Native sessions are benchmark
invocations; source, input, prompt, oracle, and session bytes are preserved.
The reports identify exclusions and unavailable measurements explicitly.

Source revisions, construction, and attribution are recorded in each study's
`problems/README.md` and `cases.json`. See the
[third-party notices](THIRD_PARTY_NOTICES.md) for retained license terms.
