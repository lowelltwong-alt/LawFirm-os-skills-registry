---
name: legal-context-bundle-assembler
description: Use when assembling a Legal Context Bundle for contract review, litigation research, discovery response, billing guideline checks, or matter intake. Produces a bundle with controlling spans, related spans, access decision, missing/uncertain items, and allowed use.
metadata:
  version: "0.1.0"
  risk_tier: high
  status: draft_candidate
---

# Legal Context Bundle Assembler

## Purpose

Give agents the right legal context bundle instead of raw top-k chunks.

## Required sequence

1. load retrieval plan.
2. collect controlling spans.
3. include definitions and schedules.
4. attach access decision.
5. record missing evidence.
6. emit bundle.
7. require human review for finality.


## LawFirm OS invariants

- Semantic Substrate owns canon.
- Legal Knowledge Runtime assembles retrieval evidence and context bundles.
- Orchestrator coordinates execution and approvals.
- Exception Lake stores evidence and candidate signals only.
- Skills produce reusable expertise, not authority.
- Ambiguity must abstain or escalate.

## Output contract

```json
{
  "skill_id": "",
  "risk_tier": "low|medium|high|critical",
  "status": "pass|fail|needs_review|abstain",
  "findings": [],
  "missing_required_context": [],
  "recommended_next_action": "continue|block|human_review|open_candidate_improvement",
  "evidence_refs": [],
  "not_canonical_truth": true
}
```

## Hard rules

- Do not ingest real client or matter data.
- Do not approve production connectors.
- Do not mutate Semantic Substrate schemas, registries, route IDs, event classes, or governance doctrine.
- Do not store full legal document payloads in Exception Lake.
- Do not treat retrieved context as legal advice or final work product.
