from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.validate_intake_specialist_skill_review import (
    IntakeSpecialistSkillReviewError,
    validate_intake_specialist_skill_review,
)


ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "registry" / "proposed-intake-specialist-skills.json"
VALIDATOR = ROOT / "scripts" / "validate_intake_specialist_skill_review.py"
EXPECTED_SKILLS = {
    "intake-source-grounding-review",
    "labor-employment-party-role-mapper",
    "intake-budget-driver-context-review",
    "carrier-rejection-learning-loop-review",
}


def _proposal_payload() -> dict:
    return json.loads(PROPOSAL.read_text(encoding="utf-8"))


def test_intake_specialist_skill_review_validates() -> None:
    data = validate_intake_specialist_skill_review()

    assert data["status"] == "draft_candidate_only"
    assert data["canonical_authority_allowed"] is False
    assert data["approval_performed"] is False
    assert {skill["skill_id"] for skill in data["skills"]} == EXPECTED_SKILLS


def test_intake_specialist_skill_review_cli_passes() -> None:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert "validation passed" in completed.stdout


def test_draft_skill_metadata_declares_context_discipline() -> None:
    for skill_id in EXPECTED_SKILLS:
        metadata = json.loads(
            (ROOT / "skills" / "draft" / skill_id / "SKILL_METADATA.json").read_text(
                encoding="utf-8"
            )
        )

        assert metadata["lifecycle_state"] == "draft"
        assert metadata["trust_status"] == "draft_candidate_unapproved"
        assert metadata["side_effect_class"] == "none"
        assert "raw_client_payload" in metadata["forbidden_context_types"]
        assert "real_matter_data" in metadata["forbidden_context_types"]
        assert metadata["required_human_gate"]
        assert metadata["revocation_path"]


def test_proposal_boundary_controls_keep_skills_unapproved_and_local() -> None:
    proposal = _proposal_payload()
    controls = proposal["boundary_controls"]

    assert controls["draft_candidate_only"] is True
    assert controls["human_review_required"] is True
    assert controls["may_execute_scripts"] is False
    assert controls["may_install_without_approval"] is False
    assert controls["may_define_canonical_taxonomy"] is False
    assert controls["may_mutate_semantic_substrate"] is False
    assert controls["may_authorize_external_writes"] is False
    assert controls["may_ingest_real_data"] is False
    assert controls["may_approve_budget_or_matter_opening"] is False


def test_draft_indexes_include_intake_specialists() -> None:
    draft_index = json.loads(
        (ROOT / "registry" / "proposed-draft-skill-index.json").read_text(
            encoding="utf-8"
        )
    )
    local_registry = json.loads(
        (ROOT / "registry" / "skill-agent-local-registry.json").read_text(
            encoding="utf-8"
        )
    )
    declared = {entry["skill_id"]: entry for entry in draft_index["skills"]}
    metadata_files = set(local_registry["metadata_files"])

    for skill_id in EXPECTED_SKILLS:
        assert (
            declared[skill_id]["proposal_pack"]
            == "intake_vertical_specialists_candidate"
        )
        assert f"skills/draft/{skill_id}/SKILL_METADATA.json" in metadata_files


def test_validator_rejects_removed_unknown_context_boundary(tmp_path: Path) -> None:
    data = _proposal_payload()
    data["boundary_controls"]["may_execute_scripts"] = True
    bad = tmp_path / "bad_proposal.json"
    bad.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(IntakeSpecialistSkillReviewError, match="may_execute_scripts"):
        validate_intake_specialist_skill_review(bad)
