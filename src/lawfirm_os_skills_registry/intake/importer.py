from __future__ import annotations
from pathlib import Path
import re
from ..security.scanner import scan_skill
from ..skill_format import load_skill
from ..util.files import ensure_dir, file_manifest, safe_copytree, write_json
from ..util.time import utc_now

def slugify(v):
    v=v.lower().strip(); v=re.sub(r'[^a-z0-9-]+','-',v); v=re.sub(r'-+','-',v).strip('-'); return v or 'unnamed-skill'

def import_skill(source: str | Path, quarantine_dir: str | Path='quarantine'):
    source=Path(source)
    if not (source/'SKILL.md').exists(): raise FileNotFoundError(f'No SKILL.md in {source}')
    doc=load_skill(source); skill_id=slugify(doc.name or source.name)
    target=Path(quarantine_dir)/skill_id
    if target.exists(): target=Path(quarantine_dir)/f"{skill_id}-{utc_now().replace(':','').replace('-','')}"
    ensure_dir(target.parent); safe_copytree(source, target)
    meta={'schema_version':'1.0','imported_at':utc_now(),'source_path':str(source),'target_path':str(target),'skill_id':skill_id,'skill_name':doc.name,'description':doc.description,'status':'quarantined'}
    write_json(target/'_intake.json', meta); write_json(target/'_file_manifest.json', file_manifest(target))
    sec=scan_skill(target); write_json(target/'_security_scan.json', sec)
    return {**meta, 'security_recommendation':sec['recommendation'], 'risk_score':sec['risk_score']}
