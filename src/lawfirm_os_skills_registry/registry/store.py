from __future__ import annotations

import json
import shutil
from pathlib import Path

from ..audit.install_update_log import append_install_update_audit, emit_install_update_audit_record
from ..domain.skill_trust_record import SkillTrustError, validate_skill_trust_record_for_approval
from ..qa.trust_surface_diff import diff_trust_surfaces
from ..skill_format import load_skill
from ..util.files import ensure_dir, read_json, write_json
from ..util.time import utc_now


def approve_skill(
    skill_dir,
    evaluation_report,
    approved_dir="skills/approved",
    registry_path="registry/approved-skills.json",
    approve=False,
    *,
    trust_record_path: str | Path | None = None,
    prior_trust_record_path: str | Path | None = None,
    first_approval: bool = False,
    approval_record_path: str | Path | None = None,
    audit_ledger_path: str | Path = "registry/skill_install_update_audit.jsonl",
):
    if not approve:
        raise PermissionError("approve-skill requires explicit --approve")
    if not trust_record_path:
        raise SkillTrustError("SkillTrustRecord path is required for approval")

    evaluation = json.loads(Path(evaluation_report).read_text(encoding="utf-8"))
    if not evaluation.get("passed"):
        raise ValueError("Evaluation report did not pass")
    security = evaluation.get("security", {})
    if security.get("risk_score", 100) >= 50:
        raise ValueError("Security risk too high")
    if security.get("recommendation") != "safe_for_eval":
        raise ValueError("Security scanner did not mark skill safe_for_eval")
    semantic_level = security.get("semantic_risk_level") or security.get("semantic_intent", {}).get("risk_level")
    if semantic_level in {"medium", "high", "critical"}:
        raise ValueError(f"Semantic malicious-intent risk requires security review: {semantic_level}")

    trust_record = read_json(trust_record_path)
    skill_dir = Path(skill_dir)
    doc = load_skill(skill_dir)
    skill_id = doc.name or skill_dir.name
    approval_record = _load_approval_record(approval_record_path)

    failures = validate_skill_trust_record_for_approval(trust_record, skill_id=skill_id)
    if failures:
        raise SkillTrustError("; ".join(failures))

    registry = read_json(registry_path, default={"schema_version": "1.0", "skills": []})
    prior_entry = next((e for e in registry.get("skills", []) if e.get("skill_id") == skill_id), None)
    if prior_entry and not prior_trust_record_path:
        prior_trust_record_path = prior_entry.get("skill_trust_record_path")
    if prior_entry and not prior_trust_record_path:
        raise SkillTrustError("existing skill approval requires prior_trust_record_path")

    if prior_trust_record_path:
        prior = read_json(prior_trust_record_path)
        surface_diff = diff_trust_surfaces(
            prior.get("trust_surface") or {},
            trust_record.get("trust_surface") or {},
            skill_id=skill_id,
        )
        if surface_diff["approval_required"] and not _approval_record_allows(approval_record):
            raise SkillTrustError("trust surface diff requires separate approved HumanApprovalRecord")
    else:
        if not first_approval:
            raise SkillTrustError("first approval requires explicit first_approval mode")
        if security.get("risk_score", 100) != 0:
            raise SkillTrustError("first approval requires zero security risk score")
        if not _approval_record_allows(approval_record):
            raise SkillTrustError("first approval requires separate approved HumanApprovalRecord")

    target = Path(approved_dir) / skill_id
    if target.exists():
        raise FileExistsError(target)
    ensure_dir(target.parent)
    shutil.move(str(skill_dir), str(target))

    entry = {
        "skill_id": skill_id,
        "version": trust_record.get("skill_version", "0.1.0"),
        "status": "approved_local",
        "approved_at": utc_now(),
        "source_path": str(target),
        "description": doc.description,
        "may_execute_scripts": (target / "scripts").exists(),
        "requires_human_review": True,
        "evaluation_report": str(evaluation_report),
        "skill_trust_record_id": trust_record["skill_trust_record_id"],
        "skill_trust_record_path": str(trust_record_path),
        "approval_record_path": str(approval_record_path) if approval_record_path else None,
        "scores": evaluation.get("scores", {}),
    }
    registry["skills"] = [e for e in registry.get("skills", []) if e.get("skill_id") != skill_id] + [entry]
    write_json(registry_path, registry)

    audit = emit_install_update_audit_record(
        skill_id=skill_id,
        skill_version=str(trust_record.get("skill_version") or "0.1.0"),
        operation="approve",
        status="success",
        skill_trust_record_id=str(trust_record["skill_trust_record_id"]),
        target_path=str(target),
    )
    append_install_update_audit(audit_ledger_path, audit)
    return entry


def _load_approval_record(path: str | Path | None) -> dict | None:
    if not path:
        return None
    record = read_json(path)
    if not isinstance(record, dict):
        raise SkillTrustError("approval_record_path must point to a JSON object")
    return record


def _approval_record_allows(record: dict | None) -> bool:
    if not record:
        return False
    if record.get("schema_version") not in {"1.0", "human_approval_record.v1"}:
        return False
    if record.get("decision") not in {"approved", "approved_with_conditions"}:
        return False
    if not record.get("approval_id"):
        return False
    if not record.get("approver_role"):
        return False
    return True


def list_approved(registry_path="registry/approved-skills.json"):
    return read_json(registry_path, default={"schema_version": "1.0", "skills": []})


def install_codex_skills(registry_path, target_repo, include_scripts=False, approve_scripts=False):
    registry = list_approved(registry_path)
    target_root = Path(target_repo) / ".agents" / "skills"
    ensure_dir(target_root)
    installed = []
    ledger = Path("registry/skill_install_update_audit.jsonl")
    for entry in registry.get("skills", []):
        src = Path(entry["source_path"])
        if not src.exists():
            continue
        dst = target_root / entry["skill_id"]
        if dst.exists():
            shutil.rmtree(dst)
        ignore = None
        if (src / "scripts").exists() and not (include_scripts and approve_scripts):
            ignore = shutil.ignore_patterns("scripts")
        shutil.copytree(src, dst, ignore=ignore)
        installed.append(
            {
                "skill_id": entry["skill_id"],
                "target": str(dst),
                "scripts_copied": bool(include_scripts and approve_scripts),
            }
        )
        audit = emit_install_update_audit_record(
            skill_id=entry["skill_id"],
            skill_version=str(entry.get("version") or "0.1.0"),
            operation="install",
            status="success",
            skill_trust_record_id=str(entry.get("skill_trust_record_id") or ""),
            target_path=str(dst),
        )
        append_install_update_audit(ledger, audit)
    return {"installed_count": len(installed), "target_root": str(target_root), "installed": installed}
