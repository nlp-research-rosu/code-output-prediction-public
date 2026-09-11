import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "shared" / "analysis" / "scripts" / "analyze.py"
SPEC = importlib.util.spec_from_file_location("shared_prediction_factor_analysis", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
analysis = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = analysis
SPEC.loader.exec_module(analysis)


class AnalysisMarkdownExplanationTests(unittest.TestCase):
    def test_association_table_explains_fields_and_metric(self) -> None:
        result = analysis.SeriesResult(
            "series",
            "model",
            "long-trace-final",
            "dynamic",
            "Omega_hat_StateSize",
            0.75,
            0.01,
            6,
            4,
            10,
            10_000,
            17,
            "OK",
        )
        markdown = analysis.markdown_association_tables([result], "dynamic")
        self.assertIn("how often a failed prediction has a larger metric value", markdown)
        self.assertIn("shuffled correct/wrong labelings", markdown)
        self.assertIn(
            "Greatest number of runtime value cells reachable", markdown
        )

    def test_accuracy_table_explains_cell_format(self) -> None:
        markdown = analysis.markdown_accuracy_table(
            [
                {
                    "arm_id": "long-trace-final",
                    "arm_group": "long-trace-final",
                    "model_id": "model",
                    "correct": "3",
                    "total": "4",
                    "accuracy": "0.75",
                }
            ]
        )
        self.assertIn("correct/eligible (accuracy)", markdown)
        self.assertIn("matched-accuracy.md", markdown)


class ReaderFacingNumberTests(unittest.TestCase):
    def test_permutation_floor_is_reported_as_an_inequality(self) -> None:
        floor = 1 / 10_001
        self.assertEqual(analysis.format_p_value(floor, 10_000), "< 0.0001")
        self.assertEqual(analysis.format_p_value(0.0123, 10_000), "0.0123")

    def test_single_outcome_series_states_the_score_not_a_status_word(self) -> None:
        points = [
            analysis.Point(
                "s", f"pred-{index}", f"p{index}", "", "model", "short-trace-final", "short-trace-final",
                "static", "Omega_CC", float(index), 0,
            )
            for index in range(4)
        ]
        result = analysis.analyze_series(points, 10, 1)
        self.assertEqual(result.status, "ALL_WRONG")
        self.assertIsNone(result.theta_obs)
        self.assertEqual(analysis.format_result(result), "— (0/4 correct)")

    def test_all_correct_series_is_labelled_separately(self) -> None:
        points = [
            analysis.Point(
                "s", f"pred-{index}", f"p{index}", "", "model", "short-trace-final", "short-trace-final",
                "static", "Omega_CC", float(index), 1,
            )
            for index in range(4)
        ]
        self.assertEqual(analysis.analyze_series(points, 10, 1).status, "ALL_CORRECT")


class LogisticRegressionTests(unittest.TestCase):
    def test_reports_odds_per_doubling_and_clear_denominators(self) -> None:
        points = []
        for index in range(60):
            level = index // 10
            wrong = index % 10 < level + 2
            points.append(
                analysis.Point(
                    "dynamic::load",
                    f"prediction-{index}",
                    f"program-{index}",
                    f"execution-{index}",
                    "model",
                    "short-trace-final",
                    "all-arms",
                    "dynamic",
                    "Omega_hat_StateLoad",
                    float(2**level),
                    0 if wrong else 1,
                )
            )
        specification = analysis.LogisticSpecification(
            "state-load",
            "Omega_hat_StateLoad",
            "dynamic",
            "all-arms",
            analysis.CANONICAL_DYNAMIC_ARMS,
        )
        fits = analysis.analyze_logistic_regressions(points, [specification])
        self.assertEqual(len(fits), 1)
        self.assertEqual(fits[0].status, "OK")
        self.assertGreater(fits[0].odds_ratio, 1)
        markdown = analysis.markdown_logistic_regressions(fits)
        self.assertIn("| Model | n | Wrong |", markdown)
        self.assertNotIn("Programs", markdown)

    def test_config_requires_explicit_arm_cohort(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "analyses": [
                            {
                                "regression_id": "load",
                                "metric_name": "Omega_hat_StateLoad",
                                "scope": "dynamic",
                                "arm_group": "all-arms",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "include_arms"):
                analysis.load_logistic_specifications(path)

    def test_config_rejects_noncanonical_arms(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "config.json"
            path.write_text(
                json.dumps(
                    {
                        "analyses": [
                            {
                                "regression_id": "load",
                                "metric_name": "Omega_hat_StateLoad",
                                "scope": "dynamic",
                                "arm_group": "all-arms",
                                "include_arms": ["short-trace-final", "in-loop-prompt"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "non-canonical arms"):
                analysis.load_logistic_specifications(path)


class ExclusionNoteTests(unittest.TestCase):
    def test_note_reports_each_cause_and_warns_that_exclusion_flatters(self) -> None:
        note = "\n".join(
            analysis.markdown_exclusion_note(
                {
                    "excluded_by_model_arm_status": {
                        "model-a::short-trace-final::not_run": 10,
                        "model-a::long-trace-final::no_response": 3,
                    }
                }
            )
        )
        self.assertIn("not** counted as wrong", note)
        self.assertIn("| `model-a` |", note)
        self.assertIn("never sent to the model", note)
        self.assertIn("returned no gradable answer", note)
        self.assertIn("optimistic", note)

    def test_absent_manifest_adds_nothing(self) -> None:
        self.assertEqual(analysis.markdown_exclusion_note(None), [])


class CrossFactorTests(unittest.TestCase):
    def points(self, records):
        result = []
        for index, (model, static_value, dynamic_value, outcome) in enumerate(records):
            for metric, value, scope in (
                ("Omega_CC", static_value, "static"),
                ("Omega_hat_NativeTrace", dynamic_value, "dynamic"),
            ):
                result.append(
                    analysis.Point(
                        f"{model}::{metric}", f"{model}::p{index}", f"p{index}",
                        f"e{index}", model, "short-trace-final", "short-trace-final", scope, metric,
                        float(value), outcome,
                    )
                )
        return result

    def test_declared_direction_is_negative_when_long_runs_are_harder(self) -> None:
        records = []
        for index in range(10):
            records.append(("m", 1, 100, 0))   # simple source, long run: all wrong
            records.append(("m", 100, 1, 1))   # complex source, short run: all correct
        result = analysis.cross_factor_analysis(
            self.points(records), "Omega_CC", "Omega_hat_NativeTrace", 200, 7
        )[0]
        self.assertEqual(result.status, "OK")
        self.assertAlmostEqual(result.difference, -1.0)
        self.assertLess(result.p_value, 0.05)

    def test_thresholds_are_shared_across_models(self) -> None:
        records = [("a", 1, 100, 0), ("a", 100, 1, 1), ("b", 1, 100, 1), ("b", 100, 1, 0)]
        results = analysis.cross_factor_analysis(
            self.points(records), "Omega_CC", "Omega_hat_NativeTrace", 50, 7
        )
        self.assertEqual({r.static_threshold for r in results}, {50.5})
        self.assertEqual({r.dynamic_threshold for r in results}, {50.5})

    def test_missing_disagreeing_cell_is_reported_not_tested(self) -> None:
        records = [("m", 1, 1, 1), ("m", 100, 100, 0)]
        result = analysis.cross_factor_analysis(
            self.points(records), "Omega_CC", "Omega_hat_NativeTrace", 50, 7
        )[0]
        self.assertEqual(result.status, "NO_DISAGREEING_CELL")
        self.assertIsNone(result.p_value)
        self.assertIn("one cell is empty", analysis.markdown_cross_factor([result]))


class ArmCoverageTests(unittest.TestCase):
    def test_partial_pooling_is_called_out(self) -> None:
        points = [
            analysis.Point(
                f"{model}::m", f"{model}::{arm}", "p", "e", model, arm, "all-arms",
                "dynamic", "Omega_hat_Assign", 1.0, 1,
            )
            for model, arms in (("wide", ["short-trace-final", "long-trace-final", "inside-loop-state"]), ("narrow", ["short-trace-final"]))
            for arm in arms
        ]
        note = "\n".join(
            analysis.coverage_note(
                analysis.arm_coverage(points), "dynamic", "all-arms", ["narrow", "wide"]
            )
        )
        self.assertIn("`narrow` pools 1 of 3 arms", note)
        self.assertNotIn("`wide` pools", note)

    def test_equal_coverage_adds_no_note(self) -> None:
        points = [
            analysis.Point(
                f"{model}::m", f"{model}::short", "p", "e", model, "short-trace-final",
                "all-arms", "dynamic", "Omega_hat_Assign", 1.0, 1,
            )
            for model in ("a", "b")
        ]
        self.assertEqual(
            analysis.coverage_note(
                analysis.arm_coverage(points), "dynamic", "all-arms", ["a", "b"]
            ),
            [],
        )


class MetricMatrixTests(unittest.TestCase):
    def result(self, model: str, metric: str, theta: float, p_value: float) -> object:
        return analysis.SeriesResult(
            f"{model}::{metric}",
            model,
            "all-arms",
            "dynamic",
            metric,
            theta,
            p_value,
            6,
            4,
            10,
            10_000,
            17,
            "OK",
        )

    def test_rows_are_ordered_by_cross_model_support(self) -> None:
        markdown = analysis.markdown_metric_matrix(
            [
                self.result("a", "Omega_hat_Loop", 0.49, 0.60),
                self.result("b", "Omega_hat_Loop", 0.47, 0.70),
                self.result("a", "Omega_hat_StateSize", 0.86, 0.001),
                self.result("b", "Omega_hat_StateSize", 0.77, 0.002),
            ]
        )
        rows = [line for line in markdown.splitlines() if line.startswith("| `Omega")]
        self.assertIn("Omega_hat_StateSize", rows[0])
        self.assertIn("2/2", rows[0])
        self.assertIn("Omega_hat_Loop", rows[1])
        self.assertIn("0/2", rows[1])

    def test_only_supported_cells_are_bold(self) -> None:
        markdown = analysis.markdown_metric_matrix(
            [
                self.result("a", "Omega_hat_Assign", 0.64, 0.001),
                self.result("b", "Omega_hat_Assign", 0.64, 0.900),
            ]
        )
        row = next(line for line in markdown.splitlines() if line.startswith("| `Omega"))
        self.assertIn("**theta=0.64<br>p 0.0010<br>n=10**", row)
        self.assertIn("| theta=0.64<br>p 0.9000<br>n=10 |", row)
        self.assertIn("1/2", row)

    def test_cells_define_theta_p_and_measured_over_eligible(self) -> None:
        results = [self.result("a", "Omega_hat_Assign", 0.64, 0.001)]
        totals = {("dynamic", "all-arms", "a"): 16}
        markdown = analysis.markdown_metric_matrix(
            results, eligible_totals=totals
        )
        self.assertIn("theta=0.64<br>p 0.0010<br>n=10/16", markdown)
        self.assertIn("`n=measured/eligible`", markdown)
        self.assertIn("not distinct programs or executions", markdown)

    def test_eligible_totals_use_all_declared_dynamic_arms(self) -> None:
        results = [self.result("a", "Omega_hat_Assign", 0.64, 0.001)]
        manifest = {
            "arm_labels": {
                arm: arm for arm in analysis.CANONICAL_DYNAMIC_ARMS
            },
            "dynamic_pooling": {
                "arms": list(analysis.CANONICAL_DYNAMIC_ARMS)
            },
            "included_by_model_arm": {
                "a::short-trace-final": 8,
                "a::long-trace-final": 7,
                "a::inside-loop-state": 6,
                "a::post-loop-state": 5,
            },
        }
        totals = analysis.metric_matrix_eligible_totals(results, manifest)
        self.assertEqual(totals[("dynamic", "all-arms", "a")], 26)

    def test_unadjusted_single_model_support_is_called_weak(self) -> None:
        markdown = analysis.markdown_metric_matrix(
            [self.result("a", "Omega_hat_Assign", 0.64, 0.001)]
        )
        self.assertIn("unadjusted", markdown)
        self.assertIn("weak evidence", markdown)
        self.assertIn("one model out of 1", markdown)


class MeasurementCoverageTests(unittest.TestCase):
    def test_explains_cells_and_unavailable_reasons(self) -> None:
        manifest = {
            "metric_measurement_coverage": {
                "unit": "program profiles",
                "records": [
                    {
                        "arm_id": "short-trace-final",
                        "metric_name": "Omega_hat_StateSize",
                        "measured": 8,
                        "selected_profiles": 10,
                        "unavailable": 2,
                        "unavailable_by_reason": {
                            "STATE_TRAVERSAL_WORK_LIMIT": 2
                        },
                    }
                ],
                "reason_definitions": {
                    "STATE_TRAVERSAL_WORK_LIMIT": "Exact traversal exceeded its limit."
                },
                "notes": [],
            }
        }
        markdown = analysis.markdown_measurement_coverage(manifest)
        assert markdown is not None
        self.assertIn("`measured / selected (coverage)`", markdown)
        self.assertIn("8 / 10 (80.0%)", markdown)
        self.assertIn(
            "measurement that failed", " ".join(markdown.split())
        )
        self.assertIn("Exact traversal exceeded its limit.", markdown)


class MatchedCohortAccuracyTests(unittest.TestCase):
    def build(self, records: list[tuple[str, str, str, int]]) -> list[object]:
        return [
            analysis.Point(
                f"{model}::{arm}::Omega_CC",
                f"{model}::{arm}::{program}",
                program,
                f"{program}::{arm}",
                model,
                arm,
                arm,
                "static",
                "Omega_CC",
                1.0,
                outcome,
            )
            for model, arm, program, outcome in records
        ]

    def test_matched_cohort_holds_the_program_set_fixed(self) -> None:
        rows = analysis.matched_accuracy_rows(
            self.build(
                [
                    ("model", "short-trace-final", "p1", 1),
                    ("model", "short-trace-final", "p2", 1),
                    ("model", "short-trace-final", "p3", 0),
                    ("model", "long-trace-final", "p1", 1),
                    ("model", "long-trace-final", "p2", 0),
                ]
            )
        )
        by_arm = {row["arm_id"]: row for row in rows}
        self.assertEqual(by_arm["short-trace-final"]["total"], "2")
        self.assertEqual(by_arm["short-trace-final"]["correct"], "2")
        self.assertEqual(by_arm["long-trace-final"]["total"], "2")
        self.assertEqual(by_arm["long-trace-final"]["correct"], "1")
        self.assertEqual(by_arm["short-trace-final"]["arm_count"], "2")

    def test_matched_cohort_is_computed_per_model(self) -> None:
        rows = analysis.matched_accuracy_rows(
            self.build(
                [
                    ("a", "short-trace-final", "p1", 1),
                    ("a", "long-trace-final", "p1", 0),
                    ("b", "short-trace-final", "p1", 1),
                    ("b", "short-trace-final", "p2", 1),
                ]
            )
        )
        totals = {(row["model_id"], row["arm_id"]): row["total"] for row in rows}
        self.assertEqual(totals[("a", "short-trace-final")], "1")
        self.assertEqual(totals[("b", "short-trace-final")], "2")
        self.assertEqual({row["arm_count"] for row in rows if row["model_id"] == "b"}, {"1"})

    def test_empty_matched_cohort_says_no_data(self) -> None:
        markdown = analysis.markdown_matched_accuracy_table(
            analysis.matched_accuracy_rows(
                self.build(
                    [
                        ("model", "short-trace-final", "p1", 1),
                        ("model", "long-trace-final", "p2", 0),
                    ]
                )
            )
        )
        self.assertIn("no data", markdown)

    def test_matched_table_warns_that_it_drops_ungradable_programs(self) -> None:
        markdown = analysis.markdown_matched_accuracy_table(
            analysis.matched_accuracy_rows(
                self.build([("model", "short-trace-final", "p1", 1), ("model", "long-trace-final", "p1", 0)])
            )
        )
        self.assertIn("hardest programs", markdown)
        self.assertIn("1 programs across 2 arms", markdown)

    def test_pooled_dynamic_series_allows_shared_execution_across_predictions(self) -> None:
        points = [
            analysis.Point(
                "series",
                f"prediction-{index}",
                "program",
                "shared-execution",
                "model",
                arm,
                "all-arms",
                "dynamic",
                "Omega_hat_StateSize",
                42.0,
                outcome,
            )
            for index, (arm, outcome) in enumerate(
                (("inside-loop-state", 1), ("post-loop-state", 0)), start=1
            )
        ]
        analysis.validate_points(points)

    def test_dynamic_series_rejects_noncanonical_arm(self) -> None:
        point = analysis.Point(
            "series",
            "prediction",
            "program",
            "execution",
            "model",
            "in-loop-prompt",
            "all-arms",
            "dynamic",
            "Omega_hat_StateSize",
            42.0,
            1,
        )
        with self.assertRaisesRegex(ValueError, "non-canonical arm"):
            analysis.validate_points([point])

    def test_manifest_requires_four_canonical_dynamic_arms(self) -> None:
        point = analysis.Point(
            "series",
            "prediction",
            "program",
            "execution",
            "model",
            "short-trace-final",
            "all-arms",
            "dynamic",
            "Omega_hat_StateSize",
            42.0,
            1,
        )
        manifest = {
            "dynamic_pooling": {
                "arms": [
                    "short-trace-final",
                    "long-trace-final",
                    "inside-loop-state",
                    "in-loop-prompt",
                    "post-loop-state",
                    "out-loop-prompt",
                ]
            }
        }
        with self.assertRaisesRegex(ValueError, "dynamic_pooling.arms"):
            analysis.validate_dynamic_pooling_manifest([point], manifest)

    def test_shared_execution_requires_one_metric_value(self) -> None:
        points = [
            analysis.Point(
                "series",
                f"prediction-{index}",
                "program",
                "shared-execution",
                "model",
                arm,
                "all-arms",
                "dynamic",
                "Omega_hat_StateSize",
                value,
                outcome,
            )
            for index, (arm, value, outcome) in enumerate(
                (("inside-loop-state", 42.0, 1), ("post-loop-state", 43.0, 0)), start=1
            )
        ]
        with self.assertRaisesRegex(ValueError, "inconsistent values"):
            analysis.validate_points(points)


if __name__ == "__main__":
    unittest.main()
