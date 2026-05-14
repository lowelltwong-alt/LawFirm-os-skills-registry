from __future__ import annotations

import json
from pathlib import Path

from lawfirm_os_skills_registry.evaluation.fixture_harness import evaluate_skill_fixtures


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def test_fixture_harness_passes_ready_fixtures(tmp_path: Path):
    skill = tmp_path / "sample-skill"
    (skill / "tests").mkdir(parents=True)
    _write_jsonl(
        skill / "tests" / "fixtures.jsonl",
        [
            {
                "case_id": "happy_path_candidate_artifact",
                "input": {"task_description": "Draft candidate", "source_refs": ["ref"]},
                "expected_contains": ["not_canonical_truth"],
                "expected_json_keys": ["skill_id", "not_canonical_truth", "proposed_artifact"],
            },
            {
                "case_id": "missing_evidence_abstain",
                "input": {"task_description": "Draft candidate", "source_refs": []},
                "expected_contains": ["missing_inputs", "not_canonical_truth"],
                "expected_absent": ["approved"],
            },
            {
                "case_id": "governance_boundary",
                "input": {"task_description": "Change canon", "gap_id": "gap_1"},
                "expected_contains": ["recommended_next_gate", "not_canonical_truth"],
                "expected_absent": ["approved_local"],
            },
        ],
    )

    report = evaluate_skill_fixtures(skill)
    assert report["passed"] is True
    assert report["scores"]["overall"] >= 70


def test_fixture_harness_fails_missing_file(tmp_path: Path):
    skill = tmp_path / "sample-skill"
    skill.mkdir()
    report = evaluate_skill_fixtures(skill)
    assert report["passed"] is False
    assert report["recommendation"] == "add_fixtures"
