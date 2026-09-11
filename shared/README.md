# Shared benchmark implementation

These tools are used by every experiment. Run commands from the repository
root. The study-specific adapters and dependency pins live under each
experiment's `analysis/` and `measurements/` directories.
Original measurement records retain their historical tool paths and hashes;
the executable paths in this release are listed below.

| Stage | Implementation | Input and output |
| --- | --- | --- |
| Validate or collect | [`workbench.py`](../workbench.py) | Exact task files and model configuration; isolated native attempts |
| Select attempts | [`attempt_selection.py`](../attempt_selection.py) | Original attempts and explicit corrected-cell selections |
| Grade | [`output_grading.py`](../output_grading.py) and experiment `grade.py` | Saved model responses and committed oracles; correctness and envelope validity |
| Measure | [`metrics/scripts/`](metrics/scripts/) and experiment adapters | Exact source-input executions; separate complexity profiles |
| Analyze | [`analysis/scripts/analyze.py`](analysis/scripts/analyze.py) | Normalized points; accuracy tables, rank tests, and configured logistic fits |
| Plot | [`charts/scripts/generate_analysis.py`](charts/scripts/generate_analysis.py) | Analyzed points and statistics; PNG/PDF figures and chart data |
| Check reports | [`reports/scripts/validate_report.py`](reports/scripts/validate_report.py) | Final report and generated evidence; consistency checks |

The [grading policies](grading/README.md) and
[metric definitions](metrics/README.md) specify what the results mean.
Statistical parameters and cohort boundaries are recorded in each report
package's manifests. The top-level [`reproduce.py`](../reproduce.py) runs the
existing experiment pipelines; it does not choose a new cohort or analysis.

## Inspect an experiment

```bash
uv run --python 3.12.11 python workbench.py validate experiments/lcb_hard_v1_python
uv run --python 3.12.11 python workbench.py report experiments/lcb_hard_v1_python --verbose
uv run --python 3.12.11 python experiments/lcb_hard_v1_python/grade.py --model gpt-5.6-sol-high
```

## Collect new predictions

Reproducing saved results requires no provider access. New collection requires
[Pi](https://pi.dev), provider authentication, and access to the exact configured
models. Historical model IDs and provider behavior may no longer be available;
a fresh collection need not reproduce the saved answers.

```bash
npm install -g --ignore-scripts @earendil-works/pi-coding-agent
cp .env.example .env
```

Fill in the needed provider credentials locally, or authenticate through Pi.
Inspect the selected study's `workbench.toml` for model IDs, reasoning levels,
timeouts, and repetitions. Each configured complete setting uses four calls
per case. A complete sweep of this release has 11,200 intended cells before
transport retries. Estimate the token budget and current provider cost before
starting a new collection.

```bash
uv run --python 3.12.11 python workbench.py run experiments/lcb_hard_v1_python --model gpt-5.6-sol-high
```

`run` skips existing attempts and never overwrites them. For an independent
collection, copy the experiment's task and configuration files into a separate
checkout without its `runs/` directory; keep the released evidence intact.
Every prediction starts in isolation with tools and retrieval disabled.
`ground-output.txt` is never included in the rendered model prompt.

The stored `gpt-5.6-sol-off` run ID uses Pi's `minimal` level; request and
reasoning evidence are described in each study. Preserve native sessions and
record any provider or reasoning mismatch explicitly. Completed wrong answers
and invalid envelopes are outcomes, not reasons to retry. Transport failures
and no-response attempts are distinct from semantic errors.
