# Data files

Every file here is generated. Do not edit them by hand; rerun the analysis.

Values are written at full precision because these files are the machine-readable
source. Reader-facing documents round them.

## `measurement-coverage.md`

Per-arm dynamic metric availability before model outcomes are joined. Every
cell divides numeric measurements by selected profiles. The adjacent reason
table distinguishes an adapter that did not run from a measurement that failed.

## `raw-points.csv`

One row per (prediction, metric). This is the input to every statistic.

| Column | Meaning |
| --- | --- |
| `series_id` | The statistical series this point belongs to. |
| `prediction_id` | One graded model answer. Stable across metrics, so the same answer keeps one id when joined to multiple metrics. |
| `program_id` | The source program the prediction is about. |
| `execution_id` | One exact source-plus-input runtime identity. Empty for static points. |
| `model_id` | The configured model and reasoning setting. |
| `arm_id` | The real arm the prediction came from. |
| `arm_group` | The label the series is reported under: the arm itself for static series, `all-arms` for the four-arm dynamic pool. |
| `scope` | `static` for source metrics, `dynamic` for execution metrics. |
| `metric_name` | Which factor this row measures. |
| `x` | The measured factor value. |
| `y` | `1` if the prediction was correct, `0` if it was wrong. |

## `series-results.csv`

One row per statistical series: one model, one arm group, one metric.

| Column | Meaning |
| --- | --- |
| `series_id` | Matches `raw-points.csv`. |
| `model_id`, `arm_group`, `scope`, `metric_name` | What the series covers. |
| `theta_obs` | How often a failed prediction had the larger metric value than a successful one, ties counting half. `0.5` means no ordering tendency. Empty when the series has only one outcome. |
| `p_value` | Share of shuffled correct/wrong labelings that separated the groups at least as much as the observed data. The smallest possible value is `1 / (1 + permutations)`; at that floor no shuffle reached the observed separation. Empty when `theta_obs` is empty. |
| `n_success` | Correct predictions carrying a measurement for this metric. |
| `n_failure` | Wrong predictions carrying a measurement for this metric. |
| `n_total` | `n_success + n_failure`. |
| `permutations` | Label shuffles performed. |
| `series_seed` | Seed for this series, derived from the global seed and `series_id`, so a rerun reproduces it exactly. |
| `status` | `OK`: theta and p were computed. `ALL_WRONG` / `ALL_CORRECT`: every prediction had the same outcome, so no failure-success pair exists and theta is undefined. That is a real result about the model, not a measurement problem. |

## Optional logistic-regression files

Produced only with `--logistic-regression-config`:

- `logistic-regression-points.csv` contains the selected numeric observations,
  with `wrong=1-y` and the real arm retained.
- `logistic-regression-results.csv` contains one model fit per declared
  regression. `odds_ratio=exp(beta1)` is the error-odds multiplier when the
  metric doubles. `se_beta1`, `ci_low`, `ci_high`, and `p_value` come from the
  standard maximum-likelihood logistic model and its covariance matrix.
- `logistic-regression-curves.csv` contains the fitted error probability and
  model-based 95% band on a fixed x grid. Chart generation reads these values and
  does not refit the model.
- `logistic-regressions.md` is the reader-facing OR, 95% CI, and p-value table.

## `chart-data.csv`

The generated bins drawn in the figures.

| Column | Meaning |
| --- | --- |
| `series_id`, `model_id`, `arm_group`, `scope`, `metric_name` | Which series the bin belongs to. |
| `bin_index` | Bin position, lowest metric values first. |
| `x` | Representative metric value for the bin. |
| `accuracy` | Share correct within the bin. |
| `wilson_low`, `wilson_high` | Wilson 95% interval for that share. Wide bars mean few predictions. |
| `n_success`, `n_failure`, `n_total` | Counts behind the bin. |

## `overall-accuracy.csv`

Accuracy per arm and model, on each cell's own eligible predictions.

| Column | Meaning |
| --- | --- |
| `arm_id` | The arm. |
| `arm_group` | Its presentation label. |
| `model_id` | The model and reasoning setting. |
| `correct` | Correct predictions. |
| `total` | Predictions that produced a gradable answer. Differs between arms. |
| `accuracy` | `correct / total`. |

## `cross-factor.md`

Produced only when a static/dynamic pair is requested. Splits every prediction
carrying both factors at each factor's median and compares the two cells where
the factors disagree, answering which kind of complexity dominates. The agreeing
cells are reported for context and are not tested.

## `matched-accuracy.csv`

Accuracy restricted, per model, to programs gradable in every arm that model
ran, so its arms share one denominator. Use it to compare arms; use
`overall-accuracy.csv` to see what each arm actually produced.

| Column | Meaning |
| --- | --- |
| `model_id` | The model and reasoning setting. |
| `arm_id`, `arm_group` | The arm and its label. |
| `arm_count` | How many arms this model ran. A model with fewer arms has an easier matched set and its rows are not comparable to a four-arm model's. |
| `correct` | Correct predictions within the matched set. |
| `total` | Size of the matched set. Identical across one model's arms. |
| `accuracy` | `correct / total`. Empty when no program was gradable in every arm. |
