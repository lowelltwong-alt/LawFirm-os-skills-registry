from __future__ import annotations
from pathlib import Path
import re
from ..util.files import append_jsonl, read_jsonl
from ..util.time import utc_now
PATTERNS=[
 (re.compile(r'evidence|provenance|source ref|citation|missing.*source', re.I),'evidence-packet-builder','new_skill'),
 (re.compile(r'route|event.?class|classification|wrong enum|canonical', re.I),'exception-classification','new_skill'),
 (re.compile(r'prompt injection|malicious|backdoor|secret|exfiltrat|supply chain', re.I),'malicious-skill-review','new_skill'),
 (re.compile(r'codex|cursor|patch|pull request|repo|test fail', re.I),'repo-safe-patch-planner','new_skill'),
 (re.compile(r'workflow|intake|handoff|process map|bottleneck', re.I),'workflow-intake-mapper','new_skill'),
 (re.compile(r'rfp|requirements|proposal|questionnaire', re.I),'rfp-requirements-extractor','new_skill'),
 (re.compile(r'research|synthesis|summary too broad|action brief', re.I),'research-to-action-brief','new_skill'),
 (re.compile(r'overbuilt|too complex|too many steps|automation.*premature', re.I),'elegant-design-review','new_skill'),
]
def _text(c):
    parts=[]
    for k in ('defect_class','summary','observed_pattern','description','affected_workflows'):
        v=c.get(k)
        if isinstance(v,list): parts.extend(map(str,v))
        elif v is not None: parts.append(str(v))
    return '\n'.join(parts)

def detect_skill_gaps(clusters_path, min_support=3):
    rows=[]
    for c in read_jsonl(clusters_path):
        support=int(c.get('support_count') or c.get('count') or len(c.get('example_failures', [])) or 1)
        if support < min_support: continue
        text=_text(c); skill='general-process-stabilizer'; typ='new_skill'
        for pat,s,t in PATTERNS:
            if pat.search(text): skill=s; typ=t; break
        rows.append({'schema_version':'1.0','record_type':'skill_gap_candidate','candidate_only':True,'requires_human_approval':True,'created_at':utc_now(),'gap_id':c.get('cluster_id') or c.get('defect_cluster_id') or f'gap_{len(rows)+1:04d}','source':'exception_cluster_jsonl','observed_pattern':c.get('observed_pattern') or c.get('summary') or text[:300],'affected_workflows':c.get('affected_workflows', []),'recommended_skill_id':skill,'skill_need_type':typ,'support_count':support,'severity':c.get('severity','medium'),'why_existing_skills_are_insufficient':c.get('why_existing_skills_are_insufficient','No approved skill has been linked to this repeated defect pattern.')})
    return rows

def write_skill_gaps(candidates, out):
    p=Path(out)
    if p.exists(): p.unlink()
    for c in candidates: append_jsonl(p,c)
