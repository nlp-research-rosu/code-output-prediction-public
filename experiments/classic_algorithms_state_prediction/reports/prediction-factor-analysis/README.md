# Prediction-factor analysis — artifacts

This package contains generated evidence and method. Findings are stated only
in the [analysis report](../README.md).

## Results and figures

- [Overall accuracy by arm](data/analysis/overall-accuracy.md)
- [Static association tables](data/analysis/static-tables.md)
- [Dynamic association tables](data/analysis/dynamic-tables.md)
- [All chart previews](charts.md)
- [Machine-readable series results](data/analysis/series-results.csv)
- [Normalized raw points](data/analysis/raw-points.csv)

## Inputs and outputs

| Artifact | Contents |
| --- | --- |
| [`data/source-points.csv`](data/source-points.csv) | Eligible predictions joined to retained metric values. |
| [`data/cohort-manifest.json`](data/cohort-manifest.json) | Selection, exclusions, coverage, and execution identities. |
| [`analysis/selected-attempts.json`](../../analysis/selected-attempts.json) | Pinned corrected attempts and session hashes. |
| [`chart-config.json`](chart-config.json) | Model order, labels, units, bins, and formats. |
| [`logistic-regression-config.json`](logistic-regression-config.json) | Four-arm pooled StateLoad regression request. |
| [Matched accuracy](data/analysis/matched-accuracy.md) | Arm scores on one fixed program cohort per model. |
| [Metric support matrix](data/analysis/metric-matrix.md) | Every theta, permutation p, and measured/eligible count. |
| [Measurement coverage](data/analysis/measurement-coverage.md) | Numeric coverage and unavailable causes. |
| [Supported associations](data/analysis/supported-associations.md) | Audit list for the predeclared decision rule. |
| [Logistic regressions](data/analysis/logistic-regressions.md) | StateLoad OR, confidence interval, p, and pooled n. |
| [`chart-data.csv`](chart-data.csv) | Exact descriptive bins drawn in ordinary charts. |
| [`logistic-chart-data.csv`](logistic-chart-data.csv) | Exact bins and fitted curve data for StateLoad. |

The generated [data dictionary](data/analysis/README.md) defines every CSV
column. PNG and PDF figures are under [`charts/`](charts/); no combined report
PDF is produced.

## Statistical method

`theta_obs` is the share of wrong-versus-correct pairs where the wrong
prediction has the larger metric, with ties worth one half. The one-sided test
uses 10,000 label permutations and seed `20260812`. Support requires
`theta_obs > 0.5` and unadjusted `p_value < 0.05`.

`Omega_CC` is arm-specific. Dynamic metrics pool `short-trace-final`,
`long-trace-final`, `inside-loop-state`, and `post-loop-state` per model.
StateLoad additionally fits `logit P(wrong=1)` against `log2(StateLoad)`.

## Regenerate

```bash
uv run --python 3.12.11 --with-requirements experiments/classic_algorithms_state_prediction/analysis/requirements.txt python experiments/classic_algorithms_state_prediction/analysis/generate_report.py
```

The [cohort](data/cohort-manifest.json),
[analysis](data/analysis/analysis-manifest.json), and
[chart](chart-manifest.json) manifests record provenance.
