from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from ..contracts import load_contract_surface_sha256
from ..util.time import utc_now
from .trust_surface import extract_trust_surface, load_skill_metadata


class SkillTrustError(ValueError):
    """Raised when a SkillTrustRecord cannot be emitted or validated."""


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:16]}"


def _map_source_origin(metadata: dict[str, Any], skill_dir: Path) -> str:
    explicit = str(metadata.get("source_origin") or "").strip()
    mapping = {
        "first_party": "first_party",
        "internal": "internal_team",
        "internal_team": "internal_team",
        "vendor": "vendor",
        "open_source": "open_source",
        "synthetic": "synthetic_fixture",
        "synthetic_fixture": "synthetic_fixture",
    }
    if explicit in mapping:
        return mapping[explicit]
    if str(skill_dir).replace("\\", "/").find("/tests/") >= 0:
        return "synthetic_fixture"
    plane = str(metadata.get("owning_plane") or "")
    if plane == "skills_registry":
        return "first_party"
    return "first_party"


def emit_skill_trust_record(
    skill_dir: str | Path,
    *,
    qa_verdict: str,
    approval_required: bool,
    freshness_status: str = "unknown",
    trust_surface_diff_record_id: str | None = None,
    approved_by: str | None = None,
    approved_at: str | None = None,
    contract_surface_sha256: str | None = None,
    skill_trust_record_id: str | None = None,
) -> dict[str, Any]:
    if qa_verdict not in {"passed", "failed", "needs_human_review"}:
        raise SkillTrustError("qa_verdict must be passed, failed, or needs_human_review")
    if freshness_status not in {"fresh", "stale", "unknown"}:
        raise SkillTrustError("freshness_status must be fresh, stale, or unknown")
    root = Path(skill_dir)
    metadata = load_skill_metadata(root)
    skill_id = str(metadata.get("id") or root.name)
    skill_version = str(metadata.get("version") or "0.1.0")
    surface = extract_trust_surface(root)
    uri_hash = metadata.get("source_uri_hash")
    if not uri_hash:
        from ..util.files import sha256_file

        skill_md = root / "SKILL.md"
        uri_hash = sha256_file(skill_md) if skill_md.exists() else "0" * 64
    uri_hash = str(uri_hash).removeprefix("sha256:")
    if len(uri_hash) != 64:
        raise SkillTrustError("source.uri_hash must be 64-hex")

    record: dict[str, Any] = {
        "schema_version": "skill_trust_record.v1",
        "skill_trust_record_id": skill_trust_record_id or new_id("str"),
        "skill_id": skill_id,
        "skill_version": skill_version,
        "source": {
            "origin": _map_source_origin(metadata, root),
            "uri_hash": uri_hash,
        },
        "trust_surface": surface,
        "qa_verdict": qa_verdict,
        "freshness_status": freshness_status,
        "approval_required": approval_required,
        "contract_surface_sha256": contract_surface_sha256 or load_contract_surface_sha256(),
        "generated_at": utc_now(),
    }
    publisher = metadata.get("publisher_id")
    if publisher:
        record["source"]["publisher_id"] = str(publisher)
    if trust_surface_diff_record_id:
        record["trust_surface_diff_record_id"] = trust_surface_diff_record_id
    if approved_by:
        record["approved_by"] = approved_by
        record["approved_at"] = approved_at or utc_now()

    if qa_verdict == "needs_human_review" and not approval_required:
        record["approval_required"] = True
    return record


def validate_skill_trust_record_for_approval(record: dict[str, Any], *, skill_id: str | None = None) -> list[str]:
    failures: list[str] = []
    if record.get("schema_version") != "skill_trust_record.v1":
        failures.append("schema_version must be skill_trust_record.v1")
    if skill_id and record.get("skill_id") != skill_id:
        failures.append("skill_id mismatch")
    verdict = record.get("qa_verdict")
    if verdict not in {"passed", "needs_human_review"}:
        failures.append("qa_verdict must be passed or needs_human_review for approval")
    if verdict == "needs_human_review" and not record.get("approved_by"):
        failures.append("needs_human_review requires approved_by on trust record")
    if record.get("approval_required") and not record.get("approved_by"):
        failures.append("approval_required trust record requires approved_by")
    if record.get("qa_verdict") == "failed":
        failures.append("qa_verdict failed cannot approve")
    return failures
