#!/usr/bin/env python3
"""Grade completed NetworkX state-prediction sessions into one report input."""

from __future__ import annotations

import json
from pathlib import Path
import sys
from collections import Counter


EXPERIMENT = Path(__file__).resolve().parent
REPOSITORY = EXPERIMENT.parents[1]
sys.path.insert(0, str(REPOSITORY))

import workbench  # noqa: E402
from attempt_selection import load_attempt_selections, selected_session_path  # noqa: E402
from output_grading import classify_response  # noqa: E402


EXPECTED_CONDITIONS = {
    "gpt-5.6-sol-high": {
        "provider_models": {("openai-codex", "gpt-5.6-sol")},
        "thinking": "high",
        "no_reasoning": False,
    },
    "gpt-5.6-sol-off": {
        "provider_models": {("openai-codex", "gpt-5.6-sol")},
        "thinking": "minimal",
        "no_reasoning": True,
    },
    "glm-5.3-high": {
        "provider_models": {
            ("openrouter", "z-ai/glm-5.3"),
            ("zai-coding-cn", "glm-5.3"),
        },
        "thinking": "high",
        "no_reasoning": False,
    },
    "deepseek-v4-pro-0813-off": {
        "provider_models": {("openrouter", "deepseek/deepseek-v4-pro-0813")},
        "thinking": "off",
        "no_reasoning": True,
    },
    "deepseek-v4-pro-0813-high": {
        "provider_models": {("openrouter", "deepseek/deepseek-v4-pro-0813")},
        "thinking": "high",
        "no_reasoning": False,
    },
    "qwen3.8-27b-off": {
        "provider_models": {("openrouter", "qwen/qwen3.8-27b")},
        "thinking": "off",
        "no_reasoning": True,
    },
    "qwen3.8-27b-high": {
        "provider_models": {("openrouter", "qwen/qwen3.8-27b")},
        "thinking": "high",
        "no_reasoning": False,
    },
}
ATTEMPT_SELECTIONS = EXPERIMENT / "analysis/selected-attempts.json"


def audit_session(path: Path) -> dict[str, object]:
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
    providers = {
        event["provider"] for event in events if event.get("type") == "model_change"
    }
    models = {
        event["modelId"] for event in events if event.get("type") == "model_change"
    }
    provider_models = {
        (event["provider"], event["modelId"])
        for event in events
        if event.get("type") == "model_change"
    }
    thinking = {
        event["thinkingLevel"]
        for event in events
        if event.get("type") == "thinking_level_change"
    }
    usage = Counter()
    transport_diagnostics = 0
    assistant_messages = 0
    thinking_blocks = 0
    completed_reasoning_tokens = None
    completed_thinking_blocks = None
    for event in events:
        message = event.get("message")
        if not isinstance(message, dict) or message.get("role") != "assistant":
            continue
        assistant_messages += 1
        thinking_blocks += sum(
            block.get("type") == "thinking"
            for block in message.get("content", [])
            if isinstance(block, dict)
        )
        message_usage = message.get("usage") or {}
        if not message.get("errorMessage") and message.get("stopReason") != "error":
            completed_reasoning_tokens = int(message_usage.get("reasoning", 0))
            completed_thinking_blocks = sum(
                block.get("type") == "thinking"
                for block in message.get("content", [])
                if isinstance(block, dict)
            )
        for field in ("input", "output", "reasoning", "totalTokens"):
            usage[field] += int(message_usage.get(field, 0))
        transport_diagnostics += sum(
            diagnostic.get("type") == "provider_transport_failure"
            for diagnostic in message.get("diagnostics", [])
            if isinstance(diagnostic, dict)
        )
    return {
        "providers": providers,
        "models": models,
        "provider_models": provider_models,
        "thinking": thinking,
        "assistant_messages": assistant_messages,
        "thinking_blocks": thinking_blocks,
        "completed_reasoning_tokens": completed_reasoning_tokens,
        "completed_thinking_blocks": completed_thinking_blocks,
        "usage": usage,
        "transport_diagnostics": transport_diagnostics,
    }


