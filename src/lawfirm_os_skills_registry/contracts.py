from __future__ import annotations

from pathlib import Path
from typing import Any

from .util.files import read_json


def load_contract_surface_sha256(lock_path: str | Path | None = None) -> str:
    """Load pinned contract surface from contracts.lock.json (synthetic/test default if missing)."""
    path = Path(lock_path or Path("contracts.lock.json"))
    if not path.exists():
        return "0" * 64
    lock = read_json(path, default={})
    surface = (lock.get("contract_surface_lock") or {}).get("surface_sha256")
    if not surface or len(str(surface)) != 64:
        raise ValueError("contracts.lock.json missing contract_surface_lock.surface_sha256")
    return str(surface)


def substrate_schema_path(schema_filename: str, *, workspace: Path | None = None) -> Path:
    root = workspace or Path(__file__).resolve().parents[3]
    substrate = root / "LawFirm-os-semantic-substrate"
    return substrate / "schemas" / schema_filename
