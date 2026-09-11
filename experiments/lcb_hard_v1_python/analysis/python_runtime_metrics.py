#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[3]
SHARED = (
    ROOT
    / "shared"
    / "metrics"
    / "scripts"
    / "python_runtime_metrics.py"
)
SPEC = importlib.util.spec_from_file_location(
    "shared_python_runtime_metrics", SHARED
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load {SHARED}")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)

run = MODULE.run
main = MODULE.main
discover_scope_names = MODULE.discover_scope_names
C_STATE_MODULE = MODULE.C_STATE_MODULE
C_STATE_COUNTER = MODULE.C_STATE_COUNTER
semantic_size = MODULE.semantic_size


if __name__ == "__main__":
    raise SystemExit(main())
