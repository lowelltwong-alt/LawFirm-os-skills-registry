from __future__ import annotations

import json
from pathlib import Path

from lawfirm_os_skills_registry.factory.first_party_reactor import (
    analyze_reference_skill,
    react_to_skill_gaps,
)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r, sort_keys=True) for r in rows) + "\n", encoding="utf-8")


def test_analyze_reference_skill_extracts_patterns_without_retaining_full_text():
    text = """---
name: sample-review
description: Use when reviewing a candidate artifact and producing a structured JSON report.
---

# Sample Review

## Hard rules

Never approve automatically.

## Output contract

```json
{"not_canonical_truth": true}
```

## Edge cases

If missing evidence, abstain.

## Examples

One small example.
"""
    result = analyze_reference_skill(text, source_url="https://example.invalid/skill")
    assert result["record_type"] == "reference_skill_pattern"
    assert result["content_retained"] == "none_full_text_not_stored"
    assert result["features"]["has_output_contract"] is True
    assert result["features"]["has_hard_rules"] is True
    assert result["features"]["has_edge_cases"] is True


def test_react_to_skill_gaps_drafts_first_party_candidate(tmp_path: Path):
    gap_file = tmp_path / "reports" / "skill_gap_candidates.jsonl"
    ref_file = tmp_path / "refs.jsonl"
    drafts_dir = tmp_path / "skills" / "draft"
    reports_dir = tmp_path / "reports"
    evals_dir = tmp_path / "evals" / "reports"

    _write_jsonl(
        gap_file,
        [
            {
                "schema_version": "1.0",
                "record_type": "skill_gap_candidate",
                "candidate_only": True,
                "requires_human_approval": True,
                "gap_id": "gap_evidence_001",
                "observed_pattern": "Reviewers repeatedly reconstruct evidence notes and citation packets by hand.",
                "affected_workflows": ["evidence review", "legal research"],
                "recommended_skill_id": "evidence-packet-builder",
                "skill_need_type": "new_skill",
                "support_count": 5,
                "severity": "medium",
            }
        ],
    )

    _write_jsonl(
        ref_file,
        [
            {
                "record_type": "reference_skill_pattern",
                "name": "reference-one",
                "description": "Use when producing structured review packets with examples and edge cases.",
                "features": {
                    "has_specific_description": True,
                    "has_output_contract": True,
                    "has_hard_rules": True,
                    "has_examples": True,
                    "has_edge_cases": True,
                    "has_progressive_disclosure": False,
                    "has_feedback_loop": False,
                    "mentions_script_execution": False,
                    "mentions_external_fetch": False,
                },
                "pattern_score": 70,
            }
        ],
    )

    report = react_to_skill_gaps(
        gap_file,
        drafts_dir=drafts_dir,
        reports_dir=reports_dir,
        evals_dir=evals_dir,
        reference_jsonl=ref_file,
        allow_network=False,
        max_gaps=1,
        min_support=3,
    )

    assert report["candidate_count"] == 1
    item = report["items"][0]
    assert item["approval_status"] == "candidate_only"
    assert item["next_gate"] == "human_review"
    assert item["network_used"] is False

    skill_path = Path(item["draft_path"])
    skill_md = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    assert "not_canonical_truth" in skill_md
    assert "Do not copy external code" in skill_md
    assert "Do not install this skill" in skill_md
    assert (skill_path / "tests" / "fixtures.jsonl").exists()
    assert Path(item["security_report"]).exists()
    assert Path(item["evaluation_report"]).exists()
    assert Path(item["fixture_report"]).exists()
