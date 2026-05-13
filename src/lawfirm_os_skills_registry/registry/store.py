from __future__ import annotations
from pathlib import Path
import json, shutil
from ..skill_format import load_skill
from ..util.files import ensure_dir, read_json, write_json
from ..util.time import utc_now

def approve_skill(skill_dir, evaluation_report, approved_dir='skills/approved', registry_path='registry/approved-skills.json', approve=False):
    if not approve: raise PermissionError('approve-skill requires explicit --approve')
    evaluation=json.loads(Path(evaluation_report).read_text(encoding='utf-8'))
    if not evaluation.get('passed'):
        raise ValueError('Evaluation report did not pass')
    security = evaluation.get('security', {})
    if security.get('risk_score', 100) >= 50:
        raise ValueError('Security risk too high')
    if security.get('recommendation') != 'safe_for_eval':
        raise ValueError('Security scanner did not mark skill safe_for_eval')
    semantic_level = security.get('semantic_risk_level') or security.get('semantic_intent', {}).get('risk_level')
    if semantic_level in {'medium', 'high', 'critical'}:
        raise ValueError(f'Semantic malicious-intent risk requires security review: {semantic_level}')
    skill_dir=Path(skill_dir); doc=load_skill(skill_dir); skill_id=doc.name or skill_dir.name
    target=Path(approved_dir)/skill_id
    if target.exists(): raise FileExistsError(target)
    ensure_dir(target.parent); shutil.move(str(skill_dir), str(target))
    registry=read_json(registry_path, default={'schema_version':'1.0','skills':[]})
    entry={'skill_id':skill_id,'version':'0.1.0','status':'approved_local','approved_at':utc_now(),'source_path':str(target),'description':doc.description,'may_execute_scripts':(target/'scripts').exists(),'requires_human_review':True,'evaluation_report':str(evaluation_report),'scores':evaluation.get('scores', {})}
    registry['skills']=[e for e in registry.get('skills', []) if e.get('skill_id') != skill_id]+[entry]
    write_json(registry_path, registry); return entry

def list_approved(registry_path='registry/approved-skills.json'):
    return read_json(registry_path, default={'schema_version':'1.0','skills':[]})

def install_codex_skills(registry_path, target_repo, include_scripts=False, approve_scripts=False):
    registry=list_approved(registry_path); target_root=Path(target_repo)/'.agents'/'skills'; ensure_dir(target_root); installed=[]
    for entry in registry.get('skills', []):
        src=Path(entry['source_path'])
        if not src.exists(): continue
        dst=target_root/entry['skill_id']
        if dst.exists(): shutil.rmtree(dst)
        ignore=None
        if (src/'scripts').exists() and not (include_scripts and approve_scripts): ignore=shutil.ignore_patterns('scripts')
        shutil.copytree(src, dst, ignore=ignore)
        installed.append({'skill_id':entry['skill_id'],'target':str(dst),'scripts_copied':bool(include_scripts and approve_scripts)})
    return {'installed_count':len(installed),'target_root':str(target_root),'installed':installed}
