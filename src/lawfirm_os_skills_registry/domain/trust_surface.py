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
_ENV_RE = re.compile(r"\b[A-Z][A-Z0-9_]{2,}\b")

TRUST_SURFACE_LIST_FIELDS = (
    "declared_tools",
    "declared_mcp_servers",
    "declared_hooks",
    "declared_connectors",
    "declared_env_vars",
    "declared_secret_refs",
    "declared_models",
    "declared_data_classes",
    "declared_write_paths",
    "declared_urls",
)
TRUST_SURFACE_SCALAR_FIELDS = ("declared_purpose_hash", "declared_freshness_window_days")
TRUST_SURFACE_FIELDS = TRUST_SURFACE_LIST_FIELDS + TRUST_SURFACE_SCALAR_FIELDS
_PROVIDER_AUTHORITY_KEYS = frozenset(
    {
        "route_id",
        "event_class",
        "defect_class",
        "admission_reason_code",
        "reason_code",
        "semantic_mutation_action",
        "model_policy",
        "model_policy_id",
        "connector_authority",
        "approval_state",
        "approval_status",
    }
)


def _bare_hash(value: Any) -> str:
    if isinstance(value, str):
        encoded = value.encode("utf-8")
    else:
        encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _sorted_unique(values: list[str]) -> list[str]:
    return sorted({v.strip() for v in values if v and str(v).strip()})


def _declared_list(metadata: dict[str, Any], declared: dict[str, Any], field: str, *aliases: str) -> list[str]:
    values: list[str] = []
    for key in (field, *aliases):
        source = declared.get(key)
        if source is None:
            source = metadata.get(key)
        if isinstance(source, list):
            values.extend(str(item) for item in source)
        elif isinstance(source, str):
            values.append(source)
    return _sorted_unique(values)


def validate_provider_metadata(provider: Any, *, path: str = "provider_metadata") -> list[str]:
    """Validate provider metadata as bounded opaque edge data, never authority."""
    failures: list[str] = []
    if provider in (None, ""):
        return failures
    if not isinstance(provider, dict):
        return [f"{path} must be an object when present"]
    if len(provider) > 16:
        failures.append(f"{path} must not contain more than 16 keys")
    for key, value in provider.items():
        key_text = str(key)
        normalized = key_text.lower()
        if normalized in _PROVIDER_AUTHORITY_KEYS:
            failures.append(f"{path}.{key_text} must not carry authority")
        if isinstance(value, dict):
            failures.append(f"{path}.{key_text} must be scalar opaque metadata, not an object")
            failures.extend(validate_provider_metadata(value, path=f"{path}.{key_text}"))
        elif isinstance(value, list):
            failures.append(f"{path}.{key_text} must be scalar opaque metadata, not an array")
        elif not isinstance(value, (str, int, float, bool, type(None))):
            failures.append(f"{path}.{key_text} must be scalar opaque metadata")
    return failures


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

    tools = _declared_list(metadata, declared, "declared_tools", "tools")
    mcp_servers = _declared_list(metadata, declared, "declared_mcp_servers", "mcp_servers")
    hooks = _declared_list(metadata, declared, "declared_hooks", "hooks")
    connectors = _declared_list(metadata, declared, "declared_connectors", "connectors")
    env_vars = _declared_list(metadata, declared, "declared_env_vars", "env_vars")
    secret_refs = _declared_list(metadata, declared, "declared_secret_refs", "secret_refs")
    models = _declared_list(metadata, declared, "declared_models", "models")
    data_classes = _declared_list(metadata, declared, "declared_data_classes", "data_classes")
    write_paths = _declared_list(metadata, declared, "declared_write_paths", "write_paths")
    urls = _declared_list(metadata, declared, "declared_urls", "external_urls", "urls")

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
    for match in _ENV_RE.findall(body):
        if match.endswith(("_TOKEN", "_KEY", "_SECRET", "_PASSWORD")):
            secret_refs.append(match)

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

    freshness_window = declared.get("declared_freshness_window_days")
    if freshness_window is None:
        freshness_window = declared.get("freshness_window_days")
    if freshness_window is None:
        windows = []
        for ref in extract_bundled_legal_references(root):
            if ref.get("freshness_window_days") is not None:
                windows.append(int(ref["freshness_window_days"]))
        freshness_window = min(windows) if windows else None

    surface = {
        "declared_tools": _sorted_unique(tools),
        "declared_mcp_servers": _sorted_unique(mcp_servers),
        "declared_hooks": _sorted_unique(hooks),
        "declared_connectors": _sorted_unique(connectors),
        "declared_env_vars": _sorted_unique(env_vars),
        "declared_secret_refs": _sorted_unique(secret_refs),
        "declared_models": _sorted_unique(models),
        "declared_data_classes": _sorted_unique(data_classes),
        "declared_write_paths": _sorted_unique(write_paths),
        "declared_urls": _sorted_unique(urls),
        "declared_purpose_hash": _bare_hash("\n".join(purpose_parts)),
    }
    if freshness_window is not None:
        surface["declared_freshness_window_days"] = int(freshness_window)
    return surface


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
