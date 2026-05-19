from __future__ import annotations

import uuid
from typing import Any

from ..domain.trust_surface import TRUST_SURFACE_FIELDS
from ..util.time import utc_now


def diff_trust_surfaces(
    prior: dict[str, Any],
    current: dict[str, Any],
    *,
    skill_id: str,
) -> dict[str, Any]:
    """Compare trust surfaces; any material change requires human approval."""
    fields = TRUST_SURFACE_FIELDS
    changes: dict[str, dict[str, list[str]]] = {}
    approval_required = False
    for field in fields:
        before = list(prior.get(field) or []) if isinstance(prior.get(field) or [], list) else prior.get(field)
        after = list(current.get(field) or []) if isinstance(current.get(field) or [], list) else current.get(field)
        if before != after:
            approval_required = True
            if not isinstance(before, list) or not isinstance(after, list):
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
