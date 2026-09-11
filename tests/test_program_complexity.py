import unittest
import gzip
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

from experiments.lcb_hard_v1_python.analysis.program_complexity import (
    CPP_METRIC_METHODS,
    PYTHON_METRIC_METHODS,
    build_post_loop_checkpoint_source,
    measure_cpp_static,
    measure_python_dynamic,
    measure_python_static,
    metric_can_reuse,
    resolve_dynamic_target,
    runtime_metric_can_reuse,
    select_programs,
)
from experiments.lcb_hard_v1_python.analysis.python_runtime_metrics import (
    C_STATE_COUNTER,
    discover_scope_names,
    run as run_python_runtime_metrics,
    semantic_size,
)


class PythonRuntimeMeasurementTests(unittest.TestCase):
    def test_discovers_module_parameters_and_initialized_locals(self) -> None:
        scopes = discover_scope_names(
            "import math\nvalue = 1\ndef total(item):\n    result = item\n    return result\n",
            "program.py",
        )
        self.assertEqual(scopes.module, {"math", "value", "total"})
        self.assertEqual(scopes.excluded, {"math", "total"})
        self.assertEqual(scopes.functions[("total", 3)], {"item", "result"})

    def test_runtime_rows_preserve_alias_state_and_are_deterministic(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            source.write_text(
                "values = []\nalias = values\nvalues.append(1)\nprint(len(values))\n",
                encoding="utf-8",
            )
            artifacts = []
            payloads = []
            for repetition in (1, 2):
                artifact = root / f"repetition-{repetition}.csv.gz"
                result = root / f"repetition-{repetition}.json"
                with redirect_stdout(io.StringIO()):
                    status = run_python_runtime_metrics(
                        source, "program.py", artifact, result
                    )
                self.assertEqual(status, 0)
                artifacts.append(artifact.read_bytes())
                payloads.append(json.loads(result.read_text()))
            self.assertEqual(artifacts[0], artifacts[1])
            self.assertEqual(
                payloads[0]["Omega_hat_NativeTrace"],
                payloads[1]["Omega_hat_NativeTrace"],
            )
            self.assertEqual(
                payloads[0]["Omega_hat_StateLoad"],
                payloads[1]["Omega_hat_StateLoad"],
            )
            self.assertEqual(payloads[0]["Omega_hat_StateSize"], 2)
            self.assertNotIn("Omega_hat_StateCount", payloads[0])
            rows = gzip.decompress(artifacts[0]).decode("utf-8")
            self.assertIn("mutation_boundary", rows)

    def test_builtin_iterator_counts_as_one_opaque_handle(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            artifact = root / "rows.csv.gz"
            result = root / "result.json"
            source.write_text("values = iter([1])\nprint(next(values))\n", encoding="utf-8")
            with redirect_stdout(io.StringIO()):
                status = run_python_runtime_metrics(
                    source, "program.py", artifact, result
                )
            payload = json.loads(result.read_text())
        self.assertEqual(status, 0)
        self.assertGreater(payload["Omega_hat_NativeTrace"], 0)
        self.assertGreater(payload["Omega_hat_StateSize"], 0)
        self.assertGreater(payload["Omega_hat_StateLoad"], 0)
        self.assertNotIn("Omega_hat_StateCount", payload)
        self.assertIsNone(payload["state_failure"])
        self.assertEqual(payload["state_counter"], "c-iterative-flat-cache-v2")

    def test_c_counter_matches_reference_for_supported_values(self) -> None:
        shared = [1, "ab"]
        values = [shared, shared, {"key": (2, 3)}, range(4)]
        expected_work = [0]
        seen: set[int] = set()
        expected = sum(semantic_size(value, seen, expected_work) for value in values)
        self.assertIsNotNone(C_STATE_COUNTER)
        status, actual, actual_work = C_STATE_COUNTER(values, 0, 100_000)
        self.assertEqual(status, 0)
        self.assertEqual(actual, expected)
        self.assertEqual(actual_work, expected_work[0])

    def test_flat_container_cache_preserves_exact_mutations(self) -> None:
        values_list = list(range(300))
        values_dict = {index: index for index in range(300)}
        values = [values_list, values_dict]

        def assert_matches_reference() -> int:
            expected_work = [0]
            seen: set[int] = set()
            expected = sum(
                semantic_size(value, seen, expected_work) for value in values
            )
            status, actual, actual_work = C_STATE_COUNTER(values, 0, 100_000)
            self.assertEqual(status, 0)
            self.assertEqual(actual, expected)
            self.assertEqual(actual_work, expected_work[0])
            return expected_work[0]

        self.assertIsNotNone(C_STATE_COUNTER)
        expected_work = assert_matches_reference()
        values_list[10] = 999
        values_dict[300] = 300
        values_dict[0] = -1
        expected_work = assert_matches_reference()
        status, _, limited_work = C_STATE_COUNTER(
            values, 0, expected_work - 1
        )
        self.assertEqual(status, 2)
        self.assertEqual(limited_work, expected_work)

        values_list[20] = [1, 2]
        values_dict[1] = {"nested": 3}
        assert_matches_reference()

    def test_incremental_dict_observations_match_reference_rows(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            source.write_text(
                "from collections import defaultdict\n"
                "values = defaultdict(int)\n"
                "for index in range(300):\n"
                "    values[index] = index\n"
                "for index in range(20):\n"
                "    values[index] = index + 1\n"
                "print(len(values))\n",
                encoding="utf-8",
            )
            payloads = {}
            artifacts = {}
            runtime_script = (
                Path(__file__).parents[1]
                / "shared"
                / "metrics"
                / "scripts"
                / "python_runtime_metrics.py"
            )
            for counter in ("python", "c"):
                artifact = root / f"{counter}.csv.gz"
                result = root / f"{counter}.json"
                environment = dict(os.environ)
                environment["PROGRAM_COMPLEXITY_STATE_COUNTER"] = counter
                environment["PROGRAM_COMPLEXITY_STATE_CELL_VISIT_LIMIT"] = "10000000"
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(runtime_script),
                        str(source),
                        "program.py",
                        str(artifact),
                        str(result),
                    ],
                    capture_output=True,
                    env=environment,
                )
                self.assertEqual(completed.returncode, 0, completed.stderr.decode())
                payloads[counter] = json.loads(result.read_text())
                artifacts[counter] = artifact.read_bytes()
        self.assertEqual(artifacts["c"], artifacts["python"])
        for field in (
            "Omega_hat_NativeTrace",
            "Omega_hat_StateSize",
            "Omega_hat_StateLoad",
            "state_cell_visits",
            "raw_observation_rows",
            "raw_artifact_sha256",
        ):
            self.assertEqual(payloads["c"][field], payloads["python"][field])

    def test_deep_builtin_state_does_not_use_python_recursion(self) -> None:
        value: object = 0
        for _ in range(1500):
            value = [value]
        self.assertIsNotNone(C_STATE_COUNTER)
        status, size, visits = C_STATE_COUNTER([value], 0, 10_000)
        self.assertEqual(status, 0)
        self.assertEqual(size, 1501)
        self.assertEqual(visits, 1501)

    def test_comprehension_iterator_is_not_a_program_binding(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            artifact = root / "rows.csv.gz"
            result = root / "result.json"
            source.write_text(
                "values = [item for item in range(2)]\nprint(len(values))\n",
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()):
                status = run_python_runtime_metrics(
                    source, "program.py", artifact, result
                )
            payload = json.loads(result.read_text())
        self.assertEqual(status, 0)
        self.assertGreater(payload["Omega_hat_StateLoad"], 0)
        self.assertNotIn("Omega_hat_StateCount", payload)

    def test_program_defined_slots_are_traversed_without_properties(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            artifact = root / "rows.csv.gz"
            result = root / "result.json"
            source.write_text(
                "class Box:\n"
                "    __slots__ = ('values',)\n"
                "box = Box()\n"
                "box.values = [1, 2]\n"
                "print(len(box.values))\n",
                encoding="utf-8",
            )
            with redirect_stdout(io.StringIO()):
                status = run_python_runtime_metrics(
                    source, "program.py", artifact, result
                )
            payload = json.loads(result.read_text())
        self.assertEqual(status, 0)
        self.assertEqual(payload["Omega_hat_StateSize"], 4)
        self.assertGreater(payload["Omega_hat_StateLoad"], 0)
        self.assertNotIn("Omega_hat_StateCount", payload)


class PythonStaticMeasurementTests(unittest.TestCase):
    def test_separates_if_and_loop_nesting(self) -> None:
        profile = measure_python_static(
            """\
x = 0
for i in range(3):
    if i and x:
        while x < 2:
            x += 1
print(x)
"""
        )
        self.assertEqual(profile["Omega_CC"], 5)
        self.assertEqual(profile["Omega_If"], 1)
        self.assertEqual(profile["Omega_Loop"], 2)
        self.assertGreater(profile["Omega_DD"], 0)

    def test_elif_is_one_conditional_level(self) -> None:
        profile = measure_python_static(
            """\
if a:
    x = 1
elif b:
    x = 2
else:
    x = 3
"""
        )
        self.assertEqual(profile["Omega_If"], 1)
        self.assertEqual(profile["Omega_CC"], 3)

    def test_comprehension_filters_are_conditionals(self) -> None:
        profile = measure_python_static("values = [i for i in range(4) if i % 2]\n")
        self.assertEqual(profile["Omega_If"], 1)
        self.assertEqual(profile["Omega_Loop"], 1)
        self.assertEqual(profile["Omega_CC"], 3)

    def test_short_circuit_expression_contributes_control_flow(self) -> None:
        profile = measure_python_static("a = 1\nb = 2\nvalue = a and b\n")
        self.assertEqual(profile["Omega_CC"], 2)
        self.assertEqual(profile["Omega_DD"], 2)

    def test_loop_else_is_not_nested_inside_the_loop(self) -> None:
        profile = measure_python_static(
            "for value in values:\n"
            "    pass\n"
            "else:\n"
            "    for other in others:\n"
            "        pass\n"
        )
        self.assertEqual(profile["Omega_Loop"], 1)

    def test_dependency_degree_uses_cfg_reaching_bindings(self) -> None:
        profile = measure_python_static(
            "x = 1\nif flag:\n    x = 2\nelse:\n    x = 3\nprint(x)\n"
        )
        self.assertEqual(profile["Omega_DD"], 3)

    def test_dependency_degree_resolves_parameter_shadowing(self) -> None:
        profile = measure_python_static(
            "x = 1\ndef f(x):\n    y = x\n    x = 2\n    return x + y\n"
        )
        self.assertEqual(profile["Omega_DD"], 4)

    def test_dependency_degree_resolves_global_and_nonlocal_writes(self) -> None:
        profile = measure_python_static(
            "x = 0\n"
            "def update_global():\n"
            "    global x\n"
            "    x += 1\n"
            "def outer():\n"
            "    y = 0\n"
            "    def update_nonlocal():\n"
            "        nonlocal y\n"
            "        y += 1\n"
        )
        self.assertEqual(profile["Omega_DD"], 4)

    def test_dependency_degree_accounts_for_loop_back_edges(self) -> None:
        profile = measure_python_static("for i in range(3):\n    x = i\nprint(x)\n")
        self.assertEqual(profile["Omega_DD"], 4)

    def test_loc_counts_multiline_tokens_and_structural_lines(self) -> None:
        profile = measure_python_static(
            'text = """a\nb\n"""\n# comment\n\nvalue = (\n    1\n)\n'
        )
        self.assertEqual(profile["Omega_Loc"], 6)

    def test_python_literals_are_halstead_operands(self) -> None:
        profile = measure_python_static("value = True\n")
        self.assertEqual(profile["Omega_Voc"], 3)

    def test_dynamic_comprehension_counts_taken_iterations_and_targets(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "values = [i if i > 1 else 0 for i in range(4) if i % 2]\n"
                "print(sum(values))\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("3\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_If"], 2)
        self.assertEqual(profile["Omega_hat_Loop"], 1)
        self.assertEqual(profile["Omega_hat_Assign"], 5)

    def test_dynamic_false_if_without_else_is_not_taken(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "if False:\n    print('never')\nprint('ok')\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("ok\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_If"], 0)

    def test_dynamic_loop_else_is_outside_active_loop(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "for first in []:\n"
                "    pass\n"
                "else:\n"
                "    for second in [1]:\n"
                "        print(second)\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("1\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_Loop"], 1)

    def test_dynamic_assignments_cover_python_binding_constructs(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "from contextlib import nullcontext\n"
                "x = 0\n"
                "if (y := 1):\n"
                "    for a, b in [(1, 2), (3, 4)]:\n"
                "        x += a\n"
                "try:\n"
                "    raise ValueError('v')\n"
                "except ValueError as exc:\n"
                "    z = exc\n"
                "with nullcontext(1) as q:\n"
                "    w = q\n"
                "match [1, 2]:\n"
                "    case [m, n]:\n"
                "        t = m + n\n"
                "print(x + y + w + t)\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("9\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_Assign"], 15)

    def test_checkpoint_helpers_do_not_contribute_dynamic_events(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "_lcb_count = [0]\n"
                "value = 0\n"
                "for item in [1, 2]:\n"
                "    _lcb_count[0] += 1\n"
                "    if _lcb_count[0] == 99:\n"
                "        raise SystemExit\n"
                "    value += item\n"
                "print(value)\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("3\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_If"], 0)
        self.assertEqual(profile["Omega_hat_Loop"], 1)
        self.assertEqual(profile["Omega_hat_Assign"], 5)

    def test_generated_post_loop_target_matches_checkpoint_oracle(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source = (
                "total = 0\n"
                "for i in range(1002):\n"
                "    total += i\n"
                "print('final')\n"
            ).encode()
            generated = build_post_loop_checkpoint_source(
                source, target_line=3, fields=["total", "i"]
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text('{"i":1001,"total":501501}\n', encoding="utf-8")
            profile, failure = measure_python_dynamic(
                None,
                input_path,
                oracle,
                timeout=5,
                source_bytes=generated,
                execution_cwd=root,
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_If"], 0)
        self.assertEqual(profile["Omega_hat_Loop"], 1)
        self.assertEqual(profile["Omega_hat_Assign"], 2005)

    def test_generated_post_loop_target_evaluates_recorded_expressions(self) -> None:
        source = (
            b"print('ignored prefix')\n"
            b"state = {'total': 0, 'lookup': {10: 'a', 2: 'b'}}\n"
            b"for i in range(1001):\n"
            b"    state['total'] += i\n"
            b"print('unreachable')\n"
        )
        generated = build_post_loop_checkpoint_source(
            source,
            target_line=4,
            fields=["i", "state['lookup']", "state['total']"],
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            input_path.write_text("", encoding="utf-8")
            oracle.write_text(
                "{\"i\":1000,\"state['lookup']\":{\"10\":\"a\",\"2\":\"b\"},"
                "\"state['total']\":500500}\n",
                encoding="utf-8",
            )
            _, failure = measure_python_dynamic(
                None,
                input_path,
                oracle,
                timeout=5,
                source_bytes=generated,
                execution_cwd=root,
                oracle_mode="last-json-line",
            )
        self.assertIsNone(failure)


class CppStaticMeasurementTests(unittest.TestCase):
    def test_statement_macro_is_expanded_for_control_flow(self) -> None:
        profile, limitations, failures = measure_cpp_static(
            "#include <bits/stdc++.h>\n"
            "#define REP(i, n) for (int i = 0; i < (n); ++i)\n"
            "int main() { int n = 3; REP(i, n) if (i && n) n--; }\n"
        )
        self.assertEqual(failures, [])
        self.assertEqual(profile["Omega_CC"], 4)
        self.assertTrue(any("macro expansion" in item for item in limitations))

    def test_comma_assignment_recovery_does_not_hide_conditional(self) -> None:
        profile, _, failures = measure_cpp_static(
            "template<class X, class Y> bool f(X& x, const Y& y) "
            "{ return (y < x) ? (x=y,1) : 0; }\n"
        )
        self.assertEqual(failures, [])
        self.assertEqual(profile["Omega_CC"], 2)

    def test_dynamic_helpers_are_not_mangled_in_class_methods(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "program.py"
            input_path = root / "input.txt"
            oracle = root / "ground-output.txt"
            source.write_text(
                "class Counter:\n"
                "    def run(self):\n"
                "        total = 0\n"
                "        for value in [1, 2]:\n"
                "            if value:\n"
                "                total += value\n"
                "        return total\n"
                "print(Counter().run())\n",
                encoding="utf-8",
            )
            input_path.write_text("", encoding="utf-8")
            oracle.write_text("3\n", encoding="utf-8")
            profile, failure = measure_python_dynamic(
                source, input_path, oracle, timeout=5
            )
        self.assertIsNone(failure)
        self.assertEqual(profile["Omega_hat_If"], 1)
        self.assertEqual(profile["Omega_hat_Loop"], 1)


class BatchMeasurementTests(unittest.TestCase):
    def test_runtime_reuse_requires_three_matching_raw_artifacts(self) -> None:
        with TemporaryDirectory() as directory:
            benchmark = Path(directory)
            repetitions = []
            for index in range(1, 4):
                artifact = benchmark / f"rows-{index}.csv.gz"
                artifact.write_bytes(b"same")
                repetitions.append(
                    {
                        "raw_artifact": artifact.name,
                        "raw_artifact_sha256": hashlib.sha256(b"same").hexdigest(),
                        "Omega_hat_NativeTrace": 12,
                        "Omega_hat_StateCount": "NOT_MEASURED",
                        "state_failure": {"type": "unsupported"},
                    }
                )
            record = {
                "runtime_measurement": {
                    "runtime": f"CPython {platform.python_version()}",
                    "status": "PARTIAL",
                    "repetitions": repetitions,
                }
            }
            self.assertTrue(
                runtime_metric_can_reuse(
                    record, "Omega_hat_NativeTrace", 12, benchmark
                )
            )
            self.assertTrue(
                runtime_metric_can_reuse(
                    record, "Omega_hat_StateCount", "NOT_MEASURED", benchmark
                )
            )
            (benchmark / "rows-2.csv.gz").write_bytes(b"changed")
            self.assertFalse(
                runtime_metric_can_reuse(
                    record, "Omega_hat_NativeTrace", 12, benchmark
                )
            )

    def test_state_arms_use_their_exact_execution_identity(self) -> None:
        with TemporaryDirectory() as directory:
            benchmark = Path(directory)
            case_root = benchmark / "problems/p/one"
            inside = case_root / "inside-loop-state"
            post = case_root / "post-loop-state"
            inside.mkdir(parents=True)
            post.mkdir(parents=True)
            (inside / "program.py").write_text("print(1)\n", encoding="utf-8")
            (post / "program.py").write_text("print(2)\n", encoding="utf-8")
            for root in (inside, post):
                (root / "input.txt").write_text("", encoding="utf-8")
                (root / "ground-output.txt").write_text("1\n", encoding="utf-8")
            inside_target = resolve_dynamic_target(inside, benchmark, {})
            post_target = resolve_dynamic_target(post, benchmark, {})
        self.assertNotEqual(post_target.execution_id, inside_target.execution_id)
        self.assertEqual(inside_target.source_arm, "inside-loop-state")
        self.assertEqual(post_target.source_arm, "post-loop-state")

    def test_selects_requested_arm_programs_by_language(self) -> None:
        with TemporaryDirectory() as directory:
            benchmark = Path(directory)
            (benchmark / "cases.json").write_text(
                '{"cases": ['
                '{"platform": "p", "question_id": "py", "language": "python"},'
                '{"platform": "p", "question_id": "cc", "language": "cpp20"}'
                "]}",
                encoding="utf-8",
            )
            python_root = benchmark / "problems" / "p" / "py" / "short-trace-final"
            long_root = benchmark / "problems" / "p" / "py" / "long-trace-final"
            cpp_root = benchmark / "problems" / "p" / "cc" / "short-trace-final"
            python_root.mkdir(parents=True)
            long_root.mkdir(parents=True)
            cpp_root.mkdir(parents=True)
            (python_root / "program.py").write_text("print(1)\n", encoding="utf-8")
            (long_root / "program.py").write_text("print(2)\n", encoding="utf-8")
            (cpp_root / "program.cpp").write_text("int main(){}\n", encoding="utf-8")
            self.assertEqual(
                select_programs(benchmark, "short-trace-final", "python", None, []),
                [python_root],
            )
            self.assertEqual(
                select_programs(benchmark, "short-trace-final", "cpp", None, []),
                [cpp_root],
            )
            self.assertEqual(
                select_programs(benchmark, "long-trace-final", "python", None, []),
                [long_root],
            )

    def test_static_reuse_requires_matching_method_and_numeric_value(self) -> None:
        record = {
            "source_sha256": "source",
            "input_sha256": "input",
            "metric_methods": CPP_METRIC_METHODS,
            "metrics": {"Omega_CC": 3},
            "failures": [],
        }
        self.assertTrue(
            metric_can_reuse(
                record,
                "Omega_CC",
                "source",
                "input",
                CPP_METRIC_METHODS,
            )
        )
        self.assertFalse(
            metric_can_reuse(
                record,
                "Omega_CC",
                "source",
                "input",
                PYTHON_METRIC_METHODS,
            )
        )
        record["metric_methods"] = CPP_METRIC_METHODS
        record["metrics"]["Omega_CC"] = "NOT_MEASURED"
        self.assertFalse(
            metric_can_reuse(
                record,
                "Omega_CC",
                "source",
                "input",
                CPP_METRIC_METHODS,
            )
        )


if __name__ == "__main__":
    unittest.main()
