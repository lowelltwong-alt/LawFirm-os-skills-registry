from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from lawfirm_os_skills_registry.audit.install_update_log import append_install_update_audit, emit_install_update_audit_record
from lawfirm_os_skills_registry.domain.skill_trust_record import (
    SkillTrustError,
    emit_skill_trust_record,
    validate_skill_trust_record_for_approval,
)
from lawfirm_os_skills_registry.domain.trust_surface import TRUST_SURFACE_FIELDS, extract_provider_metadata, extract_trust_surface
from lawfirm_os_skills_registry.governance.authority_guard import scan_skill_authority_violations
from lawfirm_os_skills_registry.qa.freshness_validator import validate_bundled_legal_freshness
from lawfirm_os_skills_registry.qa.skill_qa import run_skill_qa, write_skill_qa_report
from lawfirm_os_skills_registry.qa.trust_surface_diff import diff_trust_surfaces
from lawfirm_os_skills_registry.registry.store import approve_skill

ROOT = Path(__file__).resolve().parents[1]
WORKSPACE = ROOT.parent
SUBSTRATE = WORKSPACE / "LawFirm-os-semantic-substrate"
FIXTURES = Path(__file__).parent / "fixtures"


def _schema(name: str) -> dict:
    return json.loads((SUBSTRATE / "schemas" / name).read_text(encoding="utf-8"))


def _write_skill(
    tmp_path: Path,
    skill_id: str,
    *,
    metadata_extra: dict | None = None,
    body: str = "Use when testing. Produces JSON output.\nDo not claim canonical legal truth.",
) -> Path:
    d = tmp_path / skill_id
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(
        f"---\nname: {skill_id}\ndescription: Use when testing trust layer. Produces JSON report.\n---\n{body}",
        encoding="utf-8",
    )
    meta = {
        "id": skill_id,
        "kind": "skill",
        "name": skill_id,
        "version": "0.1.0",
        "lifecycle_state": "draft",
        "source_origin": "synthetic_fixture",
        "source_uri_hash": "b" * 64,
        "trust_surface": {
            "declared_tools": ["read_file"],
            "declared_hooks": [],
            "declared_write_paths": [],
            "declared_urls": [],
        },
        "provider_metadata": {
            "claude_plugin_ref": "claude-plugin-synthetic-fixture",
            "claude_workflow_ref": "wf-synthetic-fixture",
        },
    }
    if metadata_extra:
        meta.update(metadata_extra)
    (d / "SKILL_METADATA.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return d


def _eval_report(tmp_path: Path) -> Path:
    report = tmp_path / "eval.json"
    report.write_text(
        json.dumps(
            {
                "passed": True,
                "security": {"risk_score": 0, "recommendation": "safe_for_eval", "semantic_risk_level": "low"},
                "scores": {"overall": 90},
            }
        ),
        encoding="utf-8",
    )
    return report


def _approval_record(tmp_path: Path, *, decision: str = "approved") -> Path:
    path = tmp_path / f"approval-{decision}.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "approval_id": "appr-test",
                "run_id": "run-test",
                "trace_id": "trace-test",
                "required": True,
                "approver_role": "governance_reviewer",
                "decision": decision,
                "decision_reason": "Synthetic PR-11.5 approval fixture.",
                "created_at": "2026-05-19T00:00:00Z",
            }
        ),
        encoding="utf-8",
    )
    return path


def _trust_record(skill_dir: Path, *, approved_by: str | None = "human-reviewer") -> dict:
    return emit_skill_trust_record(
        skill_dir,
        qa_verdict="passed",
        approval_required=False,
        freshness_status="fresh",
        approved_by=approved_by,
    )


@pytest.fixture
def jsonschema_validate():
    jsonschema = pytest.importorskip("jsonschema")
    from jsonschema import validate

    return validate


def test_new_skill_cannot_approve_without_trust_record(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "no-trust-skill")
    report = _eval_report(tmp_path)
    with pytest.raises(SkillTrustError, match="SkillTrustRecord"):
        approve_skill(
            skill,
            report,
            approved_dir=tmp_path / "approved",
            registry_path=tmp_path / "reg.json",
            approve=True,
        )


def test_trust_surface_diff_requires_human_approval(tmp_path: Path) -> None:
    prior = {
        "declared_tools": ["read_file"],
        "declared_hooks": [],
        "declared_write_paths": [],
        "declared_urls": [],
        "declared_purpose_hash": "a" * 64,
    }
    current = dict(prior)
    current["declared_tools"] = ["read_file", "write_file"]
    diff = diff_trust_surfaces(prior, current, skill_id="demo-skill")
    assert diff["approval_required"] is True
    assert "declared_tools" in diff["changes"]


