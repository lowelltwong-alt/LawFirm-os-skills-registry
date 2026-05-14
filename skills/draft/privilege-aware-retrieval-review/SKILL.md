---
name: privilege-aware-retrieval-review
description: Use when reviewing a retrieval workflow for cross-matter leakage, privilege risk, confidentiality boundary failures, access-policy gaps, retention issues, or forbidden raw payload movement. Produces a boundary finding report and fail-closed recommendation.
metadata:
  version: "0.1.0"
  risk_tier: critical
  status: draft_candidate
---

# Privilege Aware Retrieval Review

## Purpose

Protect privilege, confidentiality, and matter boundaries during retrieval.

## Required sequence

1. check matter scope.
2. check privilege labels.
3. check confidentiality labels.
4. check access policy.
5. check claim-check refs.
6. check raw payload movement.
7. escalate unresolved risk.


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
