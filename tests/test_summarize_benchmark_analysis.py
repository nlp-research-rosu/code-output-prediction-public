import csv
import hashlib
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = (
    ROOT
    / "shared"
    / "reports"
    / "scripts"
    / "validate_report.py"
)
SPEC = importlib.util.spec_from_file_location("validate_benchmark_report", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)
DESCRIBE_PATH = MODULE_PATH.with_name("describe_chart_data.py")
DESCRIBE_SPEC = importlib.util.spec_from_file_location(
    "describe_benchmark_chart_data", DESCRIBE_PATH
)
assert DESCRIBE_SPEC is not None and DESCRIBE_SPEC.loader is not None
describe = importlib.util.module_from_spec(DESCRIBE_SPEC)
sys.modules[DESCRIBE_SPEC.name] = describe
DESCRIBE_SPEC.loader.exec_module(describe)

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


def write_csv(path: Path, fields: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class SummaryValidatorTests(unittest.TestCase):
    def test_chart_validation_accepts_logistic_replacement(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            ordinary = root / "chart-data.csv"
            logistic = root / "logistic-chart-data.csv"
            fields = ["metric_name", "model_id", "arm_group"]
            write_csv(
                ordinary,
                fields,
                [{"metric_name": "Omega_CC", "model_id": "m", "arm_group": "long-trace-final"}],
            )
            write_csv(
                logistic,
                fields,
                [{"metric_name": "Omega_hat_NativeTrace", "model_id": "m", "arm_group": "all-arms"}],
            )
            expected = [
                validator.Association(
                    "Omega_hat_NativeTrace", "m", "all-arms", "0.75", "0.01", 6, 4, 10
                )
            ]
            validator.validate_chart_data([ordinary, logistic], expected)

    def test_classifies_existing_bin_patterns(self) -> None:
        self.assertEqual(describe.pattern([0.5]), "insufficient bin variation")
        self.assertEqual(describe.pattern([0.5, 0.5]), "flat")
        self.assertEqual(
            describe.pattern([0.8, 0.5, 0.5]), "monotone non-increasing"
        )
        self.assertEqual(
            describe.pattern([0.2, 0.5, 0.8]), "monotone non-decreasing"
        )
        self.assertEqual(describe.pattern([0.5, 0.8, 0.2]), "mixed")

    def test_describes_logistic_replacement_as_wrong_rate(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            results = root / "results.csv"
            ordinary = root / "chart-data.csv"
            logistic = root / "logistic-chart-data.csv"
            write_csv(
                results,
                RESULT_FIELDS,
                [
                    {
                        "series_id": "dynamic-load",
                        "model_id": "model-a",
                        "arm_group": "all-arms",
                        "scope": "dynamic",
                        "metric_name": "Omega_hat_StateLoad",
                        "theta_obs": "0.75",
                        "p_value": "0.01",
                        "n_success": 6,
                        "n_failure": 4,
                        "n_total": 10,
                        "permutations": 10000,
                        "series_seed": 1,
                        "status": "OK",
                    }
                ],
            )
            write_csv(ordinary, ["series_id"], [])
            write_csv(
                logistic,
                [
                    "metric_name",
                    "model_id",
                    "arm_group",
                    "bin_index",
                    "x",
                    "wrong_rate",
                ],
                [
                    {
                        "metric_name": "Omega_hat_StateLoad",
                        "model_id": "model-a",
                        "arm_group": "all-arms",
                        "bin_index": 1,
                        "x": 10,
                        "wrong_rate": 0.1,
                    },
                    {
                        "metric_name": "Omega_hat_StateLoad",
                        "model_id": "model-a",
                        "arm_group": "all-arms",
                        "bin_index": 2,
                        "x": 20,
                        "wrong_rate": 0.4,
                    },
                ],
            )
            summary = describe.describe(results, results, ordinary, logistic)
        self.assertEqual(summary[0]["bin_measure"], "wrong_rate")
        self.assertEqual(summary[0]["pattern"], "monotone non-decreasing")
        self.assertTrue(
            summary[0]["endpoint_direction_consistent_with_failure_at_larger_values"]
        )

    def test_validates_report_scope_associations_and_glossary(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            primary = root / "primary.csv"
            pooled = root / "pooled.csv"
            chart_data = root / "chart-data.csv"
            manifest = root / "chart-manifest.json"
            report = root / "README.md"
            associations = root / "supported-associations.md"
            write_csv(
                primary,
                RESULT_FIELDS,
                [
                    {
                        "series_id": "static",
                        "model_id": "model-a",
                        "arm_group": "long-trace-final",
                        "scope": "static",
                        "metric_name": "Omega_CC",
                        "theta_obs": "0.75",
                        "p_value": "0.01",
                        "n_success": 6,
                        "n_failure": 4,
                        "n_total": 10,
                        "permutations": 10000,
                        "series_seed": 1,
                        "status": "OK",
                    }
                ],
            )
            write_csv(
                pooled,
                RESULT_FIELDS,
                [
                    {
                        "series_id": "dynamic",
                        "model_id": "model-a",
                        "arm_group": "all-arms",
                        "scope": "dynamic",
                        "metric_name": "Omega_hat_NativeTrace",
                        "theta_obs": "0.51",
                        "p_value": "0.2",
                        "n_success": 6,
                        "n_failure": 4,
                        "n_total": 10,
                        "permutations": 10000,
                        "series_seed": 2,
                        "status": "OK",
                    }
                ],
            )
            write_csv(
                chart_data,
                [
                    "series_id",
                    "model_id",
                    "arm_group",
                    "scope",
                    "metric_name",
                    "bin_index",
                ],
                [
                    {
                        "series_id": "static",
                        "model_id": "model-a",
                        "arm_group": "long-trace-final",
                        "scope": "static",
                        "metric_name": "Omega_CC",
                        "bin_index": 1,
                    }
                ],
            )
            manifest.write_text(
                json.dumps(
                    {
                        "chart_data_sha256": hashlib.sha256(
                            chart_data.read_bytes()
                        ).hexdigest()
                    }
                ),
                encoding="utf-8",
            )
            associations.write_text(
                "# Supported associations\n\n"
                "| Metric | Model | Arm group | theta_obs | p | Correct | Wrong | n |\n"
                "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |\n"
                "| Omega_CC | model-a | long-trace-final | 0.75 | 0.0100 | 6 | 4 | 10 |\n\n"
                "`theta_obs`: failure-larger rate. `p`: permutation share. "
                "`Correct` / `Wrong`: predictions carrying a value. "
                "`n`: correct plus wrong.\n",
                encoding="utf-8",
            )
            report.write_text(
                "# Report\n\n"
                "Omega_CC results. See the [shared metric definitions]"
                f"({validator.METRIC_DEFINITIONS_PATH}).\n\n"
                "See [supported associations](supported-associations.md).\n\n"
                "Limits: association is not causation; p-values are unadjusted; "
                "non-significance is not proof of no relationship; measurement coverage "
                "changes coverage; compare only with the same language adapter.\n",
                encoding="utf-8",
            )
            result = validator.validate(
                report, associations, primary, pooled, chart_data, manifest
            )
        self.assertEqual(result, {"supported_associations": 1, "metrics": 2})

    def test_rejects_missing_column_definitions(self) -> None:
        associations = " ".join(
            marker
            for marker in validator.REQUIRED_FIELD_DEFINITIONS
            if marker != "`p`:"
        )
        with self.assertRaisesRegex(
            validator.ValidationError, "lacks a column definition: `p`:"
        ):
            validator.validate_field_definitions(associations)

    def test_rejects_missing_associations_table(self) -> None:
        with self.assertRaisesRegex(
            validator.ValidationError, "table is missing"
        ):
            validator.parse_markdown_table("# Supported associations")

    def test_theta_is_compared_after_rounding_to_the_displayed_precision(self) -> None:
        exact = validator.Association(
            "Omega_CC", "model-a", "long-trace-final", "0.638938580799", "9.999e-05", 6, 4, 10
        )
        displayed = validator.Association(
            "Omega_CC", "model-a", "long-trace-final", "0.64", "< 0.0001", 6, 4, 10
        )
        self.assertEqual(validator.normalized(exact), validator.normalized(displayed))


if __name__ == "__main__":
    unittest.main()
