from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from ..skill_format import load_skill
from ..util.files import read_json


_URL_RE = re.compile(r"https?://[^\s)>'\"]+", re.IGNORECASE)
_WRITE_PATH_RE = re.compile(r"(?i)(?:write|modify|delete|create)\s+(?:to\s+)?([~/][\w./-]+|\.[\w./-]+)")
_TOOL_RE = re.compile(r"(?i)\b(mcp|tool|bash|shell|curl|wget|fetch)\b")


def _bare_hash(value: Any) -> str:
    if isinstance(value, str):
        encoded = value.encode("utf-8")
    else:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted({v.strip() for v in values if v and str(v).strip()})


def load_skill_metadata(skill_dir: Path) -> dict[str, Any]:
    meta_path = skill_dir / "SKILL_METADATA.json"
    if meta_path.exists():
        data = read_json(meta_path, default={})
        return data if isinstance(data, dict) else {}
    return {}


def extract_trust_surface(skill_dir: str | Path) -> dict[str, Any]:
    """Build declared trust surface from SKILL_METADATA trust_surface block and conservative SKILL.md scan."""
    root = Path(skill_dir)
    metadata = load_skill_metadata(root)
    declared = metadata.get("trust_surface") if isinstance(metadata.get("trust_surface"), dict) else {}

    tools = _sorted_unique([str(x) for x in declared.get("declared_tools", [])])
    hooks = _sorted_unique([str(x) for x in declared.get("declared_hooks", [])])
    write_paths = _sorted_unique([str(x) for x in declared.get("declared_write_paths", [])])
    urls = _sorted_unique([str(x) for x in declared.get("declared_urls", [])])

    try:
        doc = load_skill(root)
        body = (doc.body or "") + "\n" + (doc.description or "")
    except Exception:
        body = ""

    for match in _URL_RE.findall(body):
        urls.append(match.rstrip(".,;"))
    for match in _WRITE_PATH_RE.findall(body):
        write_paths.append(match)
    if _TOOL_RE.search(body):
        tools.append("skill_body_mentions_tools")

    side_effect = str(metadata.get("side_effect_class") or "").lower()
    if side_effect in {"write", "read_write"} and not write_paths:
        write_paths.append("implicit_write_from_side_effect_class")

    purpose_parts = [
        str(metadata.get("id") or root.name),
        str(metadata.get("name") or ""),
        str(metadata.get("notes") or ""),
    ]
    try:
        doc = load_skill(root)
        purpose_parts.append(doc.description or "")
    except Exception:
        pass

    return {
        "declared_tools": _sorted_unique(tools),
        "declared_hooks": _sorted_unique(hooks),
        "declared_write_paths": _sorted_unique(write_paths),
        "declared_urls": _sorted_unique(urls),
        "declared_purpose_hash": _bare_hash("\n".join(purpose_parts)),
    }


def extract_provider_metadata(skill_dir: str | Path) -> dict[str, Any]:
    metadata = load_skill_metadata(Path(skill_dir))
    provider = metadata.get("provider_metadata")
    return dict(provider) if isinstance(provider, dict) else {}


def extract_bundled_legal_references(skill_dir: str | Path) -> list[dict[str, Any]]:
    metadata = load_skill_metadata(Path(skill_dir))
    refs = metadata.get("bundled_legal_references")
    if not isinstance(refs, list):
        return []
    out: list[dict[str, Any]] = []
    for item in refs:
        if isinstance(item, dict):
            out.append(dict(item))
    return out


def extract_evidence_ref_links(skill_dir: str | Path) -> list[dict[str, str]]:
    """Return declared evidence links (SourceRef/PassageRef/ClaimRef ids) — evidence only, not canon."""
    metadata = load_skill_metadata(Path(skill_dir))
    links = metadata.get("evidence_ref_links")
    if not isinstance(links, list):
        return []
    allowed = {"source_ref_id", "passage_ref_id", "claim_ref_id"}
    out: list[dict[str, str]] = []
    for item in links:
        if not isinstance(item, dict):
            continue
        row = {k: str(item[k]) for k in allowed if item.get(k)}
        if row:
            out.append(row)
    return out
