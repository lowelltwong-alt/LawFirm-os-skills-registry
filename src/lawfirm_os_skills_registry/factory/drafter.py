from __future__ import annotations
from pathlib import Path
import json, re
from ..util.files import ensure_dir, write_json
from ..util.time import utc_now

def slugify(v):
    v=str(v).lower().strip(); v=re.sub(r'[^a-z0-9-]+','-',v); v=re.sub(r'-+','-',v).strip('-'); return v[:64] or 'draft-skill'

def draft_skill_from_gap(gap, drafts_dir='skills/draft'):
    skill_id=slugify(gap.get('recommended_skill_id') or gap.get('gap_id') or 'draft-skill')
    target=Path(drafts_dir)/skill_id
    if target.exists(): raise FileExistsError(target)
    ensure_dir(target/'references'); ensure_dir(target/'tests')
    desc=f"Use when LawFirm OS has repeated defects matching: {gap.get('observed_pattern','skill gap')}. Produces a structured proposal or artifact for human review; never creates canonical truth."
    if len(desc)>1000: desc=desc[:997]+'...'
    skill_md=f"""---
name: {skill_id}
description: {desc}
metadata:
  status: draft
  source: skill_gap_candidate
  generated_at: {utc_now()}
---

# {skill_id}

## Purpose

Address this observed LawFirm OS skill gap:

> {gap.get('observed_pattern', 'No observed pattern provided.')}

## Musk-style design pass

1. Question the requirement: why does this skill need to exist, and who owns the need?
2. Delete: remove any step that does not reduce the repeated defect.
3. Simplify: use registries, schemas, and deterministic validators before model judgment.
4. Accelerate: reduce reviewer reconstruction time.
5. Automate last: automate only stable, low-risk substeps after tests pass.

## Authority boundary

- This skill produces proposals, packets, drafts, or review aids.
- It must not define canonical `route_id`, `event_class`, schema meaning, policy, or approval authority.
- It must not write to the Semantic Substrate, Orchestrator, Exception Lake, GitHub, email, filesystem, or external services.
- It must not execute scripts.

## Inputs

- task description
- available approved registries or allowed IDs
- source references or evidence IDs
- desired output artifact

## Method

1. Restate the task and defect pattern.
2. Separate facts from inference.
3. Use only provided registries, contracts, and source references.
4. If required authority or evidence is missing, abstain and list missing inputs.
5. Produce the requested artifact with `not_canonical_truth: true`.
6. Add a reviewer note.

## Output contract

```json
{{
  "skill_id": "{skill_id}",
  "status": "draft_output",
  "not_canonical_truth": true,
  "inputs_used": [],
  "missing_inputs": [],
  "proposed_artifact": {{}},
  "reviewer_note": ""
}}
```
"""
    (target/'SKILL.md').write_text(skill_md, encoding='utf-8')
    skillcard={'schema_version':'1.0','skill_id':skill_id,'version':'0.1.0','status':'draft','source':'skill_gap_candidate','gap_id':gap.get('gap_id'),'created_at':utc_now(),'may_execute_scripts':False,'may_call_external_tools':False,'may_write_external_systems':False,'requires_human_review':True,'candidate_only':True}
    write_json(target/'skillcard.json', skillcard); write_json(target/'references'/'source_gap.json', gap)
    (target/'tests'/'fixtures.jsonl').write_text(json.dumps({'input':gap,'expected_contains':['not_canonical_truth']})+'\n', encoding='utf-8')
    return {'skill_id':skill_id,'draft_path':str(target),'skillcard':skillcard}

def draft_skill_from_gap_file(gap_file, gap_id=None, drafts_dir='skills/draft'):
    rows=[]
    for line in Path(gap_file).read_text(encoding='utf-8').splitlines():
        if line.strip(): rows.append(json.loads(line))
    if not rows: raise ValueError('No gap candidates found')
    gap=None
    if gap_id:
        gap=next((r for r in rows if r.get('gap_id') == gap_id), None)
    else: gap=rows[0]
    if not gap: raise ValueError(f'No gap candidate matched {gap_id}')
    return draft_skill_from_gap(gap, drafts_dir)
