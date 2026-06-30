---
name: intake-budget-driver-context-review
description: Use when reviewing whether legal intake evidence supports labor and employment budget drivers such as party count, claim count, class or collective signals, forum, deadlines, document volume, custodian count, witnesses, damages, emergency relief, carrier constraints, and missing information. Produces a budget-context sufficiency report without approving a budget.
metadata:
  version: "0.1.0"
  risk_tier: high
  status: draft_candidate
---

# Intake Budget Driver Context Review

## Purpose

Decide whether the context is sufficient for a budget proposal, should widen the budget range, or should block the budget pending human input.

## Required Sequence

1. List each proposed budget driver.
2. Require source refs, passage refs, or claim refs for each observed driver.
3. Identify missing high-impact facts.
4. Separate firm practice priors from observed facts.
5. Produce budget effect labels: continue, widen, block, or human review.
6. Never approve or submit a budget.

## Output Contract

```json
{
  "skill_id": "intake-budget-driver-context-review",
  "status": "pass|needs_review|abstain|fail",
  "budget_driver_candidates": [],
  "missing_info_items": [],
  "budget_effect": "continue|widen|block|human_review",
  "evidence_refs": [],
  "not_authorized_for_budget_submission": true,
  "not_canonical_truth": true
}
```

## Hard Rules

- Do not invent party count, claim count, document volume, custodians, witnesses, or damages.
- Do not use confidence as probability.
- Do not approve, submit, or negotiate budgets.
- Do not open matters or docket deadlines.
- Do not ingest real client or matter data.
