import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from unittest import mock

import workbench
import output_grading
from experiments.lcb_hard_v1_python.analysis import grading
from experiments.lcb_hard_v1_python import grade

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "gpt-5.6-sol-high"


def write_session(path: Path, response: str | None) -> None:
    path.parent.mkdir(parents=True)
    message = {
        "role": "assistant",
        "content": [] if response is None else [{"type": "text", "text": response}],
    }
    if response is None:
        message.update({"stopReason": "error", "errorMessage": "failed"})
    path.write_text(json.dumps({"type": "message", "message": message}) + "\n")


class SemanticOutputTests(unittest.TestCase):
    def test_json_object_order_and_layout_do_not_matter(self) -> None:
        prediction = '{\n  "second": [1, 2], "first": 1.0\n}'
        oracle = '{"first":1,"second":[1,2]}\n'
        self.assertTrue(grading.outputs_equal(prediction, oracle))

    def test_json_number_difference_is_wrong(self) -> None:
        self.assertFalse(grading.outputs_equal('{"value":1.01}', '{"value":1}'))

    def test_json_array_order_is_significant(self) -> None:
        self.assertFalse(grading.outputs_equal('[2,1]', '[1,2]'))

    def test_json_string_whitespace_is_significant(self) -> None:
        self.assertFalse(grading.outputs_equal('"a  b"', '"a b"'))

    def test_plain_text_separator_whitespace_does_not_matter(self) -> None:
        prediction = "  first   second\n\nthird  "
        oracle = "first second third\n"
        self.assertTrue(grading.outputs_equal(prediction, oracle))

    def test_plain_text_token_content_and_order_are_significant(self) -> None:
        self.assertFalse(grading.outputs_equal("second first", "first second\n"))

    def test_invalid_envelope_can_still_be_semantically_correct(self) -> None:
        status, correct = output_grading.classify_response(
            "invalid_format",
            None,
            '{"output":"265"}\n\nExplanation',
            "265\n",
        )
        self.assertEqual(status, "correct_invalid")
        self.assertTrue(correct)

    def test_invalid_envelope_with_wrong_content_stays_wrong(self) -> None:
        status, correct = output_grading.classify_response(
            "invalid_format",
            None,
            '```json\n{"output":"264"}\n```',
            "265\n",
        )
        self.assertEqual(status, "wrong_invalid")
        self.assertFalse(correct)
        self.assertFalse(grading.outputs_equal("first changed", "first second\n"))


class ReportTests(unittest.TestCase):
    def test_accuracy_excludes_ungraded_sessions(self) -> None:
        counts = Counter(
            correct_valid=2,
            correct_invalid=1,
            wrong_valid=1,
            wrong_invalid=3,
            no_response=4,
            not_run=5,
        )
        self.assertAlmostEqual(grade.graded_accuracy(counts), 3 / 16)

    def test_accuracy_is_zero_without_graded_sessions(self) -> None:
        counts = Counter(no_response=1, not_run=3)
        self.assertEqual(grade.graded_accuracy(counts), 0.0)

    def test_invalid_response_candidates_include_fenced_output_wrapper(self) -> None:
        response = '```json\n{"output":"{\\"value\\":1}"}\n```'
        self.assertIn(
            '{"value":1}', output_grading.invalid_response_candidates(response)
        )

    def test_invalid_response_candidates_include_raw_output(self) -> None:
        self.assertIn("42", output_grading.invalid_response_candidates("42"))

    def test_grade_result_enforces_attempted_invariant(self) -> None:
        self.assertEqual(
            grading.GradeResult("not_run", None, False).correct,
            None,
        )
        with self.assertRaises(ValueError):
            grading.GradeResult("not_run", False, False)
        with self.assertRaises(ValueError):
            grading.GradeResult("wrong_valid", None, True)


class SessionSelectionTests(unittest.TestCase):
    def test_direct_checkpoint_object_is_invalid_format(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_directory = Path(directory)
            write_session(
                run_directory / "r001/session.jsonl",
                '{"value":1}',
            )
            prediction, status = grading.select_prediction(run_directory)
        self.assertIsNone(prediction)
        self.assertEqual(status, "invalid_format")

    def test_first_complete_prediction_is_selected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            run_directory = Path(directory)
            write_session(
                run_directory / "r001/session.jsonl",
                '{"output":"old"}',
            )
            write_session(run_directory / "r002/session.jsonl", None)
            write_session(
                run_directory / "r003/session.jsonl",
                '{"output":"new"}',
            )
            prediction, status = grading.select_prediction(run_directory)
        self.assertEqual(prediction, "old")
        self.assertEqual(status, "parsed_output")

    def test_manifest_can_select_a_corrected_later_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_directory = root / "runs/test-model/case/inside-loop-state"
            old = run_directory / "r001/session.jsonl"
            corrected = run_directory / "r002/session.jsonl"
            write_session(old, '{"output":"old"}')
            write_session(corrected, '{"output":"corrected"}')
            selections = {
                ("test-model", "case/inside-loop-state"): (
                    "r002",
                    workbench.sha256_file(corrected),
                )
            }
            with (
                mock.patch.object(grading, "EXPERIMENT_ROOT", root),
                mock.patch.object(
                    grading, "load_attempt_selections", return_value=selections
                ),
            ):
                prediction, status = grading.select_prediction(run_directory)
        self.assertEqual(prediction, "corrected")
        self.assertEqual(status, "parsed_output")

    def test_invalidated_prediction_does_not_fall_back(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_directory = root / "runs/test-model/case/inside-loop-state"
            write_session(
                run_directory / "r001/session.jsonl",
                '{"output":"stale"}',
            )
            invalidated = {
                ("test-model", "case/inside-loop-state"): (
                    "corrected_reasoning_attempt_pending"
                )
            }
            with (
                mock.patch.object(grading, "EXPERIMENT_ROOT", root),
                mock.patch.object(
                    grading,
                    "load_invalidated_predictions",
                    return_value=invalidated,
                ),
            ):
                prediction, status = grading.select_prediction(run_directory)
        self.assertIsNone(prediction)
        self.assertEqual(status, "not_run")

    def test_exhausted_invalidated_prediction_is_no_response(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_directory = root / "runs/test-model/case/inside-loop-state"
            write_session(
                run_directory / "r001/session.jsonl",
                '{"output":"stale"}',
            )
            invalidated = {
                ("test-model", "case/inside-loop-state"): (
                    "corrected_reasoning_transport_attempts_exhausted"
                )
            }
            with (
                mock.patch.object(grading, "EXPERIMENT_ROOT", root),
                mock.patch.object(
                    grading,
                    "load_invalidated_predictions",
                    return_value=invalidated,
                ),
            ):
                prediction, status = grading.select_prediction(run_directory)
        self.assertIsNone(prediction)
        self.assertEqual(status, "no_response")

    def test_current_run_totals_cover_all_cases(self) -> None:
        run_root = ROOT / "experiments/lcb_hard_v1_python/runs" / MODEL_ID
        if not run_root.is_dir():
            self.skipTest("Local model sessions are not available")
        benchmark = workbench.load_benchmark(ROOT / "experiments/lcb_hard_v1_python")
        model = workbench.select_models(benchmark, [MODEL_ID])[0]
        results = grade.aggregate(benchmark, model)
        self.assertEqual(sum(results["short-trace-final"].values()), 283)
        self.assertEqual(sum(results["long-trace-final"].values()), 283)
        self.assertEqual(sum(results["inside-loop-state"].values()), 283)
        self.assertEqual(sum(results["post-loop-state"].values()), 283)


if __name__ == "__main__":
    unittest.main()