def test_every_trust_surface_field_is_diffed(tmp_path: Path) -> None:
    prior = {field: [] for field in TRUST_SURFACE_FIELDS}
    prior["declared_purpose_hash"] = "a" * 64
    prior["declared_freshness_window_days"] = 30
    for field in TRUST_SURFACE_FIELDS:
        current = dict(prior)
        if field == "declared_purpose_hash":
            current[field] = "b" * 64
        elif field == "declared_freshness_window_days":
            current[field] = 90
        else:
            current[field] = ["new-value"]
        diff = diff_trust_surfaces(prior, current, skill_id="demo-skill")
        assert diff["approval_required"] is True
        assert field in diff["changes"]


def test_extracted_trust_surface_includes_roadmap_surfaces(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path,
        "roadmap-surface-skill",
        metadata_extra={
            "trust_surface": {
                "declared_tools": ["read_file"],
                "declared_mcp_servers": ["mcp.synthetic"],
                "declared_hooks": ["pre_run"],
                "declared_connectors": ["courtlistener_stub"],
                "declared_env_vars": ["LFOS_MODE"],
                "declared_secret_refs": ["SECRET_TOKEN"],
                "declared_models": ["mock_model"],
                "declared_data_classes": ["synthetic"],
                "declared_write_paths": ["./out"],
                "declared_urls": ["https://example.invalid"],
                "declared_freshness_window_days": 30,
            }
        },
    )
    surface = extract_trust_surface(skill)
    for field in TRUST_SURFACE_FIELDS:
        assert field in surface


