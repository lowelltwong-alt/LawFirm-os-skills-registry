---
name: legal-retrieval-planner
description: Use when choosing retrieval primitives for a legal task. Produces a retrieval plan that selects metadata, lexical, document-tree, vector, graph, or compiled-bundle retrieval according to the Legal Context Bundle contract.
metadata:
  version: "0.1.0"
  risk_tier: medium
  status: draft_candidate
---

# Legal Retrieval Planner

## Purpose

Choose retrieval primitives because they deliver the required bundle, not because a database is fashionable.

## Required sequence

1. define task.
2. select bundle type.
3. identify required fields.
4. choose primitives.
5. apply filters.
6. declare missing sources.
7. emit retrieval plan.


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
