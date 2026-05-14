from __future__ import annotations

import json
from pathlib import Path


def test_proposed_draft_skill_index_covers_draft_folders() -> None:
    root = Path(__file__).resolve().parents[1]
    dex = json.loads((root / "registry" / "proposed-draft-skill-index.json").read_text(encoding="utf-8"))
    declared = {e["skill_id"] for e in dex["skills"]}
    disk = {p.name for p in (root / "skills" / "draft").iterdir() if p.is_dir() and not p.name.startswith(".")}
    assert disk == declared
