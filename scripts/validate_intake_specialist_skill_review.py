#!/usr/bin/env python3
"""Validate candidate intake specialist skill review surfaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
PROPOSAL = ROOT / "registry" / "proposed-intake-specialist-skills.json"
DRAFT_INDEX = ROOT / "registry" / "proposed-draft-skill-index.json"
LOCAL_REGISTRY = ROOT / "registry" / "skill-agent-local-registry.json"
EXPECTED_SKILL_IDS = {
    "intake-source-grounding-review",
    "labor-employment-party-role-mapper",
    "intake-budget-driver-context-review",
    "carrier-rejection-learning-loop-review",
}
REQUIRED_METADATA_KEYS = {
    "accepted_context_types",
    "forbidden_context_types",
    "evidence_requirements",
    "provenance_behavior",
    "allowed_autonomy_level",
    "required_human_gate",
    "data_scope",
    "revocation_path",
    "trust_status",
}
REQUIRED_FORBIDDEN_CONTEXT = {
    "raw_client_payload",
    "real_matter_data",
    "hidden_chain_of_thought",
}
REQUIRED_BOUNDARY_FALSE = {
    "may_execute_scripts",
    "may_install_without_approval",
    "may_define_canonical_taxonomy",
    "may_mutate_semantic_substrate",
    "may_authorize_external_writes",
    "may_ingest_real_data",
    "may_approve_budget_or_matter_opening",
}


class IntakeSpecialistSkillReviewError(ValueError):
    """Raised when candidate intake specialist skill surfaces are invalid."""


def _rel(path: Path) -> str:
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(path)} unreadable: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise IntakeSpecialistSkillReviewError(f"{_rel(path)} must be a JSON object")
    return data


def _require_string_list(data: dict[str, Any], key: str, label: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise IntakeSpecialistSkillReviewError(
            f"{label}.{key} must be a non-empty list"
        )
    if not all(isinstance(item, str) and item.strip() for item in value):
        raise IntakeSpecialistSkillReviewError(
            f"{label}.{key} must contain only non-empty strings"
        )
    return value


def _validate_proposal(data: dict[str, Any], label: str) -> None:
    if data.get("status") != "draft_candidate_only":
        raise IntakeSpecialistSkillReviewError(
            f"{label}.status must be draft_candidate_only"
        )
    for key in (
        "contains_real_firm_data",
        "canonical_authority_allowed",
        "approval_performed",
        "external_writes_authorized",
    ):
        if data.get(key) is not False:
            raise IntakeSpecialistSkillReviewError(f"{label}.{key} must be false")
    controls = data.get("boundary_controls")
    if not isinstance(controls, dict):
        raise IntakeSpecialistSkillReviewError(
            f"{label}.boundary_controls must be an object"
        )
    if controls.get("draft_candidate_only") is not True:
        raise IntakeSpecialistSkillReviewError(
            f"{label}.boundary_controls.draft_candidate_only must be true"
        )
    if controls.get("human_review_required") is not True:
        raise IntakeSpecialistSkillReviewError(
            f"{label}.boundary_controls.human_review_required must be true"
        )
    for key in REQUIRED_BOUNDARY_FALSE:
        if controls.get(key) is not False:
            raise IntakeSpecialistSkillReviewError(
                f"{label}.boundary_controls.{key} must be false"
            )
    skills = data.get("skills")
    if not isinstance(skills, list):
        raise IntakeSpecialistSkillReviewError(f"{label}.skills must be a list")
    observed = {
        str(skill.get("skill_id")) for skill in skills if isinstance(skill, dict)
    }
    if observed != EXPECTED_SKILL_IDS:
        raise IntakeSpecialistSkillReviewError(
            f"{label}.skills must be {sorted(EXPECTED_SKILL_IDS)}"
        )
    for skill in skills:
        if skill.get("requires_human_review") is not True:
            raise IntakeSpecialistSkillReviewError(
                f"{label}.{skill.get('skill_id')}.requires_human_review must be true"
            )
        if skill.get("may_execute_scripts") is not False:
            raise IntakeSpecialistSkillReviewError(
                f"{label}.{skill.get('skill_id')}.may_execute_scripts must be false"
            )


def _validate_skill_folder(skill_id: str) -> None:
    folder = ROOT / "skills" / "draft" / skill_id
    skill_md = folder / "SKILL.md"
    metadata_path = folder / "SKILL_METADATA.json"
    if not skill_md.exists():
        raise IntakeSpecialistSkillReviewError(f"{_rel(skill_md)} missing")
    if not metadata_path.exists():
        raise IntakeSpecialistSkillReviewError(f"{_rel(metadata_path)} missing")
    if (folder / "scripts").exists():
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(folder)} must not contain scripts/"
        )

    metadata = _read_json(metadata_path)
    if metadata.get("id") != skill_id:
        raise IntakeSpecialistSkillReviewError(f"{_rel(metadata_path)} id mismatch")
    if metadata.get("lifecycle_state") != "draft":
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} lifecycle_state must be draft"
        )
    if metadata.get("approval_required") is not False:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} approval_required must be false for unapproved draft metadata"
        )
    if metadata.get("side_effect_class") != "none":
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} side_effect_class must be none"
        )
    missing = sorted(REQUIRED_METADATA_KEYS - set(metadata))
    if missing:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} missing keys: {missing}"
        )
    forbidden = set(
        _require_string_list(metadata, "forbidden_context_types", _rel(metadata_path))
    )
    missing_forbidden = sorted(REQUIRED_FORBIDDEN_CONTEXT - forbidden)
    if missing_forbidden:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} forbidden_context_types missing {missing_forbidden}"
        )
    if metadata.get("allowed_autonomy_level") not in {
        "review_candidate_only",
        "candidate_generation_only",
        "candidate_review_only",
    }:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} allowed_autonomy_level must stay candidate-only"
        )
    if metadata.get("trust_status") != "draft_candidate_unapproved":
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(metadata_path)} trust_status must be draft_candidate_unapproved"
        )
    text = skill_md.read_text(encoding="utf-8")
    for phrase in (
        "not_canonical_truth",
        "Do not",
        "Output Contract",
        "Hard Rules",
    ):
        if phrase not in text:
            raise IntakeSpecialistSkillReviewError(
                f"{_rel(skill_md)} missing phrase {phrase!r}"
            )


def _validate_indexes() -> None:
    draft_index = _read_json(DRAFT_INDEX)
    local_registry = _read_json(LOCAL_REGISTRY)
    declared = {
        str(entry.get("skill_id")): entry
        for entry in draft_index.get("skills", [])
        if isinstance(entry, dict)
    }
    missing = sorted(EXPECTED_SKILL_IDS - set(declared))
    if missing:
        raise IntakeSpecialistSkillReviewError(
            f"{_rel(DRAFT_INDEX)} missing skill ids: {missing}"
        )
    for skill_id in EXPECTED_SKILL_IDS:
        if (
            declared[skill_id].get("proposal_pack")
            != "intake_vertical_specialists_candidate"
        ):
            raise IntakeSpecialistSkillReviewError(
                f"{_rel(DRAFT_INDEX)} {skill_id} proposal_pack must be intake_vertical_specialists_candidate"
            )
    metadata_files = set(
        _require_string_list(local_registry, "metadata_files", _rel(LOCAL_REGISTRY))
    )
    for skill_id in EXPECTED_SKILL_IDS:
        expected = f"skills/draft/{skill_id}/SKILL_METADATA.json"
        if expected not in metadata_files:
            raise IntakeSpecialistSkillReviewError(
                f"{_rel(LOCAL_REGISTRY)} missing metadata file {expected}"
            )


def validate_intake_specialist_skill_review(path: Path = PROPOSAL) -> dict[str, Any]:
    proposal = _read_json(path)
    _validate_proposal(proposal, _rel(path))
    for skill_id in sorted(EXPECTED_SKILL_IDS):
        _validate_skill_folder(skill_id)
    _validate_indexes()
    return proposal


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", type=Path, default=PROPOSAL)
    args = parser.parse_args(argv)

    try:
        validate_intake_specialist_skill_review(args.proposal)
    except IntakeSpecialistSkillReviewError as exc:
        print(
            f"Intake specialist skill review validation failed: {exc}", file=sys.stderr
        )
        return 1
    print("Intake specialist skill review validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
