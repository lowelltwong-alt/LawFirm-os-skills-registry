from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

POLICY_MARKER_ENV_VAR = "LAWFIRM_OS_VALIDATION_RUNTIME_POLICY"
POLICY_MARKER_VALUE = "skills-registry-validation-runtime-policy.v1"


def pytest_sessionstart(session) -> None:
    import os
    import pytest

    if os.environ.get(POLICY_MARKER_ENV_VAR) == POLICY_MARKER_VALUE:
        return

    pytest.exit(
        "Direct pytest invocation is blocked by the validation runtime policy. "
        "Use `python scripts/run_full_pytest.py` so full and focused tests receive "
        "the configured long timeout ceiling.",
        returncode=4,
    )
