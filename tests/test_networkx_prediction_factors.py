from experiments.networkx_network_simplex_state_prediction.analysis import (
    prediction_factors,
)


def test_numeric_measurement_value_keeps_exact_and_lower_bound_rows():
    assert prediction_factors.numeric_measurement_value(
        {"status": "MEASURED", "value_relation": "=", "value": "42"}
    ) == "42"
    assert prediction_factors.numeric_measurement_value(
        {"status": "NOT_MEASURED", "value_relation": "", "value": ""}
    ) is None
    assert prediction_factors.numeric_measurement_value(
        {"status": "LOWER_BOUND", "value_relation": ">=", "value": "42"}
    ) == "42"
