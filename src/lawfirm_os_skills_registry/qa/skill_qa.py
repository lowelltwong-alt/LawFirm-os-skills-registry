from __future__ import annotations

from pathlib import Path
from typing import Any

from ..domain.trust_surface import (
    extract_evidence_ref_links,
    extract_provider_metadata,
    extract_trust_surface,
    load_skill_metadata,
)
from ..evaluation.evaluator import evaluate_skill
from ..governance.authority_guard import scan_skill_authority_violations
from ..util.files import write_json
from ..util.time import utc_now
from .freshness_validator import validate_bundled_legal_freshness


def run_skill_qa(skill_dir: str | Path, *, as_of: str | None = None) -> dict[str, Any]:
    """Generate a Skill QA report (fixtures/synthetic only; no external API calls)."""
    root = Path(skill_dir)
    metadata = load_skill_metadata(root)
    skill_id = str(metadata.get("id") or root.name)
    evaluation = evaluate_skill(root)
    trust_surface = extract_trust_surface(root)
    freshness = validate_bundled_legal_freshness(root, as_of=as_of)
    authority_violations = scan_skill_authority_violations(root)
    provider_metadata = extract_provider_metadata(root)
    evidence_ref_links = extract_evidence_ref_links(root)

    qa_verdict = "passed"
    if authority_violations or freshness["freshness_status"] == "stale":
        qa_verdict = "needs_human_review"
    elif not evaluation.get("passed"):
        qa_verdict = "failed"
    elif evaluation.get("recommendation") not in {"approve_for_human_review"}:
        qa_verdict = "needs_human_review"

    return {
        "schema_version": "skill_qa_report.v1",
        "skill_id": skill_id,
        "skill_version": str(metadata.get("version") or "0.1.0"),
        "generated_at": utc_now(),
        "qa_verdict": qa_verdict,
        "evaluation": evaluation,
        "trust_surface": trust_surface,
        "freshness": freshness,
        "authority_violations": authority_violations,
        "provider_metadata": provider_metadata,
        "evidence_ref_links": evidence_ref_links,
        "boundary_controls": {
            "skill_defines_canonical_legal_meaning": False,
            "external_legal_data_is_evidence_not_canon": True,
            "retrieved_content_treated_as_instruction": False,
            "no_live_connector_calls": True,
        },
    }


def write_skill_qa_report(skill_dir: str | Path, out_path: str | Path, *, as_of: str | None = None) -> dict[str, Any]:
    report = run_skill_qa(skill_dir, as_of=as_of)
    write_json(out_path, report)
    return report
