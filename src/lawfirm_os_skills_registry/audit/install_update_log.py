from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

from ..contracts import load_contract_surface_sha256
from ..util.files import append_jsonl
from ..util.time import utc_now


def emit_install_update_audit_record(
    *,
    skill_id: str,
    skill_version: str,
    operation: str,
    status: str,
    skill_trust_record_id: str | None = None,
    target_path: str | None = None,
    run_id: str | None = None,
) -> dict[str, Any]:
    if operation not in {"install", "update", "approve", "quarantine"}:
        raise ValueError("operation must be install, update, approve, or quarantine")
    record = {
        "schema_version": "skill_install_update_audit.v1",
        "audit_record_id": f"sia-{uuid.uuid4().hex[:16]}",
        "skill_id": skill_id,
        "skill_version": skill_version,
        "operation": operation,
        "status": status,
        "contract_surface_sha256": load_contract_surface_sha256(),
        "created_at": utc_now(),
        "run_id": run_id or f"run-{uuid.uuid4().hex[:12]}",
    }
    if skill_trust_record_id:
        record["skill_trust_record_id"] = skill_trust_record_id
    if target_path:
        record["target_path"] = target_path
    return record


def append_install_update_audit(
    ledger_path: str | Path,
    record: dict[str, Any],
) -> dict[str, Any]:
    append_jsonl(ledger_path, record)
    return record
