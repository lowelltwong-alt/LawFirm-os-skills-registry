---
name: carrier-rejection-learning-loop-review
description: Use when reviewing candidate carrier rejection, appeal, financial outcome, and learning-loop evidence for legal budget workflows. Produces source-bound rejection bucket candidates, unknown-pattern markers, appeal result refs, and learning proposals without submitting appeals or mutating Exception Lake canon.
metadata:
  version: "0.1.0"
  risk_tier: high
  status: draft_candidate
---

# Carrier Rejection Learning Loop Review

## Purpose

Classify carrier rejection and appeal-result evidence into candidate learning-loop records while preserving unknown patterns and human authorization gates.

## Required Sequence

1. Read only source-bound rejection or appeal-result refs.
2. Classify known rejection bucket candidates or mark unknown/new pattern.
3. Link rejection to budget, actuals, appeal action, and financial outcome refs when available.
4. Require human authorization refs before appeal submission is considered complete.
5. Produce learning candidates for review, not automatic rule changes.

## Output Contract

```json
{
  "skill_id": "carrier-rejection-learning-loop-review",
  "status": "pass|needs_review|abstain|fail",
  "rejection_bucket_candidates": [],
  "unknown_pattern_candidates": [],
  "appeal_result_refs": [],
  "financial_outcome_refs": [],
  "learning_candidates": [],
  "not_authorized_for_external_write": true,
  "not_canonical_truth": true
}
```

## Hard Rules

- Do not submit appeals.
- Do not write to carrier portals or email.
- Do not approve or submit budgets.
- Do not mutate Exception Lake or Semantic Substrate canon.
- Do not learn silently from corrections or outcomes.
