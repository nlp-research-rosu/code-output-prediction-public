import json
import re
from decimal import Decimal
from typing import Callable


FENCED_RESPONSE = re.compile(
    r"\A\s*```(?:json)?\s*\n(?P<content>.*?)\n?```\s*\Z", re.DOTALL
)


def reject_constant(value: str) -> object:
    raise ValueError(f"Invalid JSON constant: {value}")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json_value(text: str) -> object:
    return json.loads(
        text,
        parse_float=Decimal,
        parse_int=Decimal,
        parse_constant=reject_constant,
        object_pairs_hook=unique_object,
    )


def json_values_equal(left: object, right: object) -> bool:
    if left is None or right is None:
        return left is None and right is None
    if isinstance(left, bool) or isinstance(right, bool):
        return isinstance(left, bool) and isinstance(right, bool) and left == right
    if isinstance(left, Decimal) or isinstance(right, Decimal):
        return (
            isinstance(left, Decimal)
            and isinstance(right, Decimal)
            and left == right
        )
    if isinstance(left, str) or isinstance(right, str):
        return isinstance(left, str) and isinstance(right, str) and left == right
    if isinstance(left, list) or isinstance(right, list):
        return (
            isinstance(left, list)
            and isinstance(right, list)
            and len(left) == len(right)
            and all(
                json_values_equal(left_item, right_item)
                for left_item, right_item in zip(left, right, strict=True)
            )
        )
    if isinstance(left, dict) or isinstance(right, dict):
        return (
            isinstance(left, dict)
            and isinstance(right, dict)
            and set(left) == set(right)
            and all(json_values_equal(left[key], right[key]) for key in left)
        )
    return False


def outputs_equal(prediction: str, oracle: str) -> bool:
    try:
        oracle_value = parse_json_value(oracle)
    except (json.JSONDecodeError, ValueError):
        return prediction.split() == oracle.split()
    try:
        prediction_value = parse_json_value(prediction)
    except (json.JSONDecodeError, ValueError):
        return False
    return json_values_equal(prediction_value, oracle_value)


def invalid_response_candidates(response: str) -> list[str]:
    candidates = [response]
    fenced = FENCED_RESPONSE.fullmatch(response)
    if fenced is not None:
        candidates.append(fenced.group("content"))

    decoder = json.JSONDecoder()
    start = 0
    while True:
        start = response.find("{", start)
        if start == -1:
            break
        try:
            value, _ = decoder.raw_decode(response[start:])
        except json.JSONDecodeError:
            start += 1
            continue
        if (
            isinstance(value, dict)
            and set(value) == {"output"}
            and isinstance(value["output"], str)
        ):
            candidates.append(value["output"])
        start += 1
    return list(dict.fromkeys(candidates))


def classify_response(
    response_status: str,
    prediction: str | None,
    raw_response: str | None,
    oracle: str,
    equivalent: Callable[[str, str], bool] = outputs_equal,
) -> tuple[str, bool]:
    if response_status == "parsed_output":
        correct = prediction is not None and equivalent(prediction, oracle)
        return ("correct_valid" if correct else "wrong_valid"), correct
    if response_status != "invalid_format":
        raise ValueError(f"Cannot classify response status: {response_status}")
    correct = raw_response is not None and any(
        equivalent(candidate, oracle)
        for candidate in invalid_response_candidates(raw_response)
    )
    return ("correct_invalid" if correct else "wrong_invalid"), correct
