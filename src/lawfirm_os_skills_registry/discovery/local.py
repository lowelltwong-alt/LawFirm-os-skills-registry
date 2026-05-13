from __future__ import annotations
from pathlib import Path
from typing import Any
from ..skill_format import parse_skill_md
from ..util.files import append_jsonl
from ..util.time import utc_now

def discover_local(source: str | Path) -> list[dict[str, Any]]:
    root=Path(source); rows=[]
    for skill_md in sorted(root.rglob('SKILL.md')):
        skill_dir=skill_md.parent
        try:
            doc=parse_skill_md(skill_md); name=doc.name or skill_dir.name; desc=doc.description or ''; err=None
        except Exception as exc:
            name=skill_dir.name; desc=''; err=str(exc)
        rows.append({'schema_version':'1.0','discovered_at':utc_now(),'source_type':'local','source_path':str(skill_dir),'skill_name':name,'description':desc,'has_scripts':(skill_dir/'scripts').exists(),'has_references':(skill_dir/'references').exists(),'has_assets':(skill_dir/'assets').exists(),'status':'discovered','parse_error':err})
    return rows

def write_discovered(rows, out):
    p=Path(out)
    if p.exists(): p.unlink()
    for r in rows: append_jsonl(p,r)
