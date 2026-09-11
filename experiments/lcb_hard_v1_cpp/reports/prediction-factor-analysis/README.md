# Prediction-factor analysis — artifacts

This package contains the generated evidence and method for the C++20 cohort.
It states no findings; the [analysis report](../README.md) interprets the
artifacts.

## Results and figures

- [Overall accuracy by arm](data/analysis/overall-accuracy.md)
- [Static association tables](data/analysis/static-tables.md)
- [Dynamic association tables](data/analysis/dynamic-tables.md)
- [All chart previews](charts.md)
- [Machine-readable series results](data/analysis/series-results.csv)
- [Normalized raw points](data/analysis/raw-points.csv)

## Inputs

| File | Contents |
| --- | --- |
| [`data/source-points.csv`](data/source-points.csv) | Every eligible prediction joined to every available retained metric. |
| [`data/cohort-manifest.json`](data/cohort-manifest.json) | Selection policy, exclusions, coverage, and pooled execution identities. |
| [`chart-config.json`](chart-config.json) | Model order, labels, units, bins, and chart presentation. |
| [`logistic-regression-config.json`](logistic-regression-config.json) | The four-arm pooled StateLoad regression requested for every model. |

Predictions come from the committed [`runs/`](../../runs/) tree. Complexity
values come from the upstream
[program-complexity package](../../measurements/program-complexity/README.md).
The selected-attempt manifest for model settings that required explicit attempt selection is
[`analysis/selected-attempts.json`](../../analysis/selected-attempts.json).

## Outputs

The generated [data dictionary](data/analysis/README.md) defines every CSV
column and status.

| Output | Contents |
| --- | --- |
| [Overall accuracy](data/analysis/overall-accuracy.md) | Correct and eligible predictions by arm and model, plus exclusions. |
| [Matched-cohort accuracy](data/analysis/matched-accuracy.md) | Arm accuracy on one fixed program set per model. |
| [Metric support matrix](data/analysis/metric-matrix.md) | `theta`, permutation `p`, and `n=measured/eligible` for every factor and model. |
| [Measurement coverage](data/analysis/measurement-coverage.md) | Numeric profile coverage and each unavailable cause. |
| [Supported associations](data/analysis/supported-associations.md) | Audit list of all series meeting the predeclared rule. |
| [Static tables](data/analysis/static-tables.md) | Arm-specific `Omega_CC` results. |
| [Dynamic tables](data/analysis/dynamic-tables.md) | Four-arm pooled runtime-factor results. |
| [Logistic regressions](data/analysis/logistic-regressions.md) | StateLoad OR per doubling, 95% CI, p-value, and pooled `n`. |
| [Chart index](charts.md) | Previews of all four static and three dynamic charts. |
| [`chart-data.csv`](chart-data.csv) | Exact descriptive bins drawn in ordinary charts. |
| [`logistic-chart-data.csv`](logistic-chart-data.csv) | Exact wrong-rate bins drawn in the StateLoad chart. |
| [`chart-manifest.json`](chart-manifest.json) | Input and output hashes, counts, versions, and style contract. |

PNG and PDF versions of every figure are under [`charts/`](charts/). No
combined report PDF is produced.

## Statistical method

For each series, `theta_obs` is the fraction of wrong-versus-correct pairs in
which the wrong prediction has the larger metric value, with ties worth one
half. The one-sided permutation test shuffles the correctness labels 10,000
times using global seed `20260812`. The declared association rule is
`theta_obs > 0.5` and unadjusted `p_value < 0.05`; the floor is `< 0.0001`.

`Omega_CC` is analyzed separately for each arm because source bytes can differ.
The three dynamic factors pool `short-trace-final`, `long-trace-final`,
`inside-loop-state`, and `post-loop-state` into one series per model. StateLoad
also uses `logit P(wrong=1) = beta0 + beta1 * log2(L)`; its reported odds ratio
is `exp(beta1)`, the error-odds multiplier when `L` doubles.

## Regenerate

```bash
uv run --python 3.12.11 --with-requirements experiments/lcb_hard_v1_cpp/analysis/requirements.txt python experiments/lcb_hard_v1_cpp/analysis/generate_report.py
```

The [cohort](data/cohort-manifest.json),
[analysis](data/analysis/analysis-manifest.json), and
[chart](chart-manifest.json) manifests record the complete provenance.
