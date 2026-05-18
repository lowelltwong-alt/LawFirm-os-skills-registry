from __future__ import annotations

import uuid
from typing import Any

from ..util.time import utc_now


def diff_trust_surfaces(
    prior: dict[str, Any],
    current: dict[str, Any],
    *,
    skill_id: str,
) -> dict[str, Any]:
    """Compare trust surfaces; any material change requires human approval."""
    fields = ("declared_tools", "declared_hooks", "declared_write_paths", "declared_urls", "declared_purpose_hash")
    changes: dict[str, dict[str, list[str]]] = {}
    approval_required = False
    for field in fields:
        before = list(prior.get(field) or []) if field != "declared_purpose_hash" else prior.get(field)
        after = list(current.get(field) or []) if field != "declared_purpose_hash" else current.get(field)
        if before != after:
            approval_required = True
            if field == "declared_purpose_hash":
                changes[field] = {"before": [str(before)], "after": [str(after)]}
            else:
                changes[field] = {
                    "added": sorted(set(after) - set(before)),
                    "removed": sorted(set(before) - set(after)),
                }
    return {
        "schema_version": "skill_trust_surface_diff.v1",
        "trust_surface_diff_record_id": f"tsd-{uuid.uuid4().hex[:16]}",
        "skill_id": skill_id,
        "approval_required": approval_required,
        "changes": changes,
        "generated_at": utc_now(),
    }
