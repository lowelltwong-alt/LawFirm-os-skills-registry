from __future__ import annotations
from pathlib import Path
from typing import Any
import re
from ..governance.design_algorithm import grade_skill_algorithm
from ..security.scanner import scan_skill
from ..skill_format import load_skill, validate_skill_name
from ..util.files import write_json
from ..util.time import utc_now

LAWFIRM_KEYWORDS = {'law','legal','contract','litigation','compliance','evidence','citation','audit','matter','client','policy','exception','workflow','document','rfp','billing','intake','governance','approval','risk','repository','github','pull request','codex','cursor'}
OUTPUT_HINTS = {'json','schema','output','return','fields','table','markdown','artifact','packet','report','contract'}
TRIGGER_HINTS = {'use when','when','trigger','asked to','for tasks involving','produces'}
VAGUE = {'helps with','assists with','general','anything','various','misc'}


def _score_trigger(description):
    d=description.lower(); score=0
    if 80 <= len(description) <= 900: score += 35
    elif description: score += 15
    if any(x in d for x in TRIGGER_HINTS): score += 25
    if any(x in d for x in OUTPUT_HINTS): score += 20
    if not any(x in d for x in VAGUE): score += 20
    return min(100, score)

def _score_output_contract(body):
    b=body.lower(); score=0
    if any(x in b for x in OUTPUT_HINTS): score += 25
    if '```json' in b or 'required json' in b or 'json fields' in b or 'output contract' in b: score += 30
    if 'do not' in b or 'must not' in b or 'hard rules' in b or 'authority boundary' in b: score += 15
    if 'edge case' in b or 'if missing' in b or 'abstain' in b: score += 15
    if len(body) > 300: score += 10
    if len(body) < 6000: score += 10
    return min(100, score)

def _score_portability(skill_dir, body):
    score=100
    if (Path(skill_dir)/'scripts').exists(): score -= 25
    if re.search(r'(?i)(/users/|c:\\|~/|api[_-]?key|secret)', body): score -= 25
    if re.search(r'(?i)(claude only|codex only|cursor only)', body): score -= 10
    return max(0, score)

def _score_lawfirm_fit(text):
    t=text.lower(); hits=sum(1 for kw in LAWFIRM_KEYWORDS if kw in t)
    return min(100, hits*10)

def evaluate_skill(skill_dir: str | Path):
    root=Path(skill_dir); errors=[]
    security=scan_skill(root)
    try:
        doc=load_skill(root)
        errors += validate_skill_name(doc.name, root.name if root.name else None)
        if not doc.description: errors.append('missing description')
        description=doc.description or ''; body=doc.body or ''
    except Exception as exc:
        doc=None; description=''; body=''; errors.append(f'parse error: {exc}')
    design=grade_skill_algorithm(root) if not errors else {'scores': {'overall': 0}, 'penalties': ['format_error'], 'recommendation': 'rewrite_or_reject'}
    scores={
        'safety': max(0,100-security['risk_score']),
        'trigger_quality': _score_trigger(description),
        'output_contract': _score_output_contract(body),
        'portability': _score_portability(root, body),
        'lawfirm_fit': _score_lawfirm_fit(description+'\n'+body),
        'algorithmic_elegance': design['scores']['overall'],
    }
    scores['overall'] = round(0.28*scores['safety']+0.17*scores['trigger_quality']+0.18*scores['output_contract']+0.12*scores['portability']+0.12*scores['lawfirm_fit']+0.13*scores['algorithmic_elegance'], 2)
    if errors:
        rec='fix_format'; passed=False
    elif security['recommendation']=='reject':
        rec='reject'; passed=False
    elif security['recommendation']=='quarantine':
        rec='keep_quarantined'; passed=False
    elif security['recommendation']=='manual_review':
        rec='security_manual_review_required'; passed=False
    elif scores['overall'] >= 75 and scores['safety'] >= 80 and scores['algorithmic_elegance'] >= 55:
        rec='approve_for_human_review'; passed=True
    elif scores['overall'] >= 60 and scores['safety'] >= 70:
        rec='revise_then_review'; passed=False
    else:
        rec='reject_or_rewrite'; passed=False
    return {
        'schema_version':'1.1',
        'generated_at':utc_now(),
        'skill_dir':str(root),
        'skill_name':getattr(doc,'name',None),
        'description':description,
        'errors':errors,
        'scores':scores,
        'security': {
            'risk_score':security['risk_score'],
            'risk_level':security.get('risk_level'),
            'static_risk_score':security.get('static_risk_score'),
            'semantic_risk_score':security.get('semantic_risk_score'),
            'semantic_risk_level':security.get('semantic_risk_level'),
            'recommendation':security['recommendation'],
            'finding_count':security['finding_count'],
            'findings':security['findings'],
            'static_findings':security.get('static_findings', []),
            'semantic_intent':security.get('semantic_intent', {}),
        },
        'algorithm_grade': design,
        'passed': passed,
        'recommendation': rec
    }

def write_evaluation(skill_dir, out):
    report=evaluate_skill(skill_dir); write_json(out, report); return report
