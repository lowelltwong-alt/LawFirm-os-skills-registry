from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..domain.trust_surface import extract_bundled_legal_references


def _parse_iso(value: str) -> datetime | None:
    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def validate_bundled_legal_freshness(
    skill_dir: str | Path,
    *,
    as_of: str | None = None,
) -> dict[str, Any]:
    """Flag stale bundled legal references; does not mutate substrate or canon."""
    refs = extract_bundled_legal_references(skill_dir)
    now = _parse_iso(as_of) if as_of else datetime.now(timezone.utc)
    stale: list[dict[str, Any]] = []
    for ref in refs:
        label = str(ref.get("ref_label") or ref.get("citation_label") or "unknown")
        last_verified = str(ref.get("last_verified") or "")
        window_days = int(ref.get("freshness_window_days") or 365)
        verified_at = _parse_iso(last_verified)
        if verified_at is None:
            stale.append({"ref_label": label, "reason": "missing_last_verified"})
            continue
        age_days = (now - verified_at.astimezone(timezone.utc)).days
        if age_days > window_days:
            stale.append(
                {
                    "ref_label": label,
                    "reason": "stale",
                    "age_days": age_days,
                    "freshness_window_days": window_days,
                }
            )
    status = "stale" if stale else ("fresh" if refs else "unknown")
    return {
        "freshness_status": status,
        "bundled_reference_count": len(refs),
        "stale_references": stale,
        "external_source_not_canon": True,
    }
