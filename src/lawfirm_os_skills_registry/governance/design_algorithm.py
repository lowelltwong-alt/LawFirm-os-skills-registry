from __future__ import annotations
from pathlib import Path
from typing import Any
import re
from ..skill_format import load_skill
from ..util.files import write_json
from ..util.time import utc_now

POSITIVE = {
    'question_requirements': [r'(?i)question.*requirement', r'(?i)owner.*requirement', r'(?i)why.*required', r'(?i)assumption'],
    'delete_before_optimize': [r'(?i)delete|remove|eliminate|defer|not build|do not build|do not do', r'(?i)unnecessary|nonessential|scope creep'],
    'simplify_optimize': [r'(?i)simplif|optimi[sz]e|lean|minimal|small|single responsibility|bounded'],
    'accelerate': [r'(?i)cycle time|latency|throughput|fast|reduce steps|reduce token|shorten review'],
    'automate_last': [r'(?i)automate last|do not automate|human approval|manual review|approval required'],
    'invariants': [r'(?i)invariant|must always|fail.closed|abstain|idempotent|contract pin'],
    'deterministic': [r'(?i)deterministic|validator|schema|enum|allowlist|structured output'],
    'evidence': [r'(?i)evidence|source ref|provenance|hash|trace|ledger'],
    'composability': [r'(?i)output contract|json|fields|handoff|downstream|artifact'],
}
NEGATIVE = [
    (r'(?i)automate.*everything|fully autonomous|no human review|skip approval', 'automation_before_control'),
    (r'(?i)invent.*(route|event_class|schema|policy)|create canonical', 'semantic_overreach'),
    (r'(?i)keep trying|repeat until|loop until|unbounded', 'unbounded_loop'),
    (r'(?i)use all tools|any tool|all available context|dump transcript', 'excessive_scope'),
]

def _hits(patterns, text):
    return sum(1 for p in patterns if re.search(p, text))

def _stage_score(stage: str, text: str) -> int:
    patterns=POSITIVE[stage]
    return min(100, _hits(patterns, text)*100)

def grade_algorithm_text(text: str) -> dict[str, Any]:
    stages={k:_stage_score(k, text) for k in POSITIVE}
    penalties=[]
    for pat, label in NEGATIVE:
        if re.search(pat, text): penalties.append(label)
    core = round(sum(stages.values()) / len(stages), 2)
    penalty = min(60, len(penalties)*20)
    overall = max(0, round(core - penalty, 2))
    if overall >= 80 and not penalties: recommendation='excellent'
    elif overall >= 65 and len(penalties) <= 1: recommendation='approve_for_review'
    elif overall >= 50: recommendation='revise'
    else: recommendation='rewrite_or_reject'
    return {'scores': {'overall': overall, **stages}, 'penalties': penalties, 'recommendation': recommendation}

def grade_skill_algorithm(skill_dir: str | Path) -> dict[str, Any]:
    doc=load_skill(skill_dir)
    text=(doc.description or '') + '\n' + doc.body
    result=grade_algorithm_text(text)
    result.update({'schema_version':'1.0','generated_at':utc_now(),'skill_dir':str(skill_dir),'skill_name':doc.name})
    return result

def write_algorithm_grade(skill_dir, out):
    report=grade_skill_algorithm(skill_dir); write_json(out, report); return report
