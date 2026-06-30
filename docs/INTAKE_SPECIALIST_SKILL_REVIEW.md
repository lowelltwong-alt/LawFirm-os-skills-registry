# Intake Specialist Skill Review

Status: draft candidate only. This document does not approve skills, install skills, promote lifecycle state, create canonical taxonomies, or authorize production automation.

## Purpose

LawFirm-os-intake needs reusable specialist skill candidates for the first labor and employment budget vertical. The skills in this proposal keep the work decomposed around different input contracts and review standards:

- `intake-source-grounding-review`: source inventory, passage refs, claim refs, hashes, attachments, prompt injection, and missing evidence;
- `labor-employment-party-role-mapper`: people, organizations, employers, employees, insurers, agencies, unions, adverse parties, witnesses, and relationship ambiguity;
- `intake-budget-driver-context-review`: source-bound budget drivers, missing high-impact facts, budget widening, and budget blockers;
- `carrier-rejection-learning-loop-review`: carrier rejections, appeals, financial outcomes, unknown patterns, and candidate learning loops.

## Why Separate Skills

These are separate because their review standards differ:

- source grounding is about provenance and evidence completeness;
- party-role mapping is about identity, capacity, and relationship ambiguity;
- budget-driver review is about sufficiency for budget math or missing-info blockers;
- carrier rejection review is about future outcomes and learning-loop evidence.

The decomposition follows the repo rule: add a specialist only when the input contract, output contract, data access boundary, or failure containment changes materially.

## Boundaries

- no approved skills in this slice;
- no installation into Codex/Cursor;
- no scripts inside the draft skill folders;
- no third-party skill execution;
- no real client or matter data;
- no Semantic Substrate writes;
- no canonical role, matter, budget, rejection, or lifecycle taxonomy;
- no carrier portal, email, billing, court, or external write authority;
- no budget approval, appeal submission, matter opening, or conflict conclusion.

## Validation

```bash
python scripts/validate_intake_specialist_skill_review.py
python scripts/run_full_pytest.py tests/test_intake_specialist_skill_review.py -q
python scripts/run_full_pytest.py
```
