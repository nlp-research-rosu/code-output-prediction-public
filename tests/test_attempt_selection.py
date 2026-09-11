from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from attempt_selection import load_attempt_selections, selected_session_path


class AttemptSelectionTests(unittest.TestCase):
    def test_manifest_selects_and_verifies_session(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            session = experiment / "runs/model/case/arm/r002/session.jsonl"
            session.parent.mkdir(parents=True)
            session.write_text("evidence\n", encoding="utf-8")
            digest = hashlib.sha256(session.read_bytes()).hexdigest()
            manifest = experiment / "analysis/selected-attempts.json"
            manifest.parent.mkdir()
            manifest.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "selections": [
                            {
                                "model_id": "model",
                                "problem_id": "case/arm",
                                "attempt": "r002",
                                "session_sha256": digest,
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            selections = load_attempt_selections(manifest)
            selected = selected_session_path(
                experiment / "runs/model/case/arm",
                experiment,
                selections,
            )
            self.assertEqual(selected, session)

    def test_manifest_rejects_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            experiment = Path(directory)
            session = experiment / "runs/model/case/arm/r002/session.jsonl"
            session.parent.mkdir(parents=True)
            session.write_text("changed\n", encoding="utf-8")
            selections = {("model", "case/arm"): ("r002", "0" * 64)}
            with self.assertRaisesRegex(ValueError, "hash drift"):
                selected_session_path(
                    experiment / "runs/model/case/arm",
                    experiment,
                    selections,
                )


if __name__ == "__main__":
    unittest.main()
