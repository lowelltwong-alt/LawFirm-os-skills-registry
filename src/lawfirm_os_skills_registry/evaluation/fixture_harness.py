from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..util.files import read_jsonl, write_json
from ..util.time import utc_now


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def evaluate_skill_fixtures(skill_dir: str | Path) -> dict[str, Any]:
    """Evaluate whether a skill has useful deterministic test fixtures.

    This harness does not execute the skill or call a model. It checks whether
    the skill package includes enough fixture structure to support future
    behavioral evaluation: happy path, abstention/missing-input path, and
    governance-boundary path.
    """

    root = Path(skill_dir)
    fixture_file = root / "tests" / "fixtures.jsonl"
    errors: list[str] = []
    warnings: list[str] = []

    if not fixture_file.exists():
        return {
            "schema_version": "1.0",
            "generated_at": utc_now(),
            "skill_dir": str(root),
            "fixture_file": str(fixture_file),
            "fixture_count": 0,
            "scores": {
                "fixture_presence": 0,
                "input_specificity": 0,
                "expected_contract": 0,
                "abstention_coverage": 0,
                "boundary_coverage": 0,
                "overall": 0,
            },
            "errors": ["missing tests/fixtures.jsonl"],
            "warnings": [],
            "passed": False,
            "recommendation": "add_fixtures",
        }

    rows = read_jsonl(fixture_file)
    if not rows:
        errors.append("fixtures.jsonl is empty")

    has_happy = False
    has_abstain = False
    has_boundary = False
    expected_contract_cases = 0
    specific_inputs = 0

    for i, row in enumerate(rows, 1):
        case_id = str(row.get("case_id") or "")
        input_obj = row.get("input")
        expected_contains = _as_list(row.get("expected_contains"))
        expected_absent = _as_list(row.get("expected_absent"))
        expected_json_keys = _as_list(row.get("expected_json_keys"))

        if not case_id:
            errors.append(f"fixture {i} missing case_id")
        if not isinstance(input_obj, dict) or not input_obj:
            errors.append(f"fixture {case_id or i} missing non-empty input object")
        else:
            if any(k in input_obj for k in ("task_description", "observed_pattern", "gap_id", "source_refs")):
                specific_inputs += 1

        if not (expected_contains or expected_absent or expected_json_keys):
            errors.append(f"fixture {case_id or i} has no deterministic expectations")

        text = json.dumps(row, sort_keys=True).lower()
        if any(x in text for x in ("happy", "normal", "valid", "candidate_artifact")):
            has_happy = True
        if any(x in text for x in ("missing", "abstain", "insufficient", "no source", "source_refs\": []")):
            has_abstain = True
        if any(x in text for x in ("governance", "boundary", "canon", "approval", "runtime")):
            has_boundary = True
        if expected_json_keys or any("not_canonical_truth" in str(x) for x in expected_contains):
            expected_contract_cases += 1

    fixture_presence = min(100, len(rows) * 34)
    input_specificity = round(100 * specific_inputs / max(1, len(rows)), 2)
    expected_contract = round(100 * expected_contract_cases / max(1, len(rows)), 2)
    abstention_coverage = 100 if has_abstain else 0
    boundary_coverage = 100 if has_boundary else 0
    overall = round(
        0.20 * fixture_presence
        + 0.20 * input_specificity
        + 0.25 * expected_contract
        + 0.20 * abstention_coverage
        + 0.15 * boundary_coverage,
        2,
    )

    if not has_happy:
        warnings.append("no clear happy-path fixture")
    if not has_abstain:
        warnings.append("no missing-input or abstention fixture")
    if not has_boundary:
        warnings.append("no governance-boundary fixture")

    passed = not errors and overall >= 70 and has_abstain and has_boundary
    recommendation = "fixtures_ready" if passed else "improve_fixtures"

    return {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "skill_dir": str(root),
        "fixture_file": str(fixture_file),
        "fixture_count": len(rows),
        "scores": {
            "fixture_presence": fixture_presence,
            "input_specificity": input_specificity,
            "expected_contract": expected_contract,
            "abstention_coverage": abstention_coverage,
            "boundary_coverage": boundary_coverage,
            "overall": overall,
        },
        "errors": errors,
        "warnings": warnings,
        "passed": passed,
        "recommendation": recommendation,
    }


def write_fixture_evaluation(skill_dir: str | Path, out: str | Path) -> dict[str, Any]:
    report = evaluate_skill_fixtures(skill_dir)
    write_json(out, report)
    return report
