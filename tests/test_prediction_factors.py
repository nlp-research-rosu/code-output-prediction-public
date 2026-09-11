import csv
import hashlib
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch

from experiments.lcb_hard_v1_python import grade
from experiments.lcb_hard_v1_python.analysis import prediction_factors
from experiments.lcb_hard_v1_python.analysis.program_complexity import (
    ALL_DYNAMIC_METRICS,
    STATIC_METRICS,
)


class PredictionFactorPreparationTests(unittest.TestCase):
    def test_keeps_static_arms_and_pools_dynamic_predictions(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            benchmark_root = root / "benchmark"
            normalized_profiles = root / "normalized-profiles.csv"
            for name in ("cases.json", "workbench.toml", "grade.py"):
                path = benchmark_root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(name, encoding="utf-8")
            problems = []
            measurement_rows = []
            for index, arm in enumerate(grade.ARMS, 1):
                problem_root = benchmark_root / "problems" / "p" / "one" / arm
                problem_root.mkdir(parents=True)
                program = problem_root / "program.py"
                program.write_text(f"value = {index}\n", encoding="utf-8")
                problems.append(SimpleNamespace(id=f"p/one/{arm}", program=program))
                source_hash = hashlib.sha256(program.read_bytes()).hexdigest()
                for offset, metric in enumerate(
                    (*STATIC_METRICS, *ALL_DYNAMIC_METRICS)
                ):
                    value = (
                        999
                        if arm == "post-loop-state"
                        and metric == "Omega_hat_StateLoad"
                        else index + offset
                    )
                    measurement_rows.append(
                        {
                            "benchmark": "benchmark",
                            "problem": "p/one",
                            "arm": arm,
                            "language": "python",
                            "source_sha256": source_hash,
                            "input_sha256": f"input-{arm}",
                            "execution_id": f"execution-{arm}",
                            "metric": metric,
                            "value": value,
                            "value_relation": "=",
                            "status": "MEASURED",
                            "not_measured_reason": "",
                        }
                    )
            with normalized_profiles.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(
                    handle, fieldnames=measurement_rows[0], lineterminator="\n"
                )
                writer.writeheader()
                writer.writerows(measurement_rows)
            (root / "normalized-profiles-config.json").write_text(
                json.dumps({"numeric_recovery_policy": "assume_equal"}),
                encoding="utf-8",
            )
            (root / "normalized-profiles-manifest.json").write_text(
                json.dumps(
                    {
                        "numeric_recovery_policy": "assume_equal",
                        "output": {
                            "sha256": hashlib.sha256(
                                normalized_profiles.read_bytes()
                            ).hexdigest()
                        },
                        "config": {
                            "sha256": hashlib.sha256(
                                (
                                    root / "normalized-profiles-config.json"
                                ).read_bytes()
                            ).hexdigest()
                        },
                    }
                ),
                encoding="utf-8",
            )
            retry_root = (
                benchmark_root
                / "runs/model-a/p/one/short-trace-final"
            )
            for repetition in ("r001", "r002"):
                path = retry_root / repetition / "session.jsonl"
                path.parent.mkdir(parents=True)
                path.write_text("{}\n", encoding="utf-8")
            benchmark = SimpleNamespace(
                root=benchmark_root,
                models=[SimpleNamespace(id="model-a")],
                problems=problems,
            )

            def grade_problem(_benchmark, _model, problem):
                if problem.id.endswith("long-trace-final"):
                    return SimpleNamespace(status="no_response", correct=False)
                return SimpleNamespace(status="correct_valid", correct=True)

            with (
                patch.object(
                    prediction_factors.workbench,
                    "load_benchmark",
                    return_value=benchmark,
                ),
                patch.object(
                    prediction_factors.grade,
                    "grade_problem",
                    side_effect=grade_problem,
                ),
            ):
                rows, manifest = prediction_factors.prepare(
                    benchmark_root, normalized_profiles, "python"
                )

        self.assertEqual(
            len(rows),
            3 * len(STATIC_METRICS) + 3 * len(ALL_DYNAMIC_METRICS),
        )
        self.assertEqual(manifest["included_prediction_count"], 3)
        self.assertEqual(manifest["retry_cells_deduplicated"], 1)
        self.assertEqual(
            manifest["excluded_by_model_arm_status"][
                "model-a::long-trace-final::no_response"
            ],
            1,
        )
        loop_row = next(
            row
            for row in rows
            if row["arm_id"] == "inside-loop-state"
            and row["metric_name"] == "Omega_CC"
        )
        self.assertEqual(loop_row["x"], "3")
        self.assertEqual(
            loop_row["prediction_id"], "model-a::p/one/inside-loop-state"
        )
        dynamic_rows = [row for row in rows if row["scope"] == "dynamic"]
        self.assertEqual(
            {row["arm_id"] for row in dynamic_rows},
            {"short-trace-final", "inside-loop-state", "post-loop-state"},
        )
        self.assertEqual({row["arm_group"] for row in dynamic_rows}, {"all-arms"})
        recovered_row = next(
            row
            for row in dynamic_rows
            if row["arm_id"] == "post-loop-state"
            and row["metric_name"] == "Omega_hat_StateLoad"
        )
        self.assertEqual(recovered_row["x"], "999")
        self.assertEqual(
            {row["series_id"] for row in dynamic_rows},
            {
                f"dynamic::model-a::all-arms::{metric}"
                for metric in ALL_DYNAMIC_METRICS
            },
        )
        pooling = manifest["dynamic_pooling"]
        self.assertEqual(
            pooling["arms"],
            [
                "short-trace-final",
                "long-trace-final",
                "inside-loop-state",
                "post-loop-state",
            ],
        )
        self.assertEqual(pooling["prediction_count"], 3)
        self.assertEqual(pooling["distinct_execution_id_count"], 3)
        self.assertEqual(pooling["shared_execution_id_count"], 0)
        self.assertEqual(pooling["predictions_backed_by_shared_execution_ids"], 0)
        coverage = manifest["metric_measurement_coverage"]
        state_load = next(
            record
            for record in coverage["records"]
            if record["arm_id"] == "short-trace-final"
            and record["metric_name"] == "Omega_hat_StateLoad"
        )
        self.assertEqual(state_load["measured"], 1)
        self.assertEqual(state_load["selected_profiles"], 1)

    def test_classifies_adapter_gap_and_state_failure(self) -> None:
        absent = {
            "status": "NOT_REQUESTED",
            "not_measured_reason": "not requested",
        }
        limited = {
            "status": "NOT_MEASURED",
            "not_measured_reason": "STATE_TRAVERSAL_WORK_LIMIT",
        }
        self.assertEqual(
            prediction_factors.measurement_unavailable_reason(absent),
            "ADAPTER_NOT_RUN",
        )
        self.assertEqual(
            prediction_factors.measurement_unavailable_reason(limited),
            "STATE_TRAVERSAL_WORK_LIMIT",
        )

    def test_uses_only_normalized_equality_measurements(self) -> None:
        self.assertEqual(
            prediction_factors.normalized_measurement_value(
                {
                    "status": "MEASURED",
                    "value_relation": "=",
                    "value": "123",
                    "not_measured_reason": "",
                }
            ),
            123,
        )
        with self.assertRaisesRegex(ValueError, "normalized as MEASURED"):
            prediction_factors.normalized_measurement_value(
                {
                    "status": "LOWER_BOUND",
                    "value_relation": ">=",
                    "value": "123",
                    "not_measured_reason": "",
                }
            )


if __name__ == "__main__":
    unittest.main()
