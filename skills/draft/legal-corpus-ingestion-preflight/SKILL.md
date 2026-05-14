---
name: legal-corpus-ingestion-preflight
description: Use when validating a legal document ingestion manifest before any legal corpus is parsed, indexed, searched, or connected to a runtime. Produces a manifest risk report, missing metadata list, access/privilege gate result, and ingestion recommendation.
metadata:
  version: "0.1.0"
  risk_tier: high
  status: draft_candidate
---

# Legal Corpus Ingestion Preflight

## Purpose

Prevent unsafe or under-specified legal document ingestion.

## Required sequence

1. confirm synthetic or approved data path.
2. verify access policy.
3. verify privilege label.
4. verify retention class.
5. verify parser profile.
6. verify permitted indexes.
7. abstain on any real-data uncertainty.


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