def test_stale_bundled_legal_reference_flagged(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path,
        "stale-legal-skill",
        metadata_extra={
            "bundled_legal_references": [
                {
                    "ref_label": "Synthetic Statute 2020",
                    "last_verified": "2020-01-01T00:00:00Z",
                    "freshness_window_days": 30,
                }
            ]
        },
    )
    as_of = datetime(2026, 5, 18, tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    result = validate_bundled_legal_freshness(skill, as_of=as_of)
    assert result["freshness_status"] == "stale"
    assert result["stale_references"]


def test_skill_qa_report_generated(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "qa-skill")
    out = tmp_path / "qa.json"
    report = write_skill_qa_report(skill, out)
    assert out.exists()
    assert report["schema_version"] == "skill_qa_report.v1"
    assert "trust_surface" in report
    assert report["boundary_controls"]["no_live_connector_calls"] is True


def test_install_update_audit_record_emitted(tmp_path: Path) -> None:
    ledger = tmp_path / "audit.jsonl"
    rec = emit_install_update_audit_record(
        skill_id="audit-skill",
        skill_version="0.1.0",
        operation="install",
        status="success",
        skill_trust_record_id="str-test",
        target_path=str(tmp_path / "target"),
    )
    append_install_update_audit(ledger, rec)
    lines = ledger.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row["operation"] == "install"
    assert row["skill_trust_record_id"] == "str-test"


def test_claude_identifiers_remain_provider_metadata(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "claude-meta-skill")
    provider = extract_provider_metadata(skill)
    assert provider["claude_plugin_ref"] == "claude-plugin-synthetic-fixture"
    meta = json.loads((skill / "SKILL_METADATA.json").read_text(encoding="utf-8"))
    assert "route_id" not in meta
    assert "event_class" not in meta


def test_skill_trust_record_matches_substrate_schema(tmp_path: Path, jsonschema_validate) -> None:
    skill = _write_skill(tmp_path, "schema-skill")
    record = _trust_record(skill)
    jsonschema_validate(record, _schema("skill-trust-record.schema.json"))


def test_forbidden_route_id_in_metadata_flagged(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "bad-route-skill", metadata_extra={"route_id": "invented.route"})
    violations = scan_skill_authority_violations(skill)
    assert any(v["kind"] == "forbidden_core_field" for v in violations)


def test_evidence_ref_links_are_refs_not_canon(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path,
        "evidence-ref-skill",
        metadata_extra={
            "evidence_ref_links": [
                {"source_ref_id": "sr-synthetic", "passage_ref_id": "pr-synthetic", "claim_ref_id": "cl-synthetic"}
            ]
        },
    )
    qa = run_skill_qa(skill)
    assert qa["evidence_ref_links"]
    assert qa["boundary_controls"]["external_legal_data_is_evidence_not_canon"] is True


def test_approve_with_valid_trust_record(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "approve-trust-skill")
    report = _eval_report(tmp_path)
    trust_path = tmp_path / "trust.json"
    trust_path.write_text(json.dumps(_trust_record(skill)), encoding="utf-8")
    entry = approve_skill(
        skill,
        report,
        approved_dir=tmp_path / "approved",
        registry_path=tmp_path / "reg.json",
        approve=True,
        trust_record_path=trust_path,
        first_approval=True,
        approval_record_path=_approval_record(tmp_path),
        audit_ledger_path=tmp_path / "audit.jsonl",
    )
    assert entry["skill_trust_record_id"]
    assert (tmp_path / "approved" / "approve-trust-skill").exists()


def test_approval_blocked_when_trust_surface_diff_without_approver(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "diff-block-skill")
    report = _eval_report(tmp_path)
    prior = emit_skill_trust_record(skill, qa_verdict="passed", approval_required=False, freshness_status="unknown")
    trust = emit_skill_trust_record(skill, qa_verdict="passed", approval_required=False, freshness_status="unknown")
    trust["trust_surface"] = dict(trust["trust_surface"])
    trust["trust_surface"]["declared_tools"] = ["read_file", "network_fetch"]
    prior_path = tmp_path / "prior.json"
    trust_path = tmp_path / "trust.json"
    prior_path.write_text(json.dumps(prior), encoding="utf-8")
    trust_path.write_text(json.dumps(trust), encoding="utf-8")
    with pytest.raises(SkillTrustError, match="trust surface diff"):
        approve_skill(
            skill,
            report,
            approved_dir=tmp_path / "approved",
            registry_path=tmp_path / "reg.json",
            approve=True,
            trust_record_path=trust_path,
            prior_trust_record_path=prior_path,
        )


def test_first_approval_requires_explicit_mode_and_approval_record(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "first-approval-skill")
    report = _eval_report(tmp_path)
    trust_path = tmp_path / "trust.json"
    trust_path.write_text(json.dumps(_trust_record(skill, approved_by="self-attested")), encoding="utf-8")
    with pytest.raises(SkillTrustError, match="first approval"):
        approve_skill(
            skill,
            report,
            approved_dir=tmp_path / "approved",
            registry_path=tmp_path / "reg.json",
            approve=True,
            trust_record_path=trust_path,
        )
    with pytest.raises(SkillTrustError, match="HumanApprovalRecord"):
        approve_skill(
            skill,
            report,
            approved_dir=tmp_path / "approved",
            registry_path=tmp_path / "reg.json",
            approve=True,
            trust_record_path=trust_path,
            first_approval=True,
        )


def test_arbitrary_approved_by_in_trust_record_does_not_satisfy_cli_approval(tmp_path: Path) -> None:
    from lawfirm_os_skills_registry.cli import main

    skill = _write_skill(tmp_path, "cli-self-attested-skill")
    report = _eval_report(tmp_path)
    trust_path = tmp_path / "trust.json"
    trust_path.write_text(json.dumps(_trust_record(skill, approved_by="any-string")), encoding="utf-8")
    with pytest.raises(SkillTrustError, match="HumanApprovalRecord"):
        main(
            [
                "approve-skill",
                "--skill",
                str(skill),
                "--evaluation",
                str(report),
                "--trust-record",
                str(trust_path),
                "--approved-dir",
                str(tmp_path / "approved"),
                "--registry",
                str(tmp_path / "reg.json"),
                "--first-approval",
                "--approve",
            ]
        )


def test_update_approval_auto_discovers_prior_trust_record(tmp_path: Path) -> None:
    skill = _write_skill(tmp_path, "update-skill")
    report = _eval_report(tmp_path)
    prior = emit_skill_trust_record(skill, qa_verdict="passed", approval_required=False, freshness_status="fresh")
    trust = emit_skill_trust_record(skill, qa_verdict="passed", approval_required=False, freshness_status="fresh")
    trust["trust_surface"] = dict(trust["trust_surface"])
    trust["trust_surface"]["declared_connectors"] = ["new_stub_connector"]
    prior_path = tmp_path / "prior.json"
    trust_path = tmp_path / "trust.json"
    prior_path.write_text(json.dumps(prior), encoding="utf-8")
    trust_path.write_text(json.dumps(trust), encoding="utf-8")
    registry_path = tmp_path / "reg.json"
    registry_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "skills": [{"skill_id": "update-skill", "skill_trust_record_path": str(prior_path)}],
            }
        ),
        encoding="utf-8",
    )
    entry = approve_skill(
        skill,
        report,
        approved_dir=tmp_path / "approved",
        registry_path=registry_path,
        approve=True,
        trust_record_path=trust_path,
        approval_record_path=_approval_record(tmp_path),
    )
    assert entry["skill_trust_record_id"] == trust["skill_trust_record_id"]


def test_provider_metadata_authority_key_flagged(tmp_path: Path) -> None:
    skill = _write_skill(
        tmp_path,
        "bad-provider-metadata",
        metadata_extra={"provider_metadata": {"route_id": "route.invented"}},
    )
    violations = scan_skill_authority_violations(skill)
    assert any("provider_metadata.route_id" in v["detail"] for v in violations)


def test_validate_skill_trust_record_for_approval_rules() -> None:
    bad = {"schema_version": "skill_trust_record.v1", "qa_verdict": "failed"}
    assert validate_skill_trust_record_for_approval(bad)
