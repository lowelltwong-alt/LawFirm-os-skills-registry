---
name: labor-employment-party-role-mapper
description: Use when intake material needs candidate labor and employment party, entity, role, and relationship mapping for budget planning. Produces source-bound candidate roles, relationship alternatives, unknown states, ambiguity notes, and human-review questions without creating canonical legal taxonomy or conflict conclusions.
metadata:
  version: "0.1.0"
  risk_tier: high
  status: draft_candidate
---

# Labor Employment Party Role Mapper

## Purpose

Identify who appears to be a person, organization, employer, employee, adverse party, insurer, union, agency, witness, or counsel, while preserving ambiguity.

## Required Sequence

1. Read only source-bound context refs.
2. Propose entity candidates and role alternatives.
3. Link each observed fact to passage refs.
4. Keep context priors separate from observed facts.
5. Preserve unknown entity, role, and relationship states.
6. Mark budget-impacting ambiguity for human review.

## Output Contract

```json
{
  "skill_id": "labor-employment-party-role-mapper",
  "status": "pass|needs_review|abstain|fail",
  "entity_candidates": [],
  "role_candidates": [],
  "relationship_candidates": [],
  "unknowns": [],
  "evidence_refs": [],
  "human_review_questions": [],
  "not_canonical_truth": true
}
```

## Hard Rules

- Do not collapse insurer, payer, employer, client, and adverse party roles without evidence.
- Do not treat role guesses as conflict conclusions.
- Do not create canonical party-role taxonomy.
- Do not approve budget, engagement, or matter opening.
- Do not ingest real client or matter data.
