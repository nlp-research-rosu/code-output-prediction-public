#!/usr/bin/env python3
"""Grade the committed CodeContests model sessions into one normalized file."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

EXPERIMENT = Path(__file__).resolve().parent
ROOT = EXPERIMENT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from output_grading import classify_response  # noqa: E402
import workbench  # noqa: E402
from attempt_selection import load_attempt_selections, selected_session_path  # noqa: E402


OUTPUT = (
    EXPERIMENT
    / "reports/prediction-factor-analysis/data/graded-predictions.json"
)
ATTEMPT_SELECTIONS = EXPERIMENT / "analysis/selected-attempts.json"
ARMS = (
    "short-trace-final",
    "long-trace-final",
    "inside-loop-state",
    "post-loop-state",
)
MODELS = {
    "gpt-5.6-sol-high": {
        "provider_models": (("openai-codex", "gpt-5.6-sol"),),
        "thinking": "high",
    },
    "gpt-5.6-sol-off": {
        "provider_models": (("openai-codex", "gpt-5.6-sol"),),
        "thinking": "minimal",
    },
    "glm-5.3-high": {
        "provider_models": (
            ("openrouter", "z-ai/glm-5.3"),
            ("zai-coding-cn", "glm-5.3"),
        ),
        "thinking": "high",
    },
    "deepseek-v4-pro-0813-off": {
        "provider_models": (("openrouter", "deepseek/deepseek-v4-pro-0813"),),
        "thinking": "off",
    },
    "deepseek-v4-pro-0813-high": {
        "provider_models": (("openrouter", "deepseek/deepseek-v4-pro-0813"),),
        "thinking": "high",
    },
    "qwen3.8-27b-off": {
        "provider_models": (("openrouter", "qwen/qwen3.8-27b"),),
        "thinking": "off",
    },
    "qwen3.8-27b-high": {
        "provider_models": (("openrouter", "qwen/qwen3.8-27b"),),
        "thinking": "high",
    },
}
NO_REASONING_MODELS = {
    "gpt-5.6-sol-off",
    "deepseek-v4-pro-0813-off",
    "qwen3.8-27b-off",
}
SEMANTIC_TOKEN = re.compile(r"-?\d+|[A-Za-z]+")


def semantic_tokens(value: str) -> list[str]:
    return SEMANTIC_TOKEN.findall(value)


def semantic_outputs_equal(prediction: str, oracle: str) -> bool:
    return semantic_tokens(prediction) == semantic_tokens(oracle)


def load_session(path: Path, expected: dict[str, object]) -> dict | None:
    entries = [json.loads(line) for line in path.read_text().splitlines()]
    model_changes = [entry for entry in entries if entry.get("type") == "model_change"]
    thinking_changes = [
        entry for entry in entries if entry.get("type") == "thinking_level_change"
    ]
    assistants = [
        entry["message"]
        for entry in entries
        if entry.get("type") == "message"
        and entry.get("message", {}).get("role") == "assistant"
    ]
    if len(model_changes) != 1:
        raise ValueError(f"{path}: expected one model change")
    model_change = model_changes[0]
    provider_model = (model_change.get("provider"), model_change.get("modelId"))
    if provider_model not in expected["provider_models"]:
        raise ValueError(f"{path}: unexpected provider or model")
    if [entry.get("thinkingLevel") for entry in thinking_changes] != [
        expected["thinking"]
    ]:
        raise ValueError(f"{path}: unexpected thinking level")
    return assistants[-1] if assistants else None


def parse_answer(message: dict | None) -> tuple[str, str | None, str, list[str]]:
    if message is None:
        return "no_response", None, "", []
    content = message.get("content", [])
    block_types = [str(block.get("type")) for block in content]
    text = "".join(
        block.get("text", "")
        for block in content
        if block.get("type") == "text"
    )
    if message.get("stopReason") == "error" or message.get("errorMessage"):
        return "no_response", None, text, block_types
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return "invalid_format", None, text, block_types
    if (
        not isinstance(parsed, dict)
        or set(parsed) != {"output"}
        or not isinstance(parsed["output"], str)
    ):
        return "invalid_format", None, text, block_types
    return "parsed_output", parsed["output"], text, block_types


def main() -> None:
    cases = json.loads((EXPERIMENT / "cases.json").read_text())
    selections = load_attempt_selections(ATTEMPT_SELECTIONS)
    rows = []
    missing = set()
    for case in cases:
        problem_id = case["problem_id"]
        for arm in ARMS:
            expected_output = (
                EXPERIMENT / "problems" / problem_id / arm / "ground-output.txt"
            ).read_text()
            for model_id, model_config in MODELS.items():
                attempt_root = (
                    EXPERIMENT
                    / "runs"
                    / model_id
                    / problem_id
                    / arm
                )
                sessions = sorted(
                    attempt_root.glob("r[0-9][0-9][0-9]/session.jsonl")
                )
                selected = selected_session_path(attempt_root, EXPERIMENT, selections)
                session = selected or next(
                    (
                        path
                        for path in sessions
                        if workbench.parse_session(path) is not None
                    ),
                    sessions[-1] if sessions else None,
                )
                if session is None:
                    missing.add((model_id, problem_id, arm))
                    continue
                message = load_session(session, model_config)
                response_status, prediction, response, block_types = parse_answer(
                    message
                )
                usage = message.get("usage", {})
                reasoning_tokens = int(usage.get("reasoning", 0))
                if model_id in NO_REASONING_MODELS:
                    if reasoning_tokens != 0 or "thinking" in block_types:
                        raise ValueError(f"{session}: no-reasoning run contains reasoning")
                elif response_status != "no_response" and (
                    reasoning_tokens <= 0 or "thinking" not in block_types
                ):
                    raise ValueError(f"{session}: reasoning run lacks reasoning evidence")
                if response_status in {"parsed_output", "invalid_format"}:
                    status, semantic_correct = classify_response(
                        response_status,
                        prediction,
                        response,
                        expected_output,
                        semantic_outputs_equal,
                    )
                    _, exact_correct = classify_response(
                        response_status,
                        prediction,
                        response,
                        expected_output,
                        lambda left, right: left == right,
                    )
                else:
                    status = response_status
                    semantic_correct = False
                    exact_correct = False
                rows.append(
                    {
                        "model": model_id,
                        "problem_id": problem_id,
                        "split": case["split"],
                        "rating": case["cf_rating"],
                        "arm_id": arm,
                        "status": status,
                        "prediction": prediction,
                        "expected": expected_output,
                        "semantic_correct": semantic_correct,
                        "exact_correct": exact_correct,
                        "input_tokens": int(usage.get("input", 0)),
                        "output_tokens": int(usage.get("output", 0)),
                        "reasoning_tokens": reasoning_tokens,
                        "provider_cost": float(
                            usage.get("cost", {}).get("total", 0)
                        ),
                    }
                )

    if missing:
        raise ValueError(f"missing prediction cells: {sorted(missing)}")
    rows.sort(key=lambda row: (row["model"], row["problem_id"], row["arm_id"]))
    document = {
        "schema": "codecontests-graded-predictions-v1",
        "experiment": EXPERIMENT.name,
        "models": list(MODELS),
        "arms": list(ARMS),
        "grading": (
            "Ordered integer and word tokens; whitespace and separator "
            "punctuation ignored."
        ),
        "missing_predictions": [
            {"model": model, "problem_id": problem_id, "arm_id": arm}
            for model, problem_id, arm in sorted(missing)
        ],
        "rows": rows,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(document, indent=2) + "\n")
    counts = Counter((row["model"], row["semantic_correct"]) for row in rows)
    collected = Counter(row["model"] for row in rows)
    for model_id in MODELS:
        print(
            f"{model_id}: {counts[(model_id, True)]}/{collected[model_id]} "
            f"correct/collected ({len(cases) * len(ARMS)} planned)"
        )
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
