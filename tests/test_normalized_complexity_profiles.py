import csv
import importlib.util
import io
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "shared"
    / "metrics"
    / "scripts"
    / "normalize_profiles.py"
)
SPEC = importlib.util.spec_from_file_location("normalize_complexity_profiles", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
NORMALIZER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = NORMALIZER
SPEC.loader.exec_module(NORMALIZER)

CONFIGS = {
    "classic_algorithms_state_prediction": 120,
    "codecontests_reasoning_state_prediction": 88,
    "lcb_hard_v1_python": 1132,
    "lcb_hard_v1_cpp": 140,
    "networkx_network_simplex_state_prediction": 120,
}


def config_path(experiment: str) -> Path:
    return (
        ROOT
        / "experiments"
        / experiment
        / "measurements"
        / "program-complexity"
        / "normalized-profiles-config.json"
    )


def generated_rows(experiment: str):
    output, manifest = NORMALIZER.generate(config_path(experiment))
    rows = list(csv.DictReader(io.StringIO(output.decode("utf-8"))))
    return output, json.loads(manifest), rows


def test_all_benchmarks_share_one_current_normalized_schema():
    observed_headers = set()
    for experiment, execution_count in CONFIGS.items():
        output, manifest, rows = generated_rows(experiment)
        package = config_path(experiment).parent
        assert (package / "normalized-profiles.csv").read_bytes() == output
        assert (
            package / "normalized-profiles-manifest.json"
        ).read_text(encoding="utf-8") == json.dumps(
            manifest, indent=2, sort_keys=True
        ) + "\n"
        observed_headers.add(tuple(rows[0].keys()))
        assert len(rows) == execution_count * len(NORMALIZER.METRICS)
        assert manifest["execution_profile_count"] == execution_count
        assert manifest["row_count"] == len(rows)
        assert manifest["columns"] == list(NORMALIZER.COLUMNS)
        assert manifest["status_vocabulary"] == list(NORMALIZER.STATUSES)
    assert observed_headers == {NORMALIZER.COLUMNS}


def test_normalized_values_statuses_and_identities_are_explicit():
    for experiment in CONFIGS:
        _, _, rows = generated_rows(experiment)
        metric_counts: dict[tuple[str, str, str], int] = {}
        for row in rows:
            assert row["schema_version"] == NORMALIZER.SCHEMA_VERSION
            assert row["benchmark"] == experiment
            assert row["arm"] in NORMALIZER.ARMS
            assert row["language"] in {"python", "cpp"}
            assert row["metric"] in NORMALIZER.METRICS
            assert row["status"] in NORMALIZER.STATUSES
            assert row["execution_id"].startswith("sha256:")
            assert len(row["execution_id"]) == len("sha256:") + 64
            assert row["adapter"]
            assert row["adapter_version"]
            assert row["runtime"]
            assert int(row["repetitions"]) >= 1
            if row["status"] in {"MEASURED", "LOWER_BOUND"}:
                assert int(row["value"]) >= 0
                assert row["not_measured_reason"] == ""
                assert row["value_relation"] == (
                    ">=" if row["status"] == "LOWER_BOUND" else "="
                )
            else:
                assert row["value"] == ""
                assert row["value_relation"] == ""
                assert row["not_measured_reason"]
            key = (row["problem"], row["arm"], row["metric"])
            metric_counts[key] = metric_counts.get(key, 0) + 1
        assert set(metric_counts.values()) == {1}


def test_manifest_coverage_matches_normalized_rows():
    for experiment in CONFIGS:
        _, manifest, rows = generated_rows(experiment)
        for metric in NORMALIZER.METRICS:
            for status in NORMALIZER.STATUSES:
                expected = sum(
                    row["metric"] == metric and row["status"] == status
                    for row in rows
                )
                assert manifest["coverage"][metric][status] == expected


def test_lcb_python_recovered_values_are_normal_measured_equalities():
    _, manifest, rows = generated_rows("lcb_hard_v1_python")
    dynamic_metrics = {
        "Omega_hat_NativeTrace",
        "Omega_hat_StateSize",
        "Omega_hat_StateLoad",
    }
    assert manifest["numeric_recovery_policy"] == "assume_equal"
    assert not [row for row in rows if row["status"] == "LOWER_BOUND"]
    for metric in dynamic_metrics:
        selected = [row for row in rows if row["metric"] == metric]
        assert sum(row["status"] == "MEASURED" for row in selected) == 1132
        assert sum(row["status"] == "NOT_MEASURED" for row in selected) == 0
        assert all(
            row["value_relation"] == "="
            for row in selected
            if row["status"] == "MEASURED"
        )
