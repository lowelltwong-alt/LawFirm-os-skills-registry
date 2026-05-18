from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from ..domain.trust_surface import load_skill_metadata


_FORBIDDEN_CORE_KEYS = frozenset({"route_id", "event_class", "defect_class", "admission_reason_code"})
_CANON_CLAIM_RE = re.compile(
    r"(?i)\b(canonical\s+legal\s+truth|source\s+of\s+truth|defines?\s+route_id|defines?\s+event_class|"
    r"mutates?\s+(?:the\s+)?semantic\s+substrate|promotes?\s+to\s+canon)\b"
)


def scan_skill_authority_violations(skill_dir: str | Path) -> list[dict[str, str]]:
    """Detect skill metadata/body patterns that claim canonical authority or regulated core fields."""
    root = Path(skill_dir)
    metadata = load_skill_metadata(root)
    violations: list[dict[str, str]] = []

    for key in _FORBIDDEN_CORE_KEYS:
        if key in metadata and metadata[key] not in (None, ""):
            violations.append(
                {
                    "kind": "forbidden_core_field",
                    "detail": f"SKILL_METADATA must not set {key}; use provider_metadata or external refs.",
                }
            )

    provider = metadata.get("provider_metadata")
    if isinstance(provider, dict):
        for bad_key in _FORBIDDEN_CORE_KEYS:
            if bad_key in provider:
                violations.append(
                    {
                        "kind": "provider_metadata_must_not_carry_authority",
                        "detail": f"provider_metadata must not include {bad_key}",
                    }
                )

    skill_md = root / "SKILL.md"
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        if _CANON_CLAIM_RE.search(text):
            violations.append(
                {
                    "kind": "canonical_authority_claim",
                    "detail": "SKILL.md must not claim canonical legal meaning or substrate authority.",
                }
            )
        if re.search(r"(?i)\broute_id\s*[:=]", text) and "provider_metadata" not in text:
            violations.append(
                {
                    "kind": "route_id_in_skill_body",
                    "detail": "route_id must not be authored in skill body as authority.",
                }
            )
        if re.search(r"(?i)\bevent_class\s*[:=]", text) and "provider_metadata" not in text:
            violations.append(
                {
                    "kind": "event_class_in_skill_body",
                    "detail": "event_class must not be authored in skill body as authority.",
                }
            )

    return violations