def main() -> None:
    benchmark = workbench.load_benchmark(EXPERIMENT)
    selections = load_attempt_selections(ATTEMPT_SELECTIONS)
    rows = []
    missing = []
    run_audit: dict[str, object] = {}
    for model in benchmark.models:
        model_audit = {
            "native_attempts": 0,
            "selected_predictions": 0,
            "predictions_with_multiple_attempts": 0,
            "statuses": Counter(),
            "provider": set(),
            "provider_model": set(),
            "provider_model_pairs": set(),
            "thinking_level": set(),
            "assistant_messages": 0,
            "thinking_blocks": 0,
            "selected_thinking_blocks": 0,
            "usage": Counter(),
            "sessions_with_zero_reasoning_tokens": 0,
            "selected_sessions_with_zero_reasoning_tokens": 0,
            "selected_completed_predictions": 0,
            "selected_completed_with_thinking": 0,
            "selected_completed_with_positive_reasoning_tokens": 0,
            "recovered_transport_diagnostics": 0,
        }
        for problem in benchmark.problems:
            attempt_root = (
                benchmark.root / "runs" / model.id / Path(problem.id)
            )
            sessions = sorted(attempt_root.glob("r[0-9][0-9][0-9]/session.jsonl"))
            if not sessions:
                missing.append(f"{model.id}/{problem.id}")
                continue
            attempts = []
            attempt_audits = {}
            for session in sessions:
                prediction, response_status = workbench.parse_prediction(session)
                raw_response = workbench.parse_session(session)
                session_audit = audit_session(session)
                attempt_id = session.parent.name
                attempt_audits[attempt_id] = session_audit
                attempts.append(
                    (attempt_id, prediction, response_status, raw_response)
                )
                model_audit["native_attempts"] += 1
                model_audit["statuses"][response_status] += 1
                model_audit["provider"].update(session_audit["providers"])
                model_audit["provider_model"].update(session_audit["models"])
                model_audit["provider_model_pairs"].update(
                    session_audit["provider_models"]
                )
                model_audit["thinking_level"].update(session_audit["thinking"])
                model_audit["assistant_messages"] += session_audit["assistant_messages"]
                model_audit["thinking_blocks"] += session_audit["thinking_blocks"]
                model_audit["usage"].update(session_audit["usage"])
                model_audit["sessions_with_zero_reasoning_tokens"] += (
                    session_audit["usage"]["reasoning"] == 0
                )
                model_audit["recovered_transport_diagnostics"] += session_audit[
                    "transport_diagnostics"
                ]
            if len(attempts) > 1:
                model_audit["predictions_with_multiple_attempts"] += 1
            selected_path = selected_session_path(
                attempt_root, EXPERIMENT, selections
            )
            if selected_path is None:
                selected = next(
                    (attempt for attempt in attempts if attempt[3] is not None),
                    attempts[-1],
                )
            else:
                selected = next(
                    attempt
                    for attempt in attempts
                    if attempt[0] == selected_path.parent.name
                )
            attempt_id, prediction, response_status, raw_response = selected
            selected_audit = attempt_audits[attempt_id]
            model_audit["selected_predictions"] += 1
            model_audit["selected_thinking_blocks"] += (
                selected_audit["completed_thinking_blocks"] or 0
            )
            model_audit["selected_sessions_with_zero_reasoning_tokens"] += (
                (selected_audit["completed_reasoning_tokens"] or 0) == 0
            )
            if response_status != "no_response":
                model_audit["selected_completed_predictions"] += 1
                model_audit["selected_completed_with_thinking"] += bool(
                    selected_audit["completed_thinking_blocks"]
                )
                model_audit[
                    "selected_completed_with_positive_reasoning_tokens"
                ] += (selected_audit["completed_reasoning_tokens"] or 0) > 0
            oracle = (problem.program.parent / "ground-output.txt").read_text(
                encoding="utf-8"
            )
            if response_status in {"parsed_output", "invalid_format"}:
                status, semantic_correct = classify_response(
                    response_status,
                    prediction,
                    raw_response,
                    oracle,
                    lambda left, right: left == right,
                )
            else:
                status = response_status
                semantic_correct = False
            rows.append(
                {
                    "model": model.id,
                    "case_id": Path(problem.id).parts[0],
                    "arm_id": Path(problem.id).parts[1],
                    "prediction_id": f"{model.id}::{problem.id}",
                    "status": status,
                    "attempt_id": attempt_id,
                    "attempts_present": [attempt[0] for attempt in attempts],
                    "semantic_correct": semantic_correct,
                    "prediction": prediction,
                }
            )
        expected = EXPECTED_CONDITIONS[model.id]
        if not model_audit["provider_model_pairs"] or not model_audit[
            "provider_model_pairs"
        ].issubset(expected["provider_models"]):
            raise RuntimeError(f"Unexpected provider/model metadata for {model.id}")
        if model_audit["thinking_level"] != {expected["thinking"]}:
            raise RuntimeError(f"Unexpected thinking metadata for {model.id}")
        if expected["no_reasoning"]:
            zero_reasoning = model_audit[
                "selected_sessions_with_zero_reasoning_tokens"
            ]
            if zero_reasoning != model_audit["selected_predictions"]:
                raise RuntimeError(
                    f"A selected no-reasoning session reported reasoning tokens: {model.id}"
                )
            if model_audit["selected_thinking_blocks"]:
                raise RuntimeError(
                    f"A no-reasoning session contains a thinking block: {model.id}"
                )
        elif model.id in {"glm-5.3-high", "deepseek-v4-pro-0813-high"}:
            completed = model_audit["selected_completed_predictions"]
            if model_audit[
                "selected_completed_with_positive_reasoning_tokens"
            ] != completed:
                raise RuntimeError(
                    f"A selected reasoning session lacks reasoning tokens: {model.id}"
                )
            if model_audit["selected_completed_with_thinking"] != completed:
                raise RuntimeError(
                    f"A selected reasoning session lacks a thinking block: {model.id}"
                )
        run_audit[model.id] = {
            "native_attempts": model_audit["native_attempts"],
            "selected_predictions": model_audit["selected_predictions"],
            "predictions_with_multiple_attempts": model_audit[
                "predictions_with_multiple_attempts"
            ],
            "statuses": dict(sorted(model_audit["statuses"].items())),
            "provider_models": [
                {"provider": provider, "model": provider_model}
                for provider, provider_model in sorted(
                    model_audit["provider_model_pairs"]
                )
            ],
            "pi_thinking_level": expected["thinking"],
            "assistant_messages": model_audit["assistant_messages"],
            "thinking_blocks": model_audit["thinking_blocks"],
            "selected_thinking_blocks": model_audit["selected_thinking_blocks"],
            "usage": dict(model_audit["usage"]),
            "sessions_with_zero_reasoning_tokens": model_audit[
                "sessions_with_zero_reasoning_tokens"
            ],
            "selected_sessions_with_zero_reasoning_tokens": model_audit[
                "selected_sessions_with_zero_reasoning_tokens"
            ],
            "selected_completed_predictions": model_audit[
                "selected_completed_predictions"
            ],
            "selected_completed_with_thinking": model_audit[
                "selected_completed_with_thinking"
            ],
            "selected_completed_with_positive_reasoning_tokens": model_audit[
                "selected_completed_with_positive_reasoning_tokens"
            ],
            "recovered_transport_diagnostics": model_audit[
                "recovered_transport_diagnostics"
            ],
        }
    if missing:
        raise RuntimeError(
            f"Cannot grade an incomplete matrix: {len(missing)} sessions missing; "
            f"first={missing[:3]}"
        )
    output = (
        EXPERIMENT
        / "reports/prediction-factor-analysis/data/graded-predictions.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"schema_version": 1, "rows": rows}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    audit_output = output.with_name("run-audit.json")
    audit_output.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "attempt_policy": "Select the earliest completed assistant response in rNNN order and preserve all native attempts. Only transport failures, timeouts, and no-response attempts may be retried.",
                "transport_note": "provider transport diagnostics recovered inside the same Pi invocation are counted separately and are not benchmark retries",
                "models": run_audit,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"Graded {len(rows)} predictions into {output}")


if __name__ == "__main__":
    main()
