import csv
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "shared" / "charts" / "scripts" / "generate_analysis.py"
SPEC = importlib.util.spec_from_file_location("generate_analysis", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
generate_analysis = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = generate_analysis
SPEC.loader.exec_module(generate_analysis)


POINT_FIELDS = [
    "series_id",
    "prediction_id",
    "program_id",
    "execution_id",
    "model_id",
    "arm_id",
    "arm_group",
    "scope",
    "metric_name",
    "x",
    "y",
]
RESULT_FIELDS = [
    "series_id",
    "model_id",
    "arm_group",
    "scope",
    "metric_name",
    "theta_obs",
    "p_value",
    "n_success",
    "n_failure",
    "n_total",
    "permutations",
    "series_seed",
    "status",
]


def fixture_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    points = []
    results = []
    for scope, group, metric in (
        ("static", "short-trace-final", "Omega_CC"),
        ("dynamic", "all-arms", "Omega_hat_Assign"),
    ):
        for model in ("model-a", "model-b"):
            series_id = f"{scope}__{group}__{metric}__{model}"
            outcomes = (1, 0, 1, 0)
            for index, outcome in enumerate(outcomes):
                arm = (
                    "short-trace-final"
                    if scope == "static"
                    else ("short-trace-final", "long-trace-final", "inside-loop-state", "post-loop-state")[index]
                )
                points.append(
                    {
                        "series_id": series_id,
                        "prediction_id": f"{model}__{arm}__p{index}",
                        "program_id": f"p{index}",
                        "execution_id": f"execution-p{index}" if scope == "dynamic" else "",
                        "model_id": model,
                        "arm_id": arm,
                        "arm_group": group,
                        "scope": scope,
                        "metric_name": metric,
                        "x": index + (10 if outcome == 0 else 0),
                        "y": outcome,
                    }
                )
            results.append(
                {
                    "series_id": series_id,
                    "model_id": model,
                    "arm_group": group,
                    "scope": scope,
                    "metric_name": metric,
                    "theta_obs": "0.875",
                    "p_value": "0.0123",
                    "n_success": 2,
                    "n_failure": 2,
                    "n_total": 4,
                    "permutations": 10000,
                    "series_seed": 17,
                    "status": "OK",
                }
            )
    return points, results


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_fixture(root: Path) -> tuple[Path, Path, Path]:
    points, results = fixture_rows()
    points_path = root / "raw-points.csv"
    results_path = root / "series-results.csv"
    config_path = root / "chart-config.json"
    write_csv(points_path, POINT_FIELDS, points)
    write_csv(results_path, RESULT_FIELDS, results)
    config_path.write_text(
        json.dumps(
            {
                "formats": ["png", "pdf"],
                "target_bins": 2,
                "dpi": 72,
                "log1p_metrics": ["Omega_CC", "Omega_hat_Assign"],
                "model_order": ["model-b", "model-a"],
                "model_labels": {"model-a": "Model A", "model-b": "Model B"},
                "group_labels": {
                    "short-trace-final": "Arm E1 - final output, simple input",
                    "all-arms": "All arms and programs",
                },
                "group_order": ["short-trace-final", "all-arms"],
                "metric_units": {
                    "Omega_CC": "paths",
                    "Omega_hat_Assign": "executed assignments",
                },
                "metric_descriptions": {
                    "Omega_CC": "The number of independent control-flow paths.",
                    "Omega_hat_Assign": "The number of assignments executed.",
                },
            }
        ),
        encoding="utf-8",
    )
    return points_path, results_path, config_path


class GenerateAnalysisTests(unittest.TestCase):
    def test_ordinary_title_wraps_before_metric_comparison(self) -> None:
        self.assertEqual(
            generate_analysis.ordinary_chart_title("Pooled: four arms", "Omega_CC"),
            "Pooled: four arms\nAccuracy versus Omega_CC",
        )

    def test_rejects_noncanonical_dynamic_points(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "raw-points.csv"
            rows, _ = fixture_rows()
            dynamic = next(row for row in rows if row["scope"] == "dynamic")
            dynamic["arm_id"] = "in-loop-prompt"
            write_csv(path, POINT_FIELDS, [dynamic])
            with self.assertRaisesRegex(
                generate_analysis.AnalysisError, "non-canonical arm"
            ):
                generate_analysis.load_points(path)

    def test_generates_static_and_pooled_dynamic_charts(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            output = root / "output"
            summary = generate_analysis.generate(points, results, config, output)
            markdown = (output / "charts.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (output / "chart-manifest.json").read_text(encoding="utf-8")
            )
            expected = [
                output / "charts/static/short-trace-final/omega-cc.png",
                output / "charts/static/short-trace-final/omega-cc.pdf",
                output / "charts/dynamic/all-arms/omega-hat-assign.png",
                output / "charts/dynamic/all-arms/omega-hat-assign.pdf",
                output / "chart-data.csv",
            ]
            self.assertTrue(all(path.is_file() for path in expected))
        self.assertEqual(summary, {"points": 16, "series": 4, "charts": 2})
        self.assertEqual(manifest["schema"], "generate-analysis-charts-v4")
        self.assertEqual(manifest["chart_data_row_count"], 8)
        self.assertEqual(
            manifest["style"]["schema"], "prediction-factor-chart-style-v1"
        )
        self.assertEqual(manifest["style"]["binned_accuracy"]["marker"], "square")
        self.assertEqual(
            manifest["style"]["binned_accuracy"]["color"], "#f05a28"
        )
        self.assertEqual(
            manifest["style"]["prediction_outcome"]["marker"], "circle"
        )
        self.assertEqual(
            manifest["style"]["statistics_annotation"]["placement"],
            "panel-header",
        )
        self.assertEqual(manifest["style"]["statistics_annotation"]["lines"], 2)
        self.assertIn("does not recalculate theta", markdown)
        self.assertIn("## Dynamic metrics", markdown)
        self.assertIn("### All arms and programs", markdown)
        self.assertIn("zero-safe log1p spacing", markdown)

    def test_multi_source_config_selects_static_and_all_arm_dynamic(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results = fixture_rows()
            static_points = [row for row in points if row["scope"] == "static"]
            dynamic_points = [row for row in points if row["scope"] == "dynamic"]
            static_results = [row for row in results if row["scope"] == "static"]
            dynamic_results = [row for row in results if row["scope"] == "dynamic"]
            write_csv(root / "static-points.csv", POINT_FIELDS, static_points)
            write_csv(root / "static-results.csv", RESULT_FIELDS, static_results)
            write_csv(root / "dynamic-points.csv", POINT_FIELDS, dynamic_points)
            write_csv(root / "dynamic-results.csv", RESULT_FIELDS, dynamic_results)
            config = root / "chart-config.json"
            config.write_text(
                json.dumps(
                    {
                        "formats": ["png"],
                        "dpi": 72,
                        "target_bins": 2,
                        "analysis_sources": [
                            {
                                "name": "primary-static",
                                "points": "static-points.csv",
                                "series_results": "static-results.csv",
                                "include_scopes": ["static"],
                            },
                            {
                                "name": "all-arm-dynamic",
                                "points": "dynamic-points.csv",
                                "series_results": "dynamic-results.csv",
                                "include_scopes": ["dynamic"],
                                "include_groups": ["all-arms"],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            output = root / "output"
            summary = generate_analysis.generate(None, None, config, output)
            manifest = json.loads(
                (output / "chart-manifest.json").read_text(encoding="utf-8")
            )
        self.assertEqual(summary, {"points": 16, "series": 4, "charts": 2})
        self.assertEqual(
            [source["name"] for source in manifest["analysis_sources"]],
            ["primary-static", "all-arm-dynamic"],
        )

    def test_log1p_ticks_keep_zero_and_original_units(self) -> None:
        self.assertEqual(generate_analysis.log1p_ticks(0, 0), [0.0])
        ticks = generate_analysis.log1p_ticks(0, 1000)
        self.assertEqual(ticks[0], 0.0)
        self.assertLessEqual(len(ticks), 5)
        self.assertEqual(generate_analysis.format_tick(1000), "1k")
        self.assertEqual(generate_analysis.format_tick(5_000_000), "5M")

    def test_log1p_metric_rejects_negative_values(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            rows = read_csv(points)
            rows[0]["x"] = "-1"
            write_csv(points, POINT_FIELDS, rows)
            with self.assertRaisesRegex(generate_analysis.AnalysisError, "negative"):
                generate_analysis.generate(points, results, config, root / "output")

    def test_results_must_match_point_counts(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            rows = read_csv(results)
            rows[0]["n_failure"] = "3"
            write_csv(results, RESULT_FIELDS, rows)
            with self.assertRaisesRegex(
                generate_analysis.AnalysisError, "result counts do not match"
            ):
                generate_analysis.generate(points, results, config, root / "output")

    def test_result_metadata_must_match_points(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            rows = read_csv(results)
            rows[0]["metric_name"] = "different"
            write_csv(results, RESULT_FIELDS, rows)
            with self.assertRaisesRegex(
                generate_analysis.AnalysisError, "result metadata does not match"
            ):
                generate_analysis.generate(points, results, config, root / "output")

    def test_series_sets_must_match(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            rows = read_csv(results)
            write_csv(results, RESULT_FIELDS, rows[1:])
            with self.assertRaisesRegex(generate_analysis.AnalysisError, "series mismatch"):
                generate_analysis.generate(points, results, config, root / "output")

    def test_outputs_are_byte_stable(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points, results, config = write_fixture(root)
            output = root / "output"
            generate_analysis.generate(points, results, config, output)
            first = {
                path.relative_to(output): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
            generate_analysis.generate(points, results, config, output)
            second = {
                path.relative_to(output): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
        self.assertEqual(first, second)

    def test_logistic_source_replaces_normal_chart_at_same_path(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            points_path, results_path, config_path = write_fixture(root)
            ordinary_points = read_csv(points_path)
            selected = [row for row in ordinary_points if row["scope"] == "dynamic"]
            logistic_points = []
            logistic_results = []
            logistic_curves = []
            for model in ("model-a", "model-b"):
                model_points = [row for row in selected if row["model_id"] == model]
                for row in model_points:
                    logistic_points.append(
                        {
                            "regression_id": "state-load",
                            "prediction_id": row["prediction_id"],
                            "program_id": row["program_id"],
                            "execution_id": row["execution_id"],
                            "model_id": model,
                            "arm_id": row["arm_id"],
                            "arm_group": "all-arms",
                            "scope": "dynamic",
                            "metric_name": "Omega_hat_Assign",
                            "x": str(float(row["x"]) + 1),
                            "wrong": str(1 - int(row["y"])),
                        }
                    )
                logistic_results.append(
                    {
                        "regression_id": "state-load",
                        "model_id": model,
                        "arm_group": "all-arms",
                        "scope": "dynamic",
                        "metric_name": "Omega_hat_Assign",
                        "included_arms": "short-trace-final,long-trace-final,inside-loop-state,post-loop-state",
                        "n": 4,
                        "n_wrong": 2,
                        "beta0": -1,
                        "beta1": 0.5,
                        "se_beta1": 0.2,
                        "odds_ratio": 1.6487,
                        "ci_low": 1.1,
                        "ci_high": 2.2,
                        "p_value": 0.02,
                        "status": "OK",
                    }
                )
                for index, (x, probability, low, high) in enumerate(
                    ((1, 0.2, 0.1, 0.3), (4, 0.4, 0.25, 0.55), (16, 0.65, 0.45, 0.8))
                ):
                    logistic_curves.append(
                        {
                            "regression_id": "state-load",
                            "model_id": model,
                            "arm_group": "all-arms",
                            "scope": "dynamic",
                            "metric_name": "Omega_hat_Assign",
                            "grid_index": index,
                            "x": x,
                            "p_wrong": probability,
                            "ci_low": low,
                            "ci_high": high,
                        }
                    )
            write_csv(
                root / "logistic-points.csv",
                list(generate_analysis.LOGISTIC_POINT_FIELDS),
                logistic_points,
            )
            write_csv(
                root / "logistic-results.csv",
                list(generate_analysis.LOGISTIC_RESULT_FIELDS),
                logistic_results,
            )
            write_csv(
                root / "logistic-curves.csv",
                list(generate_analysis.LOGISTIC_CURVE_FIELDS),
                logistic_curves,
            )
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["logistic_regression_sources"] = [
                {
                    "name": "state-load",
                    "points": "logistic-points.csv",
                    "results": "logistic-results.csv",
                    "curves": "logistic-curves.csv",
                }
            ]
            config_path.write_text(json.dumps(config), encoding="utf-8")
            output = root / "output"
            summary = generate_analysis.generate(
                points_path, results_path, config_path, output
            )
            markdown = (output / "charts.md").read_text(encoding="utf-8")
            manifest = json.loads(
                (output / "chart-manifest.json").read_text(encoding="utf-8")
            )
            logistic_chart_exists = (
                output / "charts/dynamic/all-arms/omega-hat-assign.png"
            ).is_file()
            first = {
                path.relative_to(output): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
            generate_analysis.generate(points_path, results_path, config_path, output)
            second = {
                path.relative_to(output): path.read_bytes()
                for path in output.rglob("*")
                if path.is_file()
            }
        self.assertEqual(summary["charts"], 2)
        self.assertTrue(logistic_chart_exists)
        self.assertEqual(manifest["logistic_chart_data_row_count"], 4)
        self.assertEqual(
            manifest["logistic_regression_sources"][0]["points_file"],
            "logistic-points.csv",
        )
        self.assertIn("Logistic error-probability charts", markdown)
        self.assertIn(
            "Pooled: short-trace-final, long-trace-final, inside-loop-state, post-loop-state",
            markdown,
        )
        self.assertIn("`n` is the number of pooled", markdown)
        self.assertNotIn("Unique programs", markdown)
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
