import json
import unittest
from pathlib import Path

import workbench

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOTS = {
    "python": (ROOT / "experiments/lcb_hard_v1_python", 283, 67),
    "cpp20": (ROOT / "experiments/lcb_hard_v1_cpp", 35, 315),
}


class HardV1BenchmarkTests(unittest.TestCase):
    def test_problem_count_and_review_coverage(self) -> None:
        for language, (root, case_count, excluded_count) in BENCHMARK_ROOTS.items():
            with self.subTest(language=language):
                metadata = json.loads((root / "cases.json").read_text())
                benchmark = workbench.load_benchmark(root)
                self.assertEqual(len(benchmark.problems), case_count * 4)
                arm_counts = {}
                for problem in benchmark.problems:
                    arm = problem.id.rsplit("/", 1)[-1]
                    arm_counts[arm] = arm_counts.get(arm, 0) + 1
                self.assertEqual(set(arm_counts.values()), {case_count})
                self.assertEqual(metadata["case_count"], case_count)
                self.assertEqual(metadata["problem_count"], case_count * 4)
                self.assertEqual(metadata["reviewed_source_count"], 350)
                self.assertEqual(metadata["excluded_source_count"], excluded_count)
                self.assertEqual({case["language"] for case in metadata["cases"]}, {language})
                exclusions = {
                    exclusion.get("question_id", exclusion.get("case_id")): exclusion
                    for exclusion in metadata["exclusions"]
                }
                self.assertEqual(
                    exclusions["abc376_f"]["reason"],
                    "inside_checkpoint_before_state_update",
                )
                if language == "python":
                    self.assertEqual(
                        exclusions["abc329_e"]["reason"],
                        "nondeterministic_state_output",
                    )
                    self.assertEqual(
                        exclusions["abc375_g"]["reason"],
                        "unseeded_output_randomness",
                    )

    def test_four_arms_are_controlled(self) -> None:
        expected_arms = [
            "short-trace-final",
            "long-trace-final",
            "inside-loop-state",
            "post-loop-state",
        ]
        for language, (root, _, _) in BENCHMARK_ROOTS.items():
            metadata = json.loads((root / "cases.json").read_text())
            self.assertEqual(metadata["arms"], expected_arms)
            for case in metadata["cases"]:
                with self.subTest(language=language, case=case["question_id"]):
                    self.assertEqual(case["short_trace_input"]["origin"], "public")
                    self.assertLessEqual(case["short_trace_input"]["input_bytes"], 480)
                    if "total_loop_entries" in case["long_trace_input"]:
                        self.assertLess(
                            case["short_trace_input"]["total_loop_entries"],
                            case["long_trace_input"]["total_loop_entries"],
                        )
                    self.assertTrue(case["validation"]["clean_sources_identical"])
                    self.assertTrue(case["validation"]["state_inputs_match_long_trace"])
                    self.assertTrue(case["validation"]["state_fields_and_types_match"])
                    self.assertTrue(case["validation"]["state_changes_after_selected_loop"])
                    self.assertTrue(case["validation"]["oracles_stable_across_three_runs"])
                    case_root = root / "problems" / case["platform"] / case["question_id"]
                    output_fields = {
                        "short-trace-final": "short_trace_final_bytes",
                        "long-trace-final": "long_trace_final_bytes",
                        "inside-loop-state": "inside_loop_state_bytes",
                        "post-loop-state": "post_loop_state_bytes",
                    }
                    for arm, field in output_fields.items():
                        oracle = case_root / arm / "ground-output.txt"
                        self.assertEqual(
                            case["outputs"][field],
                            len(oracle.read_bytes()),
                            f"{case['platform']}/{case['question_id']}/{arm}",
                        )


if __name__ == "__main__":
    unittest.main()
